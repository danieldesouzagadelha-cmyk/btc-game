import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

conn = sqlite3.connect("database.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS players(
id TEXT PRIMARY KEY,
name TEXT,
coins INTEGER
)
""")

conn.commit()


@app.route("/login", methods=["POST"])
def login():

    data = request.json

    user = data["user"]
    name = data["name"]

    cur.execute("SELECT * FROM players WHERE id=?", (user,))
    p = cur.fetchone()

    if not p:

        cur.execute(
        "INSERT INTO players VALUES (?,?,?)",
        (user,name,1000)
        )

        conn.commit()

    cur.execute("SELECT coins FROM players WHERE id=?", (user,))
    coins = cur.fetchone()[0]

    return jsonify({"coins":coins})


@app.route("/bet", methods=["POST"])
def bet():

    data = request.json

    user = data["user"]
    win = data["win"]

    cur.execute("SELECT coins FROM players WHERE id=?", (user,))
    coins = cur.fetchone()[0]

    if win:

        coins += 200

    else:

        coins -= 100

    cur.execute(
    "UPDATE players SET coins=? WHERE id=?",
    (coins,user)
    )

    conn.commit()

    return jsonify({"coins":coins})


@app.route("/ranking")
def ranking():

    cur.execute(
    "SELECT name,coins FROM players ORDER BY coins DESC LIMIT 10"
    )

    rows = cur.fetchall()

    return jsonify(rows)


app.run(port=5000)