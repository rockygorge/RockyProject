import http.client, json, os, tempfile, threading, unittest
from http.server import ThreadingHTTPServer
from app import Database, Metrics, handler_for

class AppTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Database(os.getenv("TEST_DATABASE_URL",
            "sqlite:///" + self.temp.name + "/test.db"))
        self.db.initialize()
        self.metrics = Metrics()
        self.server = ThreadingHTTPServer(("127.0.0.1",0),handler_for(self.db,self.metrics))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.temp.cleanup()

    def request(self, method, path, body=None):
        conn = http.client.HTTPConnection("127.0.0.1",self.server.server_port,timeout=5)
        payload = json.dumps(body) if body is not None else None
        conn.request(method,path,payload,{"Content-Type":"application/json"})
        response = conn.getresponse()
        data = response.read()
        status = response.status
        conn.close()
        return status, json.loads(data)

    def test_create_list_update_and_persistence(self):
        title = "test-" + self.temp.name
        status, task = self.request("POST","/api/tasks",{"title":title})
        self.assertEqual(status,201)
        self.assertEqual(task["status"],"open")
        self.assertTrue(any(t["id"] == task["id"] for t in self.db.list_tasks()))
        status, _ = self.request("PATCH","/api/tasks/"+task["id"],{"status":"done"})
        self.assertEqual(status,200)
        persisted = next(t for t in self.db.list_tasks() if t["id"] == task["id"])
        self.assertEqual(persisted["status"],"done")

    def test_invalid_title_and_status(self):
        for title in ["", " " * 3, "x" * 161, None, 12]:
            self.assertEqual(self.request("POST","/api/tasks",{"title":title})[0],400)
        self.assertEqual(self.request("PATCH","/api/tasks/not-a-uuid",
                                     {"status":"done"})[0],400)
        status, task = self.request("POST","/api/tasks",{"title":"valid"})
        for invalid in ["invalid", [], None]:
            self.assertEqual(self.request("PATCH","/api/tasks/"+task["id"],
                                         {"status":invalid})[0],400)

    def test_sql_payload_stays_data(self):
        title = "'; DROP TABLE tasks; --"
        self.assertEqual(self.request("POST","/api/tasks",{"title":title})[0],201)
        self.db.ready()
        self.assertTrue(any(t["title"] == title for t in self.db.list_tasks()))

    def test_health_and_missing_resource(self):
        self.assertEqual(self.request("GET","/healthz")[0],200)
        self.assertEqual(self.request("GET","/readyz")[0],200)
        self.assertEqual(self.request("GET","/missing")[0],404)
        self.assertEqual(self.request("PATCH",
            "/api/tasks/00000000-0000-0000-0000-000000000000",{"status":"done"})[0],404)

    def test_database_outage_does_not_break_liveness(self):
        def unavailable(): raise RuntimeError("private backend detail")
        self.db.ready = unavailable
        status, body = self.request("GET","/readyz")
        self.assertEqual(status,503)
        self.assertNotIn("private",str(body))
        self.assertEqual(self.request("GET","/healthz")[0],200)

    def test_metrics_count_server_errors(self):
        self.metrics.record(200,0.2)
        self.metrics.record(503,0.3)
        rendered = self.metrics.render().decode()
        self.assertIn("platformops_requests_total 2",rendered)
        self.assertIn("platformops_server_errors_total 1",rendered)

if __name__ == "__main__": unittest.main()
