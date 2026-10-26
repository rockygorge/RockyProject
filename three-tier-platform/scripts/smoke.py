"""Exercise the full HTTP path through Nginx and persist a task."""
import json, os, urllib.request, uuid
base = os.getenv("BASE_URL","http://127.0.0.1:8080").rstrip("/")
def call(path, method="GET", data=None):
    body = None if data is None else json.dumps(data).encode()
    request = urllib.request.Request(base+path,data=body,method=method,
        headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(request,timeout=15) as response:
        return json.load(response)
with urllib.request.urlopen(base+"/",timeout=15) as response:
    assert b"PlatformOps Board" in response.read()
task = call("/api/tasks","POST",{"title":"smoke-"+str(uuid.uuid4())})
assert task["status"] == "open"
call("/api/tasks/"+task["id"],"PATCH",{"status":"done"})
assert any(t["id"] == task["id"] and t["status"] == "done"
           for t in call("/api/tasks")["tasks"])
print("PASS: frontend, API create/list/update, and persistence through PostgreSQL path")
