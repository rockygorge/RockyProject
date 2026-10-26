const list = document.getElementById("tasks");
const status = document.getElementById("connection");
const message = document.getElementById("message");
async function api(path, options = {}) {
  const response = await fetch(path, options);
  const body = await response.json();
  if (!response.ok) throw new Error(body.error || "Request failed");
  return body;
}
async function refresh() {
  try {
    const body = await api("/api/tasks");
    list.replaceChildren();
    for (const task of body.tasks) {
      const row = document.createElement("article");
      const title = document.createElement("span");
      title.textContent = task.title;
      const select = document.createElement("select");
      select.setAttribute("aria-label", "Status for " + task.title);
      for (const value of ["open", "in_progress", "done"]) {
        const option = document.createElement("option");
        option.value = value; option.textContent = value.replace("_", " ");
        option.selected = task.status === value; select.append(option);
      }
      select.addEventListener("change", async () => {
        select.disabled = true;
        try {
          await api("/api/tasks/" + task.id, {method:"PATCH",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify({status:select.value})});
          message.textContent = ""; await refresh();
        } catch (error) { message.textContent = error.message; await refresh(); }
      });
      row.append(title,select); list.append(row);
    }
    if (!body.tasks.length) list.textContent = "No tasks yet. Add your first operational task.";
    status.textContent = "API connected"; status.className = "online";
  } catch (error) {
    status.textContent = "API unavailable"; status.className = "offline";
    message.textContent = error.message;
  }
}
document.getElementById("task-form").addEventListener("submit", async event => {
  event.preventDefault();
  const title = document.getElementById("title");
  try {
    await api("/api/tasks", {method:"POST",headers:{"Content-Type":"application/json"},
      body:JSON.stringify({title:title.value})});
    title.value = ""; message.textContent = ""; await refresh();
  } catch (error) { message.textContent = error.message; }
});
document.getElementById("refresh").addEventListener("click",refresh);
refresh();
