from flask import Flask, render_template, request, redirect
import sqlite3
import os
import psycopg2

app = Flask(__name__)

# ---------------- PATH DATABASE ----------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "peixaria.db")


# ---------------- SQLITE (PEIXES) ----------------

def get_db():

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS peixes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        atividade TEXT,
        periodo TEXT,
        ranking TEXT,
        impacto TEXT
    )
    """)

    conn.commit()

    return conn


# ---------------- POSTGRES (COMENTARIOS) ----------------

def get_pg():

    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise Exception("DATABASE_URL não encontrada no Render")

    conn = psycopg2.connect(database_url)

    return conn


def init_pg():

    conn = get_pg()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS comentarios(
        id SERIAL PRIMARY KEY,
        peixe_id INTEGER,
        autor TEXT,
        comentario TEXT
    )
    """)

    conn.commit()
    conn.close()


# ---------------- MURAL ----------------

@app.route("/")
def mural():

    # ---- PEIXES (SQLITE)

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM peixes ORDER BY id DESC")
    peixes = cursor.fetchall()

    conn.close()

    # ---- COMENTARIOS (POSTGRES)

    pg = get_pg()
    cursor_pg = pg.cursor()

    cursor_pg.execute("SELECT peixe_id, autor, comentario FROM comentarios")

    comentarios = [
        {
            "peixe_id": c[0],
            "autor": c[1],
            "comentario": c[2]
        }
        for c in cursor_pg.fetchall()
    ]

    pg.close()

    # ---- ESTATÍSTICAS

    total_peixes = len(peixes)

    big_fish = 0
    for peixe in peixes:
        if peixe["ranking"] and ("Tubarão" in peixe["ranking"] or "Dourado" in peixe["ranking"]):
            big_fish += 1

    total_comentarios = len(comentarios)

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

    if not comentario:
        return redirect("/")

    if not peixe_id:
        return redirect("/")

    if autor == "":
        autor = "Anonymous"

    peixe_id = int(peixe_id)

    print("Comentário salvo:", peixe_id, autor, comentario)

    conn = get_pg()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO comentarios (peixe_id, autor, comentario) VALUES (%s,%s,%s)",
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


# ---------------- API PEIXARIA DESKTOP ----------------

@app.route("/api/add_peixe", methods=["POST"])
def api_add_peixe():

    data = request.json

    if not data:
        return {"status": "error", "message": "No JSON received"}

    atividade = data.get("atividade")
    periodo = data.get("periodo")
    ranking = data.get("ranking")
    impacto = data.get("impacto")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO peixes (atividade, periodo, ranking, impacto)
        VALUES (?, ?, ?, ?)
    """, (atividade, periodo, ranking, impacto))

    conn.commit()
    conn.close()

    return {"status": "success"}


# ---------------- START APP ----------------

init_pg()

if __name__ == "__main__":
    app.run(debug=True)