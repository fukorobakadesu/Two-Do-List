"""
two-do — Flask Backend
=======================

Data stores:
  tasks.json    → todo list
  events.json   → calendar events
  shopping.json → shared shopping list

All follow the same REST pattern.
Long-poll endpoint watches ALL three files for changes.
"""

from flask import Flask, jsonify, request, send_from_directory
import json, os, time, threading

app = Flask(__name__, static_folder="static")

TASKS_FILE    = "tasks.json"
EVENTS_FILE   = "events.json"
SHOPPING_FILE = "shopping.json"
CHANGE_FILE   = ".last_change"
file_lock     = threading.Lock()

# ── Storage helpers ────────────────────────────────────────────────────────────

def read_json(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return json.load(f)

def write_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    with open(CHANGE_FILE, "w") as f:
        f.write(str(time.time()))

def last_change_time():
    try:
        with open(CHANGE_FILE) as f:
            return float(f.read())
    except:
        return 0.0

# ── Frontend ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/dashboard")
def dashboard():
    return send_from_directory("static", "dashboard.html")

# ── Tasks ──────────────────────────────────────────────────────────────────────

@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    with file_lock:
        return jsonify(read_json(TASKS_FILE))

@app.route("/api/tasks", methods=["POST"])
def add_task():
    data = request.json
    if not data or not data.get("text", "").strip():
        return jsonify({"error": "text required"}), 400
    task = {
        "id":      int(time.time() * 1000),
        "text":    data["text"].strip(),
        "cat":     data.get("cat", "📝"),
        "author":  data.get("author", "you"),
        "done":    False,
        "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    with file_lock:
        tasks = read_json(TASKS_FILE)
        tasks.insert(0, task)
        write_json(TASKS_FILE, tasks)
    return jsonify(task), 201

@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.json or {}
    with file_lock:
        tasks = read_json(TASKS_FILE)
        task  = next((t for t in tasks if t["id"] == task_id), None)
        if not task:
            return jsonify({"error": "not found"}), 404
        if "done" in data: task["done"] = bool(data["done"])
        if "text" in data: task["text"] = data["text"].strip()
        if "cat"  in data: task["cat"]  = data["cat"]
        write_json(TASKS_FILE, tasks)
    return jsonify(task)

@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    with file_lock:
        tasks = read_json(TASKS_FILE)
        new   = [t for t in tasks if t["id"] != task_id]
        if len(new) == len(tasks):
            return jsonify({"error": "not found"}), 404
        write_json(TASKS_FILE, new)
    return jsonify({"deleted": task_id})

# ── Events ─────────────────────────────────────────────────────────────────────

@app.route("/api/events", methods=["GET"])
def get_events():
    with file_lock:
        return jsonify(read_json(EVENTS_FILE))

@app.route("/api/events", methods=["POST"])
def add_event():
    data = request.json
    if not data or not data.get("title", "").strip():
        return jsonify({"error": "title required"}), 400
    event = {
        "id":         int(time.time() * 1000),
        "title":      data["title"].strip(),
        "date":       data.get("date", ""),
        "time":       data.get("time", ""),
        "notes":      data.get("notes", "").strip(),
        "author":     data.get("author", "you"),
        "recur":      data.get("recur", "none"),
        "recur_days": data.get("recur_days", []),
        "recur_end":  data.get("recur_end", None),
        "created":    time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    with file_lock:
        events = read_json(EVENTS_FILE)
        events.append(event)
        events.sort(key=lambda e: (e["date"], e["time"]))
        write_json(EVENTS_FILE, events)
    return jsonify(event), 201

@app.route("/api/events/<int:event_id>", methods=["PUT"])
def update_event(event_id):
    data = request.json or {}
    with file_lock:
        events = read_json(EVENTS_FILE)
        event  = next((e for e in events if e["id"] == event_id), None)
        if not event:
            return jsonify({"error": "not found"}), 404
        for field in ["title", "date", "time", "notes", "recur", "recur_end"]:
            if field in data:
                event[field] = data[field].strip() if isinstance(data[field], str) else data[field]
        events.sort(key=lambda e: (e["date"], e["time"]))
        write_json(EVENTS_FILE, events)
    return jsonify(event)

@app.route("/api/events/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    with file_lock:
        events = read_json(EVENTS_FILE)
        new    = [e for e in events if e["id"] != event_id]
        if len(new) == len(events):
            return jsonify({"error": "not found"}), 404
        write_json(EVENTS_FILE, new)
    return jsonify({"deleted": event_id})

# ── Shopping ───────────────────────────────────────────────────────────────────
# Each item:
#   id, name, qty, unit, aisle, checked, recurring, author, created

@app.route("/api/shopping", methods=["GET"])
def get_shopping():
    with file_lock:
        return jsonify(read_json(SHOPPING_FILE))

@app.route("/api/shopping", methods=["POST"])
def add_shopping():
    data = request.json
    if not data or not data.get("name", "").strip():
        return jsonify({"error": "name required"}), 400
    item = {
        "id":        int(time.time() * 1000),
        "name":      data["name"].strip(),
        "qty":       data.get("qty", 1),
        "unit":      data.get("unit", "").strip(),       # e.g. "kg", "pack", ""
        "aisle":     data.get("aisle", "Other"),         # e.g. "Produce", "Dairy"
        "checked":   False,
        "recurring": data.get("recurring", False),       # always on the list
        "author":    data.get("author", "you"),
        "created":   time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    with file_lock:
        items = read_json(SHOPPING_FILE)
        items.append(item)
        items.sort(key=lambda i: i["aisle"])
        write_json(SHOPPING_FILE, items)
    return jsonify(item), 201

@app.route("/api/shopping/<int:item_id>", methods=["PUT"])
def update_shopping(item_id):
    data = request.json or {}
    with file_lock:
        items = read_json(SHOPPING_FILE)
        item  = next((i for i in items if i["id"] == item_id), None)
        if not item:
            return jsonify({"error": "not found"}), 404
        for field in ["name", "unit", "aisle"]:
            if field in data: item[field] = data[field].strip()
        if "qty"       in data: item["qty"]       = data["qty"]
        if "checked"   in data: item["checked"]   = bool(data["checked"])
        if "recurring" in data: item["recurring"] = bool(data["recurring"])
        items.sort(key=lambda i: i["aisle"])
        write_json(SHOPPING_FILE, items)
    return jsonify(item)

@app.route("/api/shopping/<int:item_id>", methods=["DELETE"])
def delete_shopping(item_id):
    with file_lock:
        items = read_json(SHOPPING_FILE)
        new   = [i for i in items if i["id"] != item_id]
        if len(new) == len(items):
            return jsonify({"error": "not found"}), 404
        write_json(SHOPPING_FILE, new)
    return jsonify({"deleted": item_id})

@app.route("/api/shopping/clear-checked", methods=["POST"])
def clear_checked():
    """
    Remove all checked non-recurring items after shopping.
    Recurring items get unchecked instead so they reappear next trip.
    """
    with file_lock:
        items = read_json(SHOPPING_FILE)
        kept  = []
        for i in items:
            if i["checked"] and i["recurring"]:
                i["checked"] = False   # reset recurring → stays on list unchecked
                kept.append(i)
            elif not i["checked"]:
                kept.append(i)
            # checked + not recurring → removed
        write_json(SHOPPING_FILE, kept)
    return jsonify(kept)

# ── Long poll (tasks + events + shopping) ─────────────────────────────────────

@app.route("/api/poll/<float:since>")
def poll(since):
    deadline = time.time() + 25
    while time.time() < deadline:
        if last_change_time() > since:
            with file_lock:
                tasks    = read_json(TASKS_FILE)
                events   = read_json(EVENTS_FILE)
                shopping = read_json(SHOPPING_FILE)
            return jsonify({
                "changed":  True,
                "tasks":    tasks,
                "events":   events,
                "shopping": shopping,
                "ts":       last_change_time()
            })
        time.sleep(0.5)
    return jsonify({"changed": False, "ts": last_change_time()})

# ── Run ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("╔══════════════════════════════════╗")
    print("║   💕 two-do · home server         ║")
    print("║   http://localhost:5001           ║")
    print("╚══════════════════════════════════╝")
    app.run(host="0.0.0.0", port=5001, debug=False, threaded=True)
