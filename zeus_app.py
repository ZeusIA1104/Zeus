import streamlit as st
import sqlite3
import hashlib
from datetime import date
from fpdf import FPDF
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import requests

# === CONFIG ===
ACCESS_TOKEN = "APP_USR-507730409898756-041401-cfb0d18f342ea0b8ada862a23497b9ca-1026722362"
ADMIN_EMAIL = "guibarcellosdaniel6@gmail.com"

# === BANCO DE DADOS ===
def criar_banco():
    conn = sqlite3.connect("zeus_usuarios.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            genero TEXT,
            peso REAL,
            altura REAL,
            objetivo TEXT,
            status_pagamento TEXT DEFAULT 'pendente'
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS progresso (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            data TEXT,
            peso REAL,
            calorias_consumidas INTEGER,
            treino_realizado TEXT,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
    """)
    conn.commit()
    conn.close()

# === AUTENTICAÇÃO ===
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def verificar_login(email, senha):
    conn = sqlite3.connect("zeus_usuarios.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email=? AND senha=?", (email, hash_senha(senha)))
    user = cursor.fetchone()
    conn.close()
    return user

def atualizar_status_pagamento(email, status):
    conn = sqlite3.connect("zeus_usuarios.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE usuarios SET status_pagamento=? WHERE email=?", (status, email))
    conn.commit()
    conn.close()

def buscar_status_pagamento(email):
    conn = sqlite3.connect("zeus_usuarios.db")
    cursor = conn.cursor()
    cursor.execute("SELECT status_pagamento FROM usuarios WHERE email=?", (email,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else "pendente"

# === PAGAMENTO ===
def gerar_link_pagamento(nome_usuario):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    body = {
        "items": [{
            "title": "Assinatura Mensal - ZEUS",
            "quantity": 1,
            "currency_id": "BRL",
            "unit_price": 49.90
        }],
        "payer": {
            "name": nome_usuario
        }
    }
    response = requests.post("https://api.mercadopago.com/checkout/preferences", headers=headers, json=body)
    if response.status_code == 201:
        return response.json()["init_point"]
    return None

def verificar_pagamento(email_usuario):
    if email_usuario == ADMIN_EMAIL:
        return True
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    url = "https://api.mercadopago.com/v1/payments/search"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        results = response.json().get("results", [])
        for pagamento in results:
            payer_email = pagamento.get("payer", {}).get("email", "").lower()
            status = pagamento.get("status")
            if payer_email == email_usuario.lower() and status == "approved":
                atualizar_status_pagamento(email_usuario, "aprovado")
                return True
    return False
# === IMC, PROGRESSO E PDF ===
def calcular_imc(peso, altura):
    return round(peso / (altura ** 2), 2)

def classificar_imc(imc):
    if imc < 18.5:
        return "Abaixo do peso"
    elif imc < 25:
        return "Peso normal"
    elif imc < 30:
        return "Sobrepeso"
    elif imc < 35:
        return "Obesidade Grau I"
    elif imc < 40:
        return "Obesidade Grau II"
    else:
        return "Obesidade Grau III"

def grafico_imc(usuario_id, altura):
    conn = sqlite3.connect("zeus_usuarios.db")
    cursor = conn.cursor()
    cursor.execute("SELECT data, peso FROM progresso WHERE usuario_id=? ORDER BY data", (usuario_id,))
    registros = cursor.fetchall()
    conn.close()
    if registros:
        datas = [r[0] for r in registros]
        pesos = [r[1] for r in registros]
        imcs = [round(p / (altura ** 2), 2) for p in pesos]
        fig = go.Figure(data=go.Scatter(x=datas, y=imcs, mode='lines+markers'))
        fig.update_layout(title="Evolução do IMC", xaxis_title="Data", yaxis_title="IMC")
        st.plotly_chart(fig)
    else:
        st.info("Nenhum dado de progresso registrado ainda.")

def gerar_pdf(titulo, conteudo):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=titulo, ln=True, align="C")
    pdf.ln(10)
    for linha in conteudo:
        pdf.multi_cell(0, 10, txt=linha)
    pdf_path = titulo.replace(" ", "_") + ".pdf"
    pdf.output(pdf_path)
    return pdf_path

# === INTERFACE PRINCIPAL E LOGIN ===
st.set_page_config(page_title="Zeus", layout="centered")
criar_banco()

if "usuario" not in st.session_state:
    st.session_state["usuario"] = None

st.title("ZEUS - Acesso")

menu = st.selectbox("Menu", ["Login", "Cadastrar"])
email = st.text_input("Email")
senha = st.text_input("Senha", type="password")

if menu == "Cadastrar":
    nome = st.text_input("Nome completo")
    genero = st.selectbox("Gênero", ["Masculino", "Feminino", "Outro"])
    peso = st.number_input("Peso (kg)", 30.0, 200.0)
    altura = st.number_input("Altura (m)", 1.0, 2.5)
    objetivo = st.selectbox("Objetivo", ["Hipertrofia", "Emagrecimento", "Manutenção", "Ganho de Massa Muscular"])
    if st.button("Cadastrar"):
        try:
            conn = sqlite3.connect("zeus_usuarios.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO usuarios (nome, email, senha, genero, peso, altura, objetivo) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (nome, email, hash_senha(senha), genero, peso, altura, objetivo))
            conn.commit()
            conn.close()
            st.success("Cadastro realizado com sucesso! Faça login para continuar.")
        except:
            st.error("Erro: E-mail já cadastrado ou dados inválidos.")

elif menu == "Login":
    if st.button("Entrar"):
        user = verificar_login(email, senha)
        if user:
            st.session_state["usuario"] = user
            st.experimental_rerun()
        else:
            st.error("E-mail ou senha incorretos.")

# === BLOQUEIO DE ACESSO ===
if st.session_state["usuario"]:
    user = st.session_state["usuario"]
    email_user = user[2]
    nome_usuario = user[1]

    if not verificar_pagamento(email_user):
        st.warning("Pagamento não confirmado. Pague para liberar o acesso.")
        link_pagamento = gerar_link_pagamento(nome_usuario)
        if link_pagamento:
            st.markdown(f"[Clique aqui para pagar R$49,90]({link_pagamento})", unsafe_allow_html=True)
        if st.button("Verificar Pagamento"):
            if verificar_pagamento(email_user):
                st.success("Pagamento confirmado! Recarregue a página.")
                st.experimental_rerun()
            else:
                st.error("Pagamento ainda não identificado.")
        st.stop()
    # === PAINEL ZEUS LIBERADO ===
    st.title(f"Bem-vindo ao Zeus, {nome_usuario}!")
    st.metric("Peso Atual", f"{user[5]} kg")
    imc = calcular_imc(user[5], user[6])
    st.metric("IMC", imc, classificar_imc(imc))
    grafico_imc(user[0], user[6])

    st.subheader("Registrar Progresso Diário")
    novo_peso = st.number_input("Peso de hoje (kg)", 30.0, 200.0, step=0.1)
    calorias = st.number_input("Calorias consumidas hoje", 0, 8000)
    treino = st.text_input("Treino realizado")
    if st.button("Salvar progresso"):
        conn = sqlite3.connect("zeus_usuarios.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO progresso (usuario_id, data, peso, calorias_consumidas, treino_realizado) VALUES (?, ?, ?, ?, ?)",
                       (user[0], str(date.today()), novo_peso, calorias, treino))
        conn.commit()
        conn.close()
        st.success("Progresso registrado com sucesso!")

    # === MENU PRINCIPAL DO USUÁRIO ===
    aba = st.selectbox("Escolha uma seção", ["Treino", "Dieta da Semana", "Suplementos e Receitas", "Gerar PDF"])

   # ------------------ Treinos por grupo muscular e objetivo ------------------

treinos = {
    "Peito": {
        "Hipertrofia": [
            "Supino reto com barra - 4x10",
            "Supino inclinado com halteres - 4x10",
            "Crucifixo reto - 3x12",
            "Crossover - 3x15",
            "Peck deck - 3x12"
        ],
        "Emagrecimento": [
            "Flexões - 4x20",
            "Supino reto leve - 3x20",
            "Crossover contínuo - 3x20",
            "Peck deck leve - 3x20",
            "Flexão com apoio - 4x15"
        ],
        "Resistência": [
            "Flexões inclinadas - 4x25",
            "Supino reto com isometria - 3x30s",
            "Crucifixo leve - 3x25",
            "Flexões declinadas - 3x20",
            "Crossover alternado - 3x30"
        ],
        "Ganho de Massa Muscular": [
            "Supino reto pesado - 5x5",
            "Supino inclinado com barra - 4x6",
            "Crucifixo inclinado com halteres - 4x8",
            "Crossover com peso - 3x8",
            "Peck deck pesado - 4x8"
        ]
    },
    "Ombro": {
        "Hipertrofia": [
            "Elevação lateral - 4x12",
            "Desenvolvimento com barra - 4x10",
            "Elevação frontal - 3x12",
            "Remada alta - 3x12",
            "Desenvolvimento Arnold - 3x10"
        ],
        "Emagrecimento": [
            "Elevação lateral leve - 4x15",
            "Desenvolvimento com halteres leves - 3x15",
            "Elevação alternada - 3x20",
            "Circuito de ombros com peso corporal - 3x20",
            "Remada com elástico - 3x20"
        ],
        "Resistência": [
            "Elevação lateral contínua - 4x20",
            "Desenvolvimento leve - 4x20",
            "Remada alta leve - 3x20",
            "Exercício de isometria - 3x30s",
            "Elevação frontal com pausa - 3x20"
        ],
        "Ganho de Massa Muscular": [
            "Desenvolvimento com halteres pesados - 5x6",
            "Elevação lateral com peso - 4x8",
            "Arnold press - 4x8",
            "Desenvolvimento militar - 4x6",
            "Face pull com carga - 4x10"
        ]
    },
    "Bíceps": {
        "Hipertrofia": [
            "Rosca direta com barra - 4x10",
            "Rosca martelo com halteres - 4x10",
            "Rosca alternada - 4x10",
            "Rosca concentrada - 3x12",
            "Rosca Scott - 3x10"
        ],
        "Emagrecimento": [
            "Rosca leve com alta repetição - 4x20",
            "Rosca alternada leve - 4x20",
            "Rosca com elástico - 3x25",
            "Rosca com isometria - 3x30s",
            "Circuito de bíceps - 3x20"
        ],
        "Resistência": [
            "Rosca direta leve - 4x20",
            "Rosca martelo com repetição contínua - 3x25",
            "Rosca concentrada - 4x20",
            "Rosca com tempo sob tensão - 3x20",
            "Curl 21's leve - 3x7"
        ],
        "Ganho de Massa Muscular": [
            "Rosca direta com barra pesada - 5x6",
            "Rosca martelo com peso - 4x6",
            "Rosca alternada com carga - 4x8",
            "Rosca concentrada - 4x8",
            "Rosca no cabo - 3x10"
        ]
    },
    "Tríceps": {
        "Hipertrofia": [
            "Tríceps testa - 4x10",
            "Tríceps pulley com barra - 4x10",
            "Tríceps corda - 4x12",
            "Mergulho entre bancos - 3x12",
            "Tríceps francês - 3x10"
        ],
        "Emagrecimento": [
            "Tríceps com elástico - 4x15",
            "Flexão fechada - 3x20",
            "Tríceps banco - 3x15",
            "Pulley leve - 3x20",
            "Extensão leve acima da cabeça - 3x20"
        ],
        "Resistência": [
            "Tríceps contínuo no banco - 4x20",
            "Tríceps corda leve - 3x25",
            "Pulley com isometria - 3x30s",
            "Flexão fechada isométrica - 3x20",
            "Circuito de tríceps - 3x20"
        ],
        "Ganho de Massa Muscular": [
            "Tríceps pulley pesado - 5x6",
            "Tríceps francês com peso - 4x8",
            "Tríceps corda pesado - 4x8",
            "Mergulho com peso - 4x6",
            "Supino fechado - 4x8"
        ]
    },
    "Pernas": {
        "Hipertrofia": [
            "Agachamento livre - 4x10",
            "Leg press - 4x10",
            "Cadeira extensora - 3x12",
            "Mesa flexora - 3x12",
            "Stiff com barra - 4x8"
        ],
        "Emagrecimento": [
            "Agachamento com peso corporal - 4x20",
            "Afundo alternado - 4x15",
            "Leg press leve - 4x15",
            "Cadeira extensora leve - 3x20",
            "Step-ups em banco - 3x15"
        ],
        "Resistência": [
            "Agachamento - 4x20",
            "Cadeira extensora leve - 3x20",
            "Mesa flexora leve - 3x20",
            "Afundo estático - 4x20",
            "Polichinelos com agachamento - 3x25"
        ],
        "Ganho de Massa Muscular": [
            "Agachamento livre pesado - 5x6",
            "Leg press pesado - 5x8",
            "Cadeira extensora pesada - 4x8",
            "Mesa flexora pesada - 4x8",
            "Avanço com halteres - 4x10"
        ]
    },
    "Costas": {
        "Hipertrofia": [
            "Remada curvada com barra - 4x10",
            "Puxada alta na polia - 4x10",
            "Remada cavalinho - 4x10",
            "Levantamento terra - 4x8",
            "Remada unilateral - 4x10"
        ],
        "Emagrecimento": [
            "Puxada alta leve - 4x15",
            "Remada com elástico - 4x20",
            "Remada inversa - 3x20",
            "Puxada com triângulo - 3x15",
            "Burpee com remada - 4x30s"
        ],
        "Resistência": [
            "Remada leve - 4x20",
            "Puxada aberta contínua - 3x25",
            "Remada serrote leve - 3x20",
            "Remada no banco - 4x20",
            "Puxada com isometria - 3x30s"
        ],
        "Ganho de Massa Muscular": [
            "Barra fixa com peso - 4x6",
            "Remada curvada pesada - 5x6",
            "Remada unilateral com halteres - 4x8",
            "Puxada fechada - 4x8",
            "Levantamento terra pesado - 4x6"
        ]
    },
    "Glúteos": {
        "Hipertrofia": [
            "Elevação de quadril com barra - 4x10",
            "Agachamento sumô - 4x10",
            "Avanço com peso - 4x10",
            "Cadeira abdutora - 3x12",
            "Extensão de quadril na polia - 3x15"
        ],
        "Emagrecimento": [
            "Glute bridge com peso corporal - 4x20",
            "Agachamento lateral - 4x15",
            "Elevação de quadril unilateral - 3x15",
            "Afundo alternado - 3x20",
            "Step up - 3x15"
        ],
        "Resistência": [
            "Ponte de glúteo - 4x20",
            "Agachamento com isometria - 3x30s",
            "Extensão com elástico - 3x25",
            "Cadeira abdutora leve - 3x20",
            "Afundo com pausa - 3x20"
        ],
        "Ganho de Massa Muscular": [
            "Hip thrust pesado - 5x6",
            "Avanço com barra - 4x8",
            "Extensão de quadril com carga - 4x8",
            "Cadeira abdutora pesada - 4x10",
            "Agachamento sumô com peso - 4x8"
        ]
    }
}

def gerar_treino(grupo, objetivo):
    return treinos.get(grupo, {}).get(objetivo, ["Nenhum treino disponível para essa combinação."])

    # ------------------ Dietas Semanais por Objetivo ------------------
dietas_semanais = {
    "Emagrecimento": {
        "Segunda": [("Café da manhã", "1 ovo, pão integral, café", 250),
                    ("Almoço", "Frango, arroz integral, salada", 400),
                    ("Jantar", "Sopa de legumes", 300)],
        "Terça": [("Café da manhã", "Iogurte com aveia", 220),
                  ("Almoço", "Peixe, batata doce, salada", 370),
                  ("Jantar", "Omelete com legumes", 280)],
        "Quarta": [("Café da manhã", "Smoothie de frutas", 250),
                   ("Almoço", "Tofu, quinoa, legumes", 360),
                   ("Jantar", "Salada com grão-de-bico", 290)],
        "Quinta": [("Café da manhã", "2 ovos, chá verde", 200),
                   ("Almoço", "Frango, arroz integral, brócolis", 380),
                   ("Jantar", "Caldo de frango", 300)],
        "Sexta": [("Café da manhã", "Panqueca de aveia", 230),
                  ("Almoço", "Frango, abóbora, couve", 360),
                  ("Jantar", "Iogurte com chia", 280)]
    },
    "Hipertrofia": {
        "Segunda": [("Café da manhã", "3 ovos, pão, banana", 450),
                    ("Almoço", "Carne vermelha, arroz, legumes", 600),
                    ("Jantar", "Frango, macarrão, salada", 500)],
        "Terça": [("Café da manhã", "Omelete com espinafre", 480),
                  ("Almoço", "Peixe, batata doce, salada", 600),
                  ("Jantar", "Tofu com abóbora", 500)],
        "Quarta": [("Café da manhã", "Shake de whey com aveia", 450),
                   ("Almoço", "Frango, arroz, feijão, vegetais", 650),
                   ("Jantar", "Omelete com batata doce", 520)],
        "Quinta": [("Café da manhã", "Smoothie de proteína vegetal", 430),
                   ("Almoço", "Carne moída, purê de batata", 630),
                   ("Jantar", "Frango com legumes", 500)],
        "Sexta": [("Café da manhã", "Pão integral com ovo", 420),
                  ("Almoço", "Frango, arroz, lentilha", 640),
                  ("Jantar", "Ovos com batata", 510)]
    }
}
dietas_semanais["Ganho de Massa Muscular"] = dietas_semanais["Hipertrofia"]
dietas_semanais["Manutenção"] = dietas_semanais["Emagrecimento"]

   # ------------------ Suplementos e Receitas ------------------
def dicas_suplementos(objetivo):
    if objetivo == "Emagrecimento":
        return ["Cafeína", "L-Carnitina", "Chá verde"]
    elif objetivo == "Hipertrofia":
        return ["Whey", "Creatina", "BCAA"]
    elif objetivo == "Ganho de Massa Muscular":
        return ["Whey", "Creatina", "BCAA", "Hipercalórico"]
    else:
        return ["Multivitamínico", "Ômega 3"]

def receitas_fitness():
    return [
        "Panqueca de banana com aveia",
        "Shake de morango com whey",
        "Omelete com espinafre",
        "Frango com legumes",
        "Salada de quinoa"
    ]

    # === GERAR PDF ===
    elif aba == "Gerar PDF":
        st.subheader("Gerar plano completo em PDF")
        treino = st.session_state.get("treino", [])
        dieta = st.session_state.get("dieta", [])
        suplementos = st.session_state.get("suplementos", [])
        receitas = st.session_state.get("receitas", [])
        if st.button("Gerar PDF"):
            conteudo = ["Plano de Treino:"] + treino + ["", "Plano de Dieta:"] + dieta + ["", "Suplementos:"] + suplementos + ["", "Receitas:"] + receitas
            pdf_path = gerar_pdf("Plano Zeus", conteudo)
            with open(pdf_path, "rb") as f:
                st.download_button("Baixar PDF", f, file_name="Plano_Zeus.pdf")
