from flask import Flask, render_template, request, redirect
import os
import psycopg2

app = Flask(__name__)

# ---------------- POSTGRES CONNECTION ----------------

def get_db():

    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise Exception("DATABASE_URL não encontrada")

    conn = psycopg2.connect(database_url)

    return conn


# ---------------- INIT DATABASE ----------------

def init_db():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS peixes(
        id SERIAL PRIMARY KEY,
        atividade TEXT,
        periodo TEXT,
        ranking TEXT,
        impacto TEXT
    )
    """)

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

    conn = get_db()
    cursor = conn.cursor()

    # ---- PEIXES

    cursor.execute("SELECT * FROM peixes ORDER BY id DESC")

    peixes = [
        {
            "id": p[0],
            "atividade": p[1],
            "periodo": p[2],
            "ranking": p[3],
            "impacto": p[4]
        }
        for p in cursor.fetchall()
    ]

    # ---- COMENTARIOS

    cursor.execute("SELECT peixe_id, autor, comentario FROM comentarios")

    comentarios = [
        {
            "peixe_id": c[0],
            "autor": c[1],
            "comentario": c[2]
        }
        for c in cursor.fetchall()
    ]

    conn.close()

    # ---- ESTATÍSTICAS

    total_peixes = len(peixes)

    big_fish = sum(
        1 for p in peixes if "Tubarão" in p["ranking"] or "Dourado" in p["ranking"]
    )

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

    if autor == "":
        autor = "Anonymous"

    conn = get_db()
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

    pasta = "static/recognitions"

    imagens = []

    if os.path.exists(pasta):
        imagens = os.listdir(pasta)

    return render_template("recognitions.html", imagens=imagens)


# ---------------- API PEIXARIA DESKTOP ----------------

@app.route("/api/add_peixe", methods=["POST"])
def api_add_peixe():

    data = request.json

    if not data:
        return {"status": "error"}

    atividade = data.get("atividade")
    periodo = data.get("periodo")
    ranking = data.get("ranking")
    impacto = data.get("impacto")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO peixes (atividade, periodo, ranking, impacto)
        VALUES (%s,%s,%s,%s)
    """, (atividade, periodo, ranking, impacto))

    conn.commit()
    conn.close()

    return {"status": "success"}


# ---------------- START ----------------

init_db()

if __name__ == "__main__":
    app.run(debug=True)