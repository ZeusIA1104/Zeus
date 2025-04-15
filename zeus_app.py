import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
import requests
import json

# ---------- CONFIGS ----------
ACCESS_TOKEN = "APP_USR-507730409898756-041401-cfb0d18f342ea0b8ada862a23497b9ca-1026722362"
ADMIN_USERNAME = "guilhermeadm6"
ADMIN_EMAIL = "guibarcellosdaniel6@gmail.com"

# ---------- BANCO DE DADOS ----------
def connect_db():
    conn = sqlite3.connect("zeus_usuarios.db")
    c = conn.cursor()
    return conn, c

def create_usertable():
    conn, c = connect_db()
    c.execute("CREATE TABLE IF NOT EXISTS users(username TEXT, email TEXT, password TEXT, payment_status TEXT DEFAULT 'pendente', payment_link TEXT)")
    conn.commit()
    conn.close()

def add_userdata(username, email, password, payment_link):
    conn, c = connect_db()
    c.execute('INSERT INTO users(username, email, password, payment_status, payment_link) VALUES (?, ?, ?, ?, ?)',
              (username, email, password, "pendente", payment_link))
    conn.commit()
    conn.close()

def login_user(username, password):
    conn, c = connect_db()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    data = c.fetchone()
    conn.close()
    return data

def get_payment_status(username):
    conn, c = connect_db()
    c.execute('SELECT payment_status FROM users WHERE username = ?', (username,))
    status = c.fetchone()
    conn.close()
    return status[0] if status else None

def update_payment_status(username, status):
    conn, c = connect_db()
    c.execute('UPDATE users SET payment_status = ? WHERE username = ?', (status, username))
    conn.commit()
    conn.close()

def get_payment_link(username):
    conn, c = connect_db()
    c.execute('SELECT payment_link FROM users WHERE username = ?', (username,))
    link = c.fetchone()
    conn.close()
    return link[0] if link else None

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

def gerar_link_pagamento(username):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    body = {
        "items": [{
            "title": "Acesso Zeus Mensal",
            "quantity": 1,
            "currency_id": "BRL",
            "unit_price": 49.90
        }],
        "payer": {
            "name": username
        }
    }
    response = requests.post("https://api.mercadopago.com/checkout/preferences", headers=headers, data=json.dumps(body))
    if response.status_code == 201:
        return response.json()["init_point"]
    return None

def tela_login():
    st.title("ZEUS - Seu Personal Digital")

    menu = ["Login", "Cadastro"]
    escolha = st.sidebar.selectbox("Menu", menu)

    if escolha == "Login":
        st.subheader("Entrar na sua conta")

        username = st.text_input("UsuÃ¡rio")
        password = st.text_input("Senha", type='password')
        if st.button("Login"):
            hashed_pswd = make_hashes(password)
            resultado = login_user(username, hashed_pswd)
            if resultado:
                st.success(f"Bem-vindo, {username}!")
                st.session_state['username'] = username
                st.session_state['logado'] = True
            else:
                st.error("UsuÃ¡rio/senha incorretos")

    elif escolha == "Cadastro":
        st.subheader("Criar nova conta")
        new_user = st.text_input("Novo usuÃ¡rio")
        new_email = st.text_input("Email")
        new_password = st.text_input("Senha", type='password')

        if st.button("Cadastrar"):
            hashed_new_password = make_hashes(new_password)
            link_pagamento = gerar_link_pagamento(new_user)
            if link_pagamento:
                add_userdata(new_user, new_email, hashed_new_password, link_pagamento)
                st.success("Conta criada com sucesso!")
                st.info("FaÃ§a login para continuar")
            else:
                st.error("Erro ao gerar link de pagamento")

def verificar_pagamento(username):
    if username == ADMIN_USERNAME:
        return True

    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    pagamentos = requests.get("https://api.mercadopago.com/v1/payments/search", headers=headers)

    if pagamentos.status_code == 200:
        resultados = pagamentos.json().get("results", [])
        for item in resultados:
            nome = item.get("payer", {}).get("name", "").lower()
            status = item.get("status")
            if nome == username.lower() and status == "approved":
                update_payment_status(username, "aprovado")
                return True
    return False

def tela_pagamento(username):
    st.warning("Pagamento ainda nÃ£o confirmado.")
    link = get_payment_link(username)
    if link:
        st.markdown(f"[Clique aqui para pagar R$49,90 e liberar o acesso]({link})", unsafe_allow_html=True)
    if st.button("Verificar pagamento"):
        if verificar_pagamento(username):
            st.success("Pagamento confirmado! Recarregue a pÃ¡gina.")
            st.rerun()
        else:
            st.error("Pagamento ainda nÃ£o identificado.")

def tela_principal(username):
    st.title("ZEUS - Personal Trainer Virtual")

    st.sidebar.subheader("NavegaÃ§Ã£o")
    opcoes = ["Treinos", "Dietas", "Suplementos", "Receitas", "Gerar PDF"]
    escolha = st.sidebar.radio("Escolha uma opÃ§Ã£o", opcoes)

    if escolha == "Treinos":
        st.header("Treinos por Grupo Muscular e Objetivo")
        grupo = st.selectbox("Selecione o grupo muscular", ["Peito", "Costas", "Pernas", "Ombro", "BÃ­ceps", "TrÃ­ceps", "GlÃºteos"])
        objetivo = st.selectbox("Objetivo", ["Hipertrofia", "DefiniÃ§Ã£o", "ResistÃªncia"])
        st.markdown(f"*Treino para {grupo} com foco em {objetivo}:*")
        for i in range(1, 6):
            st.write(f"- ExercÃ­cio {i}: ...")

    elif escolha == "Dietas":
        st.header("Dietas Semanais Personalizadas")
        objetivo_dieta = st.selectbox("Objetivo da dieta", ["Emagrecimento", "Hipertrofia", "ManutenÃ§Ã£o"])
        dia = st.selectbox("Dia da semana", ["Segunda", "TerÃ§a", "Quarta", "Quinta", "Sexta"])
        st.markdown(f"*Dieta de {objetivo_dieta} para {dia}:*")
        st.write("- CafÃ© da manhÃ£: ...")
        st.write("- AlmoÃ§o: ...")
        st.write("- Lanche: ...")
        st.write("- Jantar: ...")

    elif escolha == "Suplementos":
        st.header("SugestÃµes de Suplementos")
        st.write("- Whey Protein)
- Creatina
- CafeÃ­na
- MultivitamÃ­nico")

    elif escolha == "Receitas":
        st.header("Receitas Fitness")
        st.write("- Panqueca de banana
- Frango grelhado com legumes
- Shake de proteÃ­na com aveia")

    elif escolha == "Gerar PDF":
        st.header("PDF com Treino e Dieta")
        st.write("Aqui vocÃª poderÃ¡ gerar o PDF com seus planos. (funÃ§Ã£o ainda em construÃ§Ã£o)")

def main():
    st.set_page_config(page_title="Zeus", layout="centered")
    create_usertable()

    if 'logado' not in st.session_state:
        st.session_state['logado'] = False

    if st.session_state['logado']:
        username = st.session_state['username']
        status_pagamento = get_payment_status(username)

        if username == ADMIN_USERNAME or status_pagamento == "aprovado":
            tela_principal(username)
        else:
            tela_pagamento(username)

    else:
        tela_login()

if _name_ == '_main_':
    main()
