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

    # === TREINO ===
    if aba == "Treino":
        grupo = st.selectbox("Grupo muscular", ["Peito", "Costas", "Ombro", "Bíceps", "Tríceps", "Pernas", "Glúteos"])
        objetivo = user[7]
        treino = {
            "Peito": {
                "Hipertrofia": ["Supino reto - 4x10", "Supino inclinado - 3x12", "Crossover - 3x15"],
                "Emagrecimento": ["Flexão - 4x20", "Peck Deck - 3x15"],
                "Resistência": ["Flexão inclinada - 3x25", "Crucifixo leve - 3x20"],
                "Ganho de Massa Muscular": ["Supino reto pesado - 5x5", "Crucifixo com carga - 4x8"]
            },
            "Costas": {
                "Hipertrofia": ["Puxada frente - 4x10", "Remada curvada - 3x12"],
                "Emagrecimento": ["Puxada leve - 4x15", "Remada unilateral - 3x20"],
                "Resistência": ["Remada leve contínua - 4x20", "Puxada com isometria - 3x30s"],
                "Ganho de Massa Muscular": ["Levantamento terra - 5x5", "Remada cavalinho - 4x8"]
            }
        }
        treino_sugerido = treino.get(grupo, {}).get(objetivo, ["Nenhum treino disponível."])
        st.subheader(f"Treino para {grupo} - Objetivo: {objetivo}")
        for t in treino_sugerido:
            st.write("-", t)
        st.session_state["treino"] = treino_sugerido

    # === DIETA ===
    elif aba == "Dieta da Semana":
        plano = []
        st.subheader(f"Dieta semanal para: {user[7]}")
        dietas = {
            "Emagrecimento": {
                "Segunda": [("Café da manhã", "Ovo + café", 150), ("Almoço", "Frango + salada", 400), ("Jantar", "Sopa de legumes", 300)],
                "Terça": [("Café da manhã", "Iogurte light", 180), ("Almoço", "Peixe + legumes", 420), ("Jantar", "Omelete", 280)]
            },
            "Hipertrofia": {
                "Segunda": [("Café da manhã", "3 ovos + aveia", 400), ("Almoço", "Carne + arroz", 700), ("Jantar", "Macarrão + frango", 600)],
                "Terça": [("Café da manhã", "Whey + banana", 380), ("Almoço", "Frango + batata doce", 650), ("Jantar", "Panqueca", 550)]
            }
        }
        dietas["Ganho de Massa Muscular"] = dietas["Hipertrofia"]
        dietas["Manutenção"] = dietas["Emagrecimento"]

        dias = dietas.get(user[7], {})
        for dia, refeicoes in dias.items():
            st.markdown(f"*{dia}*")
            for refeicao, descricao, kcal in refeicoes:
                st.write(f"- {refeicao}: {descricao} ({kcal} kcal)")
                plano.append(f"{dia} - {refeicao}: {descricao} ({kcal} kcal)")
        st.session_state["dieta"] = plano

    # === SUPLEMENTOS E RECEITAS ===
    elif aba == "Suplementos e Receitas":
        def dicas_suplementos(objetivo):
            if objetivo == "Emagrecimento":
                return ["Cafeína", "L-Carnitina", "Chá verde"]
            elif objetivo == "Hipertrofia":
                return ["Whey Protein", "Creatina", "BCAA"]
            elif objetivo == "Ganho de Massa Muscular":
                return ["Whey", "Creatina", "Hipercalórico"]
            else:
                return ["Multivitamínico", "Ômega 3"]

        def receitas_fitness():
            return ["Panqueca de banana", "Shake de morango", "Omelete", "Frango com legumes", "Salada de quinoa"]

        suplementos = dicas_suplementos(user[7])
        receitas = receitas_fitness()
        st.subheader("Suplementos recomendados:")
        for s in suplementos:
            st.write("-", s)
        st.subheader("Receitas fitness:")
        for r in receitas:
            st.write("-", r)
        st.session_state["suplementos"] = suplementos
        st.session_state["receitas"] = receitas

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
