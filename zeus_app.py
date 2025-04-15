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
    c.execute('''CREATE TABLE IF NOT EXISTS users(
                username TEXT, email TEXT, password TEXT,
                payment_status TEXT DEFAULT "pendente", payment_link TEXT)''')
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

# ---------- SEGURANÇA ----------
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# ---------- MERCADO PAGO ----------
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

        username = st.text_input("Usuário")
        password = st.text_input("Senha", type='password')
        if st.button("Login"):
            hashed_pswd = make_hashes(password)
            resultado = login_user(username, hashed_pswd)
            if resultado:
                st.success(f"Bem-vindo, {username}!")
                st.session_state['username'] = username
                st.session_state['logado'] = True
            else:
                st.error("Usuário/senha incorretos")

    elif escolha == "Cadastro":
        st.subheader("Criar nova conta")
        new_user = st.text_input("Novo usuário")
        new_email = st.text_input("Email")
        new_password = st.text_input("Senha", type='password')

        if st.button("Cadastrar"):
            hashed_new_password = make_hashes(new_password)
            link_pagamento = gerar_link_pagamento(new_user)
            if link_pagamento:
                add_userdata(new_user, new_email, hashed_new_password, link_pagamento)
                st.success("Conta criada com sucesso!")
                st.info("Faça login para continuar")
            else:
                st.error("Erro ao gerar link de pagamento")

# Verificação de pagamento do usuário
def verificar_pagamento(username):
    if username == ADMIN_USERNAME:
        return True

    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    pagamentos = requests.get("https://api.mercadopago.com/v1/payments/search?sort=date_created&criteria=desc&external_reference=",
                              headers=headers)

    if pagamentos.status_code == 200:
        resultados = pagamentos.json().get("results", [])
        for item in resultados:
            nome = item.get("payer", {}).get("name", "").lower()
            status = item.get("status")
            if nome == username.lower() and status == "approved":
                update_payment_status(username, "aprovado")
                return True
    return False

# Tela de aguardo de pagamento
def tela_pagamento(username):
    st.warning("Pagamento ainda não confirmado.")
    link = get_payment_link(username)
    if link:
        st.markdown(f"[Clique aqui para pagar R$49,90 e liberar o acesso]({link})", unsafe_allow_html=True)
    if st.button("Verificar pagamento"):
        if verificar_pagamento(username):
            st.success("Pagamento confirmado! Recarregue a página.")
            st.rerun()
        else:
            st.error("Pagamento ainda não identificado.")
