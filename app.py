# app.py
from flask import Flask, request, render_template, g
import sqlite3, os

DB = os.path.join(os.path.dirname(__file__), "guests.db")
app = Flask(__name__)
app.config['DATABASE'] = DB

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/", methods=["GET", "POST"])
def index():
    query = ""
    results = []
    message = None
    if request.method == "POST":
        query = request.form.get("name", "").strip()
        if query:
            db = get_db()
            cur = db.execute("SELECT * FROM guests WHERE lower(full_name) = lower(?)", (query,))
            exact = cur.fetchone()
            if exact:
                results = [exact]
            else:
                qlike = f"%{query}%"
                cur = db.execute(
                    "SELECT * FROM guests WHERE lower(full_name) LIKE lower(?) OR lower(first_name) LIKE lower(?) OR lower(last_name) LIKE lower(?) LIMIT 50",
                    (qlike, qlike, qlike)
                )
                results = cur.fetchall()
            if not results:
                message = "No guest found. Please check spelling or visit the registraion table."
    return render_template("index.html", query=query, results=results, message=message)

@app.route("/guest/<int:guest_id>")
def guest(guest_id):
    db = get_db()
    cur = db.execute("SELECT * FROM guests WHERE id = ?", (guest_id,))
    guest = cur.fetchone()
    if not guest:
        return render_template("result.html", guest=None, error="Guest not found.")
    if guest["paid"] == 0:
        return render_template("result.html", guest=guest, unpaid=True)
    else:
        return render_template("result.html", guest=guest, unpaid=False)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
