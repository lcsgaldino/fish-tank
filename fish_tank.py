from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

# ---------------- DATABASE ----------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "peixaria.db")


def get_db():

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS comentarios(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    peixe_id INTEGER,
    autor TEXT,
    comentario TEXT
    )
    """)

    conn.commit()

    return conn


# ---------------- MURAL ----------------

@app.route("/")
def mural():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM peixes ORDER BY id DESC")
    peixes = cursor.fetchall()

    cursor.execute("SELECT * FROM comentarios")
    comentarios = cursor.fetchall()

    # -------- ESTATÍSTICAS --------

    total_peixes = len(peixes)

    big_fish = 0
    for peixe in peixes:
        if "Tubarão" in peixe["ranking"] or "Dourado" in peixe["ranking"]:
            big_fish += 1

    total_comentarios = len(comentarios)

    conn.close()

    return render_template(
        "mural.html",
        peixes=peixes,
        comentarios=comentarios,
        total_peixes=total_peixes,
        big_fish=big_fish,
        total_comentarios=total_comentarios
    )


# ---------------- COMENTÁRIOS ----------------

@app.route("/comentar", methods=["POST"])
def comentar():

    peixe_id = request.form.get("peixe_id")
    autor = request.form.get("autor", "").strip()
    comentario = request.form.get("comentario", "").strip()

    if comentario == "":
        return redirect("/")

    if autor == "":
        autor = "Anonymous"

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO comentarios (peixe_id, autor, comentario) VALUES (?, ?, ?)",
        (peixe_id, autor, comentario)
    )

    conn.commit()
    conn.close()

    return redirect("/")


# ---------------- RECOGNITION WALL ----------------

@app.route("/recognitions")
def recognitions():

    pasta = os.path.join(BASE_DIR, "static", "recognitions")

    imagens = []

    if os.path.exists(pasta):
        imagens = os.listdir(pasta)

    return render_template("recognitions.html", imagens=imagens)


# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)