def tela_principal(username):
    st.title("ZEUS - Personal Trainer Virtual")

    st.sidebar.subheader("Navegação")
    opcoes = ["Treinos", "Dietas", "Suplementos", "Receitas", "Gerar PDF"]
    escolha = st.sidebar.radio("Escolha uma opção", opcoes)

    if escolha == "Treinos":
        st.header("Treinos por Grupo Muscular e Objetivo")
        grupo = st.selectbox("Selecione o grupo muscular", ["Peito", "Costas", "Pernas", "Ombro", "Bíceps", "Tríceps", "Glúteos"])
        objetivo = st.selectbox("Objetivo", ["Hipertrofia", "Definição", "Resistência"])
        
        # Aqui você pode adicionar mais treinos personalizados por grupo e objetivo
        st.markdown(f"*Treino para {grupo} com foco em {objetivo}:*")
        st.write("- Exercício 1\n- Exercício 2\n- Exercício 3\n- Exercício 4\n- Exercício 5")

    elif escolha == "Dietas":
        st.header("Dietas Semanais Personalizadas")
        objetivo_dieta = st.selectbox("Objetivo da dieta", ["Emagrecimento", "Hipertrofia", "Manutenção"])
        dia = st.selectbox("Dia da semana", ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"])

        # Aqui você pode fazer um dicionário com variações por dia e objetivo
        st.markdown(f"*Dieta de {objetivo_dieta} para {dia}:*")
        st.write("- Café da manhã: ...\n- Almoço: ...\n- Lanche: ...\n- Jantar: ...")

    elif escolha == "Suplementos":
        st.header("Sugestões de Suplementos")
        st.write("- Whey Protein\n- Creatina\n- Cafeína\n- Multivitamínico")

    elif escolha == "Receitas":
        st.header("Receitas Fitness")
        st.write("- Panqueca de banana\n- Frango grelhado com legumes\n- Shake de proteína com aveia")

    elif escolha == "Gerar PDF":
        st.header("PDF com Treino e Dieta")
        st.write("Aqui você poderá gerar o PDF com seus planos. (função ainda em construção)")
# ---------- INICIAR APP ----------
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
            "Flex\u00f5es - 4x20",
            "Supino reto leve - 3x20",
            "Crossover cont\u00ednuo - 3x20",
            "Peck deck leve - 3x20",
            "Flex\u00e3o com apoio - 4x15"
        ],
        "Resist\u00eancia": [
            "Flex\u00f5es inclinadas - 4x25",
            "Supino reto com isometria - 3x30s",
            "Crucifixo leve - 3x25",
            "Flex\u00f5es declinadas - 3x20",
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
            "Eleva\u00e7\u00e3o lateral - 4x12",
            "Desenvolvimento com barra - 4x10",
            "Eleva\u00e7\u00e3o frontal - 3x12",
            "Remada alta - 3x12",
            "Desenvolvimento Arnold - 3x10"
        ],
        "Emagrecimento": [
            "Eleva\u00e7\u00e3o lateral leve - 4x15",
            "Desenvolvimento com halteres leves - 3x15",
            "Eleva\u00e7\u00e3o alternada - 3x20",
            "Circuito de ombros com peso corporal - 3x20",
            "Remada com el\u00e1stico - 3x20"
        ],
        "Resist\u00eancia": [
            "Eleva\u00e7\u00e3o lateral cont\u00ednua - 4x20",
            "Desenvolvimento leve - 4x20",
            "Remada alta leve - 3x20",
            "Exerc\u00edcio de isometria - 3x30s",
            "Eleva\u00e7\u00e3o frontal com pausa - 3x20"
        ],
        "Ganho de Massa Muscular": [
            "Desenvolvimento com halteres pesados - 5x6",
            "Eleva\u00e7\u00e3o lateral com peso - 4x8",
            "Arnold press - 4x8",
            "Desenvolvimento militar - 4x6",
            "Face pull com carga - 4x10"
        ]
    },
    "B\u00edceps": {
        "Hipertrofia": [
            "Rosca direta com barra - 4x10",
            "Rosca martelo com halteres - 4x10",
            "Rosca alternada - 4x10",
            "Rosca concentrada - 3x12",
            "Rosca Scott - 3x10"
        ],
        "Emagrecimento": [
            "Rosca leve com alta repeti\u00e7\u00e3o - 4x20",
            "Rosca alternada leve - 4x20",
            "Rosca com el\u00e1stico - 3x25",
            "Rosca com isometria - 3x30s",
            "Circuito de b\u00edceps - 3x20"
        ],
        "Resist\u00eancia": [
            "Rosca direta leve - 4x20",
            "Rosca martelo com repeti\u00e7\u00e3o cont\u00ednua - 3x25",
            "Rosca concentrada - 4x20",
            "Rosca com tempo sob tens\u00e3o - 3x20",
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
    "Tr\u00edceps": {
        "Hipertrofia": [
            "Tr\u00edceps testa - 4x10",
            "Tr\u00edceps pulley com barra - 4x10",
            "Tr\u00edceps corda - 4x12",
            "Mergulho entre bancos - 3x12",
            "Tr\u00edceps franc\u00eas - 3x10"
        ],
        "Emagrecimento": [
            "Tr\u00edceps com el\u00e1stico - 4x15",
            "Flex\u00e3o fechada - 3x20",
            "Tr\u00edceps banco - 3x15",
            "Pulley leve - 3x20",
            "Extens\u00e3o leve acima da cabe\u00e7a - 3x20"
        ],
        "Resist\u00eancia": [
            "Tr\u00edceps cont\u00ednuo no banco - 4x20",
            "Tr\u00edceps corda leve - 3x25",
            "Pulley com isometria - 3x30s",
            "Flex\u00e3o fechada isom\u00e9trica - 3x20",
            "Circuito de tr\u00edceps - 3x20"
        ],
        "Ganho de Massa Muscular": [
            "Tr\u00edceps pulley pesado - 5x6",
            "Tr\u00edceps franc\u00eas com peso - 4x8",
            "Tr\u00edceps corda pesado - 4x8",
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
        "Resist\u00eancia": [
            "Agachamento - 4x20",
            "Cadeira extensora leve - 3x20",
            "Mesa flexora leve - 3x20",
            "Afundo est\u00e1tico - 4x20",
            "Polichinelos com agachamento - 3x25"
        ],
        "Ganho de Massa Muscular": [
            "Agachamento livre pesado - 5x6",
            "Leg press pesado - 5x8",
            "Cadeira extensora pesada - 4x8",
            "Mesa flexora pesada - 4x8",
            "Avan\u00e7o com halteres - 4x10"
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
            "Remada com el\u00e1stico - 4x20",
            "Remada inversa - 3x20",
            "Puxada com tri\u00e2ngulo - 3x15",
            "Burpee com remada - 4x30s"
        ],
        "Resist\u00eancia": [
            "Remada leve - 4x20",
            "Puxada aberta cont\u00ednua - 3x25",
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
    "Gl\u00fateos": {
        "Hipertrofia": [
            "Eleva\u00e7\u00e3o de quadril com barra - 4x10",
            "Agachamento sum\u00f4 - 4x10",
            "Avan\u00e7o com peso - 4x10",
            "Cadeira abdutora - 3x12",
            "Extens\u00e3o de quadril na polia - 3x15"
        ],
        "Emagrecimento": [
            "Glute bridge com peso corporal - 4x20",
            "Agachamento lateral - 4x15",
            "Eleva\u00e7\u00e3o de quadril unilateral - 3x15",
            "Afundo alternado - 3x20",
            "Step up - 3x15"
        ],
        "Resist\u00eancia": [
            "Ponte de gl\u00fateo - 4x20",
            "Agachamento com isometria - 3x30s",
            "Extens\u00e3o com el\u00e1stico - 3x25",
            "Cadeira abdutora leve - 3x20",
            "Afundo com pausa - 3x20"
        ],
        "Ganho de Massa Muscular": [
            "Hip thrust pesado - 5x6",
            "Avan\u00e7o com barra - 4x8",
            "Extens\u00e3o de quadril com carga - 4x8",
            "Cadeira abdutora pesada - 4x10",
            "Agachamento sum\u00f4 com peso - 4x8"
        ]
    }
}



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

# ------------------ Interface Principal ------------------
st.header("Plano de Treino e Dieta Zeus")

aba = st.selectbox("Escolha uma seção", ["Treino", "Dieta da Semana", "Suplementos e Receitas", "Gerar PDF"])

if aba == "Treino":
    grupo = st.selectbox("Grupo muscular", list(treinos.keys()))
    objetivo = st.selectbox("Objetivo do treino", ["Hipertrofia", "Emagrecimento", "Resistência", "Ganho de Massa Muscular"])
    if st.button("Gerar treino"):
        treino = gerar_treino(grupo, objetivo)
        st.subheader("Treino Sugerido:")
        for t in treino:
            st.write("-", t)
        st.session_state["treino"] = treino

elif aba == "Dieta da Semana":
    objetivo_dieta = user[7]
    if st.button("Gerar Dieta da Semana"):
        dieta_dias = dietas_semanais.get(objetivo_dieta, {})
        st.subheader(f"Dieta semanal para: {objetivo_dieta}")
        plano_dieta_semana = []
        for dia, refeicoes in dieta_dias.items():
            st.markdown(f"{dia}")
            for refeicao, descricao, kcal in refeicoes:
                st.write(f"- {refeicao}: {descricao} ({kcal} kcal)")
                plano_dieta_semana.append(f"{dia} - {refeicao}: {descricao} ({kcal} kcal)")
        st.session_state["dieta"] = plano_dieta_semana

elif aba == "Suplementos e Receitas":
    objetivo = user[7]
    st.subheader("Suplementos recomendados:")
    suplementos = dicas_suplementos(objetivo)
    for s in suplementos:
        st.write("-", s)
    st.subheader("Receitas fitness:")
    receitas = receitas_fitness()
    for r in receitas:
        st.write("-", r)
    st.session_state["suplementos"] = suplementos
    st.session_state["receitas"] = receitas

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
