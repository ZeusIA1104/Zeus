import streamlit as st
import sqlite3
import hashlib
from fpdf import FPDF
import requests
import unicodedata

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

def normalizar_nome(nome):
    return ''.join(
        c for c in unicodedata.normalize('NFD', nome.lower())
        if unicodedata.category(c) != 'Mn'
    )

def verificar_pagamento_por_nome(nome_usuario):
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    url = "https://api.mercadopago.com/v1/payments/search?sort=date_created&criteria=desc"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        nome_normalizado = normalizar_nome(nome_usuario)
        results = response.json().get("results", [])
        for pagamento in results:
            payer_name = pagamento.get("payer", {}).get("first_name", "")
            status = pagamento.get("status", "")
            if status == "approved":
                payer_normalizado = normalizar_nome(payer_name)
                if payer_normalizado in nome_normalizado or nome_normalizado in payer_normalizado:
                    return True
    return False

def calcular_imc(peso, altura):
    return round(peso / (altura ** 2), 2)

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
                st.info("Após o pagamento, clique no botão abaixo para verificar.")
                if st.button("Verificar Pagamento"):
                    if verificar_pagamento_por_nome(nome):
                        atualizar_status_pagamento(email, "aprovado")
                        st.success("Pagamento confirmado! Faça login para acessar o Zeus.")
                    else:
                        st.warning("Pagamento ainda não identificado.")
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
                if st.button("Verificar Pagamento"):
                    if verificar_pagamento_por_nome(nome_usuario):
                        atualizar_status_pagamento(email, "aprovado")
                        st.success("Pagamento confirmado! Recarregando...")
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

    if email_user == ADMIN_EMAIL:"guibarcellosdaniel6@gmail.com"
        st.markdown("---")
        st.subheader("Painel do Administrador - Liberar Acesso Manual")
        nome_alvo = st.text_input("Nome do usuário a liberar:")
        if st.button("Liberar acesso manualmente"):
            try:
                conn = sqlite3.connect("zeus_usuarios.db")
                cursor = conn.cursor()
                cursor.execute("UPDATE usuarios SET status_pagamento='aprovado' WHERE nome LIKE ?", (f"%{nome_alvo}%",))
                conn.commit()
                conn.close()
                st.success(f"Acesso de '{nome_alvo}' liberado com sucesso!")
            except Exception as e:
                st.error(f"Erro ao liberar acesso: {e}")
# === TREINOS POR GRUPO ===
treinos = {
    "Peito": {
        "Hipertrofia": ["Supino reto", "Supino inclinado", "Crucifixo", "Crossover", "Flexão com carga"],
        "Emagrecimento": ["Flexão", "Supino leve", "Pullover leve", "Crossover leve", "Peck deck leve"],
        "Manutenção": ["Supino reto", "Crucifixo", "Peck deck", "Flexão", "Crossover"]
    },
    "Costas": {
        "Hipertrofia": ["Remada curvada", "Puxada frontal", "Levantamento terra", "Remada baixa", "Puxada fechada"],
        "Emagrecimento": ["Puxada leve", "Remada unilateral", "Pull down", "Crucifixo invertido", "Barra assistida"],
        "Manutenção": ["Remada baixa", "Puxada frente", "Barra fixa", "Remada curvada", "Encolhimento"]
    }
}

def gerar_treino(grupo, objetivo):
    return treinos.get(grupo, {}).get(objetivo, ["Treino não encontrado."])

# === DIETAS SEMANAIS ===
dietas_semanais = {
    "Hipertrofia": {
        "Segunda-feira": [("Café da manhã", "Ovos e aveia", 350), ("Almoço", "Arroz, frango e feijão", 700), ("Jantar", "Batata doce e carne", 600)],
        "Terça-feira": [("Café da manhã", "Pão integral com ovos", 320), ("Almoço", "Macarrão com carne moída", 680), ("Jantar", "Frango grelhado e purê", 550)]
    },
    "Emagrecimento": {
        "Segunda-feira": [("Café da manhã", "Iogurte com chia", 200), ("Almoço", "Salada com frango", 400), ("Jantar", "Sopa de legumes", 300)],
        "Terça-feira": [("Café da manhã", "Vitamina de banana", 250), ("Almoço", "Peixe grelhado e legumes", 420), ("Jantar", "Salada de atum", 320)]
    }
}

