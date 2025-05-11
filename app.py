from flask import Flask, render_template, request, redirect, url_for
import random

app = Flask(__name__)
import os
TASK_FILE = os.path.join(os.path.dirname(__file__), "tasks.txt")

def load_tasks():
    try:
        with open(TASK_FILE, "r") as f:
            return [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        return []



def save_task(task_text):
    print("Saving to:", os.path.abspath(TASK_FILE))  # ✅ Add this line
    with open(TASK_FILE, "a") as f:
        f.write(task_text + "\n")


def delete_task(task_text):
    tasks = load_tasks()
    tasks = [task for task in tasks if task.strip() != task_text.strip()]
    with open(TASK_FILE, "w") as f:
        f.writelines([task + "\n" for task in tasks])



@app.route("/")
def index():
    tasks = load_tasks()
    return render_template("index.html", tasks=tasks)

@app.route("/add", methods=["GET", "POST"])
def add_task():
    if request.method == "POST":
        task = request.form.get("task")
        duration = request.form.get("duration")
        if task and duration:
            save_task(f"{task} – {duration} mins")
        return redirect("/")
    return render_template("add.html")

@app.route("/delete", methods=["POST"])
def delete():
    task = request.form.get("task")
    print(f"Received request to delete: '{task}'")  # Debug
    delete_task(task)
    return redirect("/")

# ✅ ONLY THIS kill_time ROUTE SHOULD EXIST
@app.route("/kill-time", methods=["GET", "POST"])
def kill_time():
    if request.method == "POST":
        minutes_available = int(request.form.get("minutes", 0))
        tasks = load_tasks()
        suitable_tasks = []

        for task in tasks:
            if "–" in task:
                task_name, duration = task.split(" – ")
                duration = int(duration.replace(" mins", "").strip())
                if duration <= minutes_available:
                    suitable_tasks.append((task_name, duration))

        if suitable_tasks:
            chosen = random.choice(suitable_tasks)
            return redirect(url_for("task_detail", task=chosen[0], duration=chosen[1]))
        else:
            return render_template("time_to_kill.html", chosen_task="No suitable tasks found!")

    return render_template("time_to_kill.html")

@app.route('/edit', methods=['POST'])
def edit_task():
    original_task = request.form['original_task'].strip()
    new_task_name = request.form['new_task_name'].strip()
    new_duration = request.form['new_duration'].strip()
    new_task_line = f"{new_task_name} – {new_duration}"

    if os.path.exists(TASK_FILE):
        with open(TASK_FILE, 'r') as file:
            lines = file.readlines()
        
        with open(TASK_FILE, 'w') as file:
            for line in lines:
                if line.strip() == original_task:
                    file.write(new_task_line + "\n")
                else:
                    file.write(line)

    return redirect('/')



@app.route("/task")
def task_detail():
    task_name = request.args.get("task", "No Task")
    duration = int(request.args.get("duration", 0))
    return render_template("task_detail.html", task_name=task_name, duration=duration)

@app.route("/switch-task")
def switch_task():
    try:
        minutes = int(request.args.get("minutes", 0))
        current_task = request.args.get("current_task", "")
        tasks = load_tasks()
        suitable_tasks = []

        for task in tasks:
            if "–" in task:
                task_name, duration = task.split(" – ")
                duration = int(duration.replace(" mins", "").strip())
                if duration <= minutes:
                    suitable_tasks.append((task_name, duration))

        # Filter out the current task if there are other options
        alternatives = [t for t in suitable_tasks if t[0] != current_task]
        chosen_pool = alternatives if alternatives else suitable_tasks

        if chosen_pool:
            chosen = random.choice(chosen_pool)
            return redirect(url_for("task_detail", task=chosen[0], duration=chosen[1]))
        else:
            return render_template("task_detail.html", task_name="No suitable tasks found!", duration=0)
    except Exception:
        return render_template("task_detail.html", task_name="Error selecting task", duration=0)



if __name__ == "__main__":
    app.run(debug=True)
