import customtkinter as ctk
import sqlite3
from tkcalendar import DateEntry
from datetime import datetime
import win32com.client as win32
from PIL import Image
import requests

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ---------------- BANCO ----------------

conn = sqlite3.connect("peixaria.db")
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

numero_peixe_atual = 0

# ---------------- JANELA ----------------

app = ctk.CTk()
app.geometry("900x700")
app.title("🐟 Peixaria - IBM Edition")

app.grid_rowconfigure(1, weight=1)
app.grid_columnconfigure(0, weight=1)

# ---------------- HEADER ----------------

header = ctk.CTkFrame(app, height=70)
header.grid(row=0, column=0, sticky="ew")

logo_path = r"C:\Users\Usuario\Documents\Peixaria app - IBM -- Ideia Boas Mergulham\img\ibm_logo.png"

logo_img = ctk.CTkImage(
    light_image=Image.open(logo_path),
    dark_image=Image.open(logo_path),
    size=(120,40)
)

logo_label = ctk.CTkLabel(header, image=logo_img, text="")
logo_label.pack(side="left", padx=20, pady=15)

titulo = ctk.CTkLabel(header, text="Peixaria Analytics", font=("Arial",22,"bold"))
titulo.pack(side="left")

# ---------------- MAIN ----------------

main = ctk.CTkFrame(app)
main.grid(row=1, column=0, sticky="nsew", padx=30, pady=20)

# ---------------- FUNÇÕES ----------------

def obter_numero_peixe():
    cursor.execute("SELECT COUNT(*) FROM peixes")
    return cursor.fetchone()[0]


def calcular_quarter(data):
    mes = data.month

    if mes <= 3:
        return "Q1"
    elif mes <= 6:
        return "Q2"
    elif mes <= 9:
        return "Q3"
    else:
        return "Q4"


def enviar_email():

    global numero_peixe_atual

    if numero_peixe_atual == 0:
        numero_peixe_atual = obter_numero_peixe()

    inicio = datetime.strptime(data_inicio.get(), "%d/%m/%Y")
    quarter = calcular_quarter(inicio)

    periodo = f"{data_inicio.get()} – {data_fim.get()}"

    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)

    mail.To = "SEU_EMAIL@EMPRESA.COM"

    mail.Subject = f"Peixe #{numero_peixe_atual} – Process Excellence in Incentive eXecution & Efficiency – {quarter}"

    corpo = f"""
Hello,

I would like to share a recent contribution:

Activity: {atividade.get()}
Period: {periodo}
Complexity: {ranking.get()}

Business impact:
{impacto.get("1.0","end")}

You can also explore my Fish Tank – Contribution Board and leave a comment about this contribution:

[LINK_TO_FISH_TANK]

Contribution FishScore explanation:

🐟 Sardinha — Small contribution or operational support
🐠 Tilápia — Moderate process support or issue resolution
🐡 Salmão — Significant process contribution and activity
🐬 Dourado — High-impact contribution with measurable results
🦈 Tubarão — Strategic contribution with major business impact

Feel free to visit the board and leave your feedback.

Best regards,
Lucas
"""

    mail.Body = corpo
    mail.Display()


def salvar():

    global numero_peixe_atual

    periodo = f"{data_inicio.get()} – {data_fim.get()}"

    cursor.execute("""
    INSERT INTO peixes(atividade,periodo,ranking,impacto)
    VALUES(?,?,?,?)
    """, (
        atividade.get(),
        periodo,
        ranking.get(),
        impacto.get("1.0", "end")
    ))

    conn.commit()

    numero_peixe_atual = obter_numero_peixe()

    # ---------------- ENVIA PARA O FISH TANK ONLINE ----------------

    try:

        requests.post(
            "https://fish-tank-p6c1.onrender.com/api/add_peixe",
            json={
                "atividade": atividade.get(),
                "periodo": periodo,
                "ranking": ranking.get(),
                "impacto": impacto.get("1.0", "end")
            }
        )

    except:
        print("Erro ao enviar para Fish Tank online")

    carregar()


def carregar():

    for widget in frame_cards.winfo_children():
        widget.destroy()

    cursor.execute("SELECT * FROM peixes")
    dados = cursor.fetchall()

    for peixe in dados:

        card = ctk.CTkFrame(frame_cards, corner_radius=12)
        card.pack(pady=8, fill="x")

        titulo_card = ctk.CTkLabel(
            card,
            text=f"Peixe #{peixe[0]} — {peixe[1]}",
            font=("Arial",16,"bold")
        )
        titulo_card.pack(anchor="w", padx=15, pady=5)

        periodo_label = ctk.CTkLabel(card, text=f"Período: {peixe[2]}")
        periodo_label.pack(anchor="w", padx=15)

        ranking_label = ctk.CTkLabel(card, text=f"Ranking: {peixe[3]}")
        ranking_label.pack(anchor="w", padx=15, pady=(0,10))


# ---------------- FORMULÁRIO ----------------

atividade = ctk.CTkEntry(main, placeholder_text="Activity / Contribution")
atividade.pack(pady=10, fill="x")

frame_datas = ctk.CTkFrame(main)
frame_datas.pack(pady=10)

data_inicio = DateEntry(frame_datas, date_pattern="dd/mm/yyyy")
data_inicio.pack(side="left", padx=10)

data_fim = DateEntry(frame_datas, date_pattern="dd/mm/yyyy")
data_fim.pack(side="left", padx=10)

ranking = ctk.CTkOptionMenu(main, values=[
    "Sardinha 🐟",
    "Tilápia 🐠🐠",
    "Salmão 🐡🐡🐡",
    "Dourado 🐬🐬🐬🐬",
    "Tubarão 🦈🦈🦈🦈🦈"
])
ranking.pack(pady=10)

impacto = ctk.CTkTextbox(main, height=120)
impacto.pack(pady=10, fill="x")

# ---------------- BOTÕES ----------------

botoes_frame = ctk.CTkFrame(main)
botoes_frame.pack(pady=10, fill="x")

btn_salvar = ctk.CTkButton(
    botoes_frame,
    text="Salvar Peixe",
    command=salvar,
    fg_color="#0f62fe",
    hover_color="#0353e9"
)
btn_salvar.pack(side="left", padx=10, expand=True)

btn_email = ctk.CTkButton(
    botoes_frame,
    text="📧 Enviar para gestor",
    command=enviar_email,
    fg_color="#0f62fe",
    hover_color="#0353e9"
)
btn_email.pack(side="left", padx=10, expand=True)

btn_carregar = ctk.CTkButton(
    botoes_frame,
    text="Atualizar Dashboard",
    command=carregar
)
btn_carregar.pack(side="left", padx=10, expand=True)

# ---------------- DASHBOARD ----------------

titulo_dashboard = ctk.CTkLabel(
    main,
    text="🐟 Fish Tank",
    font=("Arial",18,"bold")
)
titulo_dashboard.pack(pady=(20,5))

frame_cards = ctk.CTkScrollableFrame(main)
frame_cards.pack(pady=10, fill="both", expand=True)

carregar()

# ---------------- FOOTER ----------------

footer = ctk.CTkFrame(app, height=35)
footer.grid(row=2, column=0, sticky="ew")

footer_label = ctk.CTkLabel(
    footer,
    text="Peixaria | Developed by Lucas Galdino",
    font=("Arial",11),
    text_color="gray70"
)

footer_label.pack(pady=6)

# ---------------- RUN ----------------

app.mainloop()