def dicas_suplementos(objetivo):
    if objetivo == "Hipertrofia":
        return ["Whey Protein", "Creatina", "BCAA", "Albumina"]
    elif objetivo == "Emagrecimento":
        return ["Termogênico", "L-Carnitina", "Chá verde", "Cafeína"]
    else:
        return ["Multivitamínico", "Ômega 3", "Vitamina D"]

def receitas_fitness():
    return ["Panqueca de banana", "Omelete de claras", "Shake de whey com aveia", "Frango com batata doce"]

# === MENU PRINCIPAL ===
if st.session_state["usuario"]:
    user = st.session_state["usuario"]
    nome_usuario = user[1]
    email_user = user[2]
    objetivo_user = user[7]
    status_pag = buscar_status_pagamento(email_user)

    if status_pag != "aprovado":
        st.warning("Pagamento não confirmado.")
        link = gerar_link_pagamento(nome_usuario, email_user)
        if link:
            st.markdown(f"[Clique aqui para pagar R$49,90]({link})", unsafe_allow_html=True)
        if st.button("Verificar Pagamento"):
            if verificar_pagamento_por_nome(nome_usuario):
                atualizar_status_pagamento(email_user, "aprovado")
                st.success("Pagamento confirmado. Recarregando...")
                st.experimental_rerun()
            else:
                st.warning("Pagamento ainda não identificado.")
        st.stop()

    st.subheader(f"Bem-vindo ao Zeus, {nome_usuario.split()[0]}!")
    aba = st.selectbox("Escolha uma seção", ["Treino", "Dieta da Semana", "Suplementos e Receitas", "Gerar PDF"])

    if aba == "Treino":
        grupo = st.selectbox("Grupo muscular", list(treinos.keys()))
        if st.button("Gerar Treino"):
            treino = gerar_treino(grupo, objetivo_user)
            st.subheader(f"Treino para {grupo} - {objetivo_user}")
            for ex in treino:
                st.write("- ", ex)
            st.session_state["treino"] = treino

    elif aba == "Dieta da Semana":
        if st.button("Gerar Dieta da Semana"):
            dieta_dias = dietas_semanais.get(objetivo_user, {})
            st.subheader(f"Dieta semanal - {objetivo_user}")
            plano_dieta_semana = []
            for dia, refeicoes in dieta_dias.items():
                st.markdown(f"*{dia}*")
                for refeicao, descricao, kcal in refeicoes:
                    st.write(f"- {refeicao}: {descricao} ({kcal} kcal)")
                    plano_dieta_semana.append(f"{dia} - {refeicao}: {descricao} ({kcal} kcal)")
            st.session_state["dieta"] = plano_dieta_semana

    elif aba == "Suplementos e Receitas":
        st.subheader("Suplementos recomendados:")
        for s in dicas_suplementos(objetivo_user):
            st.write("- ", s)
        st.subheader("Receitas fitness:")
        for r in receitas_fitness():
            st.write("- ", r)

    elif aba == "Gerar PDF":
        conteudo_pdf = []
        if "treino" in st.session_state:
            conteudo_pdf.append("Plano de Treino:")
            conteudo_pdf.extend(st.session_state["treino"])
        if "dieta" in st.session_state:
            conteudo_pdf.append("Plano de Dieta:")
            conteudo_pdf.extend(st.session_state["dieta"])
        if conteudo_pdf:
            caminho = gerar_pdf(f"Plano Zeus - {nome_usuario}", conteudo_pdf)
            with open(caminho, "rb") as f:
                st.download_button("Baixar PDF do Plano", f, file_name=caminho)
        else:
            st.info("Gere treino ou dieta antes de exportar.")
