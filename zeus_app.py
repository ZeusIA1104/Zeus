import streamlit as st
import sqlite3
import hashlib
from datetime import date
from fpdf import FPDF
import matplotlib.pyplot as plt
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

def buscar_status_pagamento(email):
    conn = sqlite3.connect("zeus_usuarios.db")
    cursor = conn.cursor()
    cursor.execute("SELECT status_pagamento FROM usuarios WHERE email=?", (email,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else "pendente"

def atualizar_status_pagamento(email, status):
    conn = sqlite3.connect("zeus_usuarios.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE usuarios SET status_pagamento=? WHERE email=?", (status, email))
    conn.commit()
    conn.close()
# === PAGAMENTO ===
def gerar_link_pagamento(nome_usuario, email_usuario):
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
            "name": nome_usuario,
            "email": email_usuario
        }
    }
    response = requests.post("https://api.mercadopago.com/checkout/preferences", headers=headers, json=body)
    if response.status_code == 201:
        return response.json()["init_point"]
    return None

def verificar_pagamento_por_nome(nome_usuario):
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    url = "https://api.mercadopago.com/v1/payments/search?sort=date_created&criteria=desc"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        results = response.json().get("results", [])
        for pagamento in results:
            payer_name = pagamento.get("payer", {}).get("first_name", "").lower().strip()
            status = pagamento.get("status", "")
            if payer_name in nome_usuario.lower() and status == "approved":
                return True
    return False

# === FUNÇÕES DE IMC E PDF ===
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

# === INÍCIO DA INTERFACE ===
st.set_page_config(page_title="ZEUS", layout="centered")
criar_banco()
st.title("ZEUS - Acesso")

if "usuario" not in st.session_state:
    st.session_state["usuario"] = None
menu = st.selectbox("Menu", ["Login", "Cadastrar"])
email = st.text_input("Email")
senha = st.text_input("Senha", type="password")

if menu == "Cadastrar":
    nome = st.text_input("Nome completo (use o mesmo do Pix)")
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
            link = gerar_link_pagamento(nome, email)
            if link:
                st.success("Cadastro realizado com sucesso!")
                st.markdown(f"[Clique aqui para pagar R$49,90 e liberar o acesso]({link})", unsafe_allow_html=True)
                st.info("Após o pagamento, clique no botão abaixo:")
                if st.button("Verificar Pagamento"):
                    if verificar_pagamento_por_nome(nome):
                        atualizar_status_pagamento(email, "aprovado")
                        st.success("Pagamento confirmado! Faça login para acessar o Zeus.")
                    else:
                        st.warning("Pagamento ainda não identificado.")
            else:
                st.warning("Não foi possível gerar o link de pagamento.")
        except:
            st.error("Erro: E-mail já cadastrado ou dados inválidos.")

elif menu == "Login":
    if st.button("Entrar"):
        user = verificar_login(email, senha)
        if user:
            nome_usuario = user[1]
            status_pag = buscar_status_pagamento(email)
            if status_pag != "aprovado":
                st.warning("Pagamento não confirmado. Faça o pagamento para continuar.")
                link = gerar_link_pagamento(nome_usuario, email)
                if link:
                    st.markdown(f"[Clique aqui para pagar R$49,90]({link})", unsafe_allow_html=True)
                st.info("Após o pagamento, clique no botão abaixo:")
                if st.button("Verificar Pagamento"):
                    if verificar_pagamento_por_nome(nome_usuario):
                        atualizar_status_pagamento(email, "aprovado")
                        st.success("Pagamento confirmado! Recarregue a página.")
                        st.experimental_rerun()
                    else:
                        st.warning("Pagamento ainda não identificado.")
                st.stop()
            else:
                st.session_state["usuario"] = user
                st.experimental_rerun()
        else:
            st.error("Email ou senha incorretos.")
# === PAINEL DO ADMIN PARA LIBERAR ACESSO MANUAL ===
if st.session_state["usuario"]:
    user = st.session_state["usuario"]
    email_user = user[2]
    if email_user == ADMIN_EMAIL:
        st.subheader("Painel do Administrador - Liberar Acesso Manual")
        nome_alvo = st.text_input("Nome ou parte do nome do usuário para liberar o acesso:")
        if st.button("Liberar acesso manualmente"):
            try:
                conn = sqlite3.connect("zeus_usuarios.db")
                cursor = conn.cursor()
                cursor.execute("UPDATE usuarios SET status_pagamento='aprovado' WHERE nome LIKE ?", (f"%{nome_alvo}%",))
                conn.commit()
                conn.close()
                st.success(f"Acesso de '{nome_alvo}' foi liberado com sucesso!")
            except Exception as e:
                st.error(f"Erro ao liberar acesso: {e}")
