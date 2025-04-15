import streamlit as st
import sqlite3
import hashlib
import requests
import json
from fpdf import FPDF

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


# ---------- CÃLCULO DE IMC ----------
def calcular_imc(peso, altura):
    altura_m = altura / 100
    imc = peso / (altura_m ** 2)
    if imc < 18.5:
        status = "Abaixo do peso"
    elif imc < 24.9:
        status = "Peso normal"
    elif imc < 29.9:
        status = "Sobrepeso"
    else:
        status = "Obesidade"
    return round(imc, 2), status

# ---------- GERAÃÃO DE PDF ----------
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Plano Zeus - Treino e Dieta', ln=True, align='C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, ln=True, align='L')
        self.ln(5)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 10, body)
        self.ln()

    def add_section(self, title, body):
        self.chapter_title(title)
        self.chapter_body(body)

def gerar_pdf(treino, dieta):
    pdf = PDF()
    pdf.add_page()
    pdf.add_section("Treino", treino)
    pdf.add_section("Dieta", dieta)
    caminho = "/mnt/data/plano_zeus.pdf"
    pdf.output(caminho)
    return caminho


# ---------- TREINOS COMPLETOS ----------
treinos = {
    "Peito": {
        "Hipertrofia": ["Supino reto", "Supino inclinado", "Crucifixo", "Crossover", "FlexÃ£o com peso"],
        "DefiniÃ§Ã£o": ["FlexÃ£o explosiva", "Crossover leve", "Supino com halteres", "Crucifixo inclinado", "FlexÃ£o no solo"],
        "ResistÃªncia": ["FlexÃ£o 4x20", "Peck deck leve", "Supino reto leve", "FlexÃ£o com pausa", "Pullover"]
    },
    "Costas": {
        "Hipertrofia": ["Barra fixa", "Remada curvada", "Puxada frontal", "Remada unilateral", "Levantamento terra"],
        "DefiniÃ§Ã£o": ["Puxada aberta", "Remada baixa", "Barra com pegada neutra", "Pullover mÃ¡quina", "Remada com elÃ¡stico"],
        "ResistÃªncia": ["Remada leve", "Barra assistida", "Puxada com elÃ¡stico", "Remada unilateral leve", "Pulldown"]
    },
    "Pernas": {
        "Hipertrofia": ["Agachamento livre", "Leg press", "Cadeira extensora", "Cadeira flexora", "Afundo com halteres"],
        "DefiniÃ§Ã£o": ["Agachamento com peso corporal", "Leg leve", "Afundo alternado", "Flexora leve", "Stiff leve"],
        "ResistÃªncia": ["Corrida leve", "Agachamento 4x20", "AvanÃ§o contÃ­nuo", "Extensora leve", "Subida em banco"]
    },
    "Ombro": {
        "Hipertrofia": ["Desenvolvimento com barra", "ElevaÃ§Ã£o lateral", "ElevaÃ§Ã£o frontal", "Remada alta", "Desenvolvimento Arnold"],
        "DefiniÃ§Ã£o": ["ElevaÃ§Ã£o lateral leve", "Desenvolvimento com halteres", "ElevaÃ§Ã£o frontal leve", "Crucifixo inverso", "Facepull"],
        "ResistÃªncia": ["Circuito ombro leve", "ElevaÃ§Ãµes 4x20", "Desenvolvimento leve", "Puxada frontal", "RotaÃ§Ã£o externa"]
    },
    "BÃ­ceps": {
        "Hipertrofia": ["Rosca direta", "Rosca alternada", "Rosca concentrada", "Rosca 21", "Rosca martelo"],
        "DefiniÃ§Ã£o": ["Rosca com elÃ¡stico", "Rosca leve 4x20", "Rosca concentrada", "Rosca direta leve", "Rosca inversa"],
        "ResistÃªncia": ["Rosca direta 4x20", "Rosca martelo leve", "Circuito bÃ­ceps", "Rosca alternada leve", "Rosca em pÃ©"]
    },
    "TrÃ­ceps": {
        "Hipertrofia": ["TrÃ­ceps testa", "Mergulho entre bancos", "TrÃ­ceps pulley", "TrÃ­ceps coice", "TrÃ­ceps francÃªs"],
        "DefiniÃ§Ã£o": ["TrÃ­ceps com corda", "Pulley leve", "TrÃ­ceps banco", "Coice leve", "ExtensÃ£o acima da cabeÃ§a"],
        "ResistÃªncia": ["TrÃ­ceps no banco 4x20", "Pulley com elÃ¡stico", "FlexÃ£o de trÃ­ceps", "ExtensÃ£o leve", "Mergulho assistido"]
    },
    "GlÃºteos": {
        "Hipertrofia": ["Agachamento sumÃ´", "ElevaÃ§Ã£o pÃ©lvica com peso", "AvanÃ§o com passada longa", "Cadeira abdutora", "Stiff com halteres"],
        "DefiniÃ§Ã£o": ["ElevaÃ§Ã£o pÃ©lvica", "Abdutora leve", "Agachamento sumÃ´ leve", "AvanÃ§o leve", "ExtensÃ£o quadril"],
        "ResistÃªncia": ["GlÃºteo 4x20", "Abdutora rÃ¡pida", "Passada no step", "ExtensÃ£o leve", "Circuito glÃºteo"]
    },
    "Panturrilha": {
        "Hipertrofia": ["GÃªmeos sentado com carga", "GÃªmeos em pÃ© com barra", "ElevaÃ§Ã£o unilateral", "GÃªmeos no leg press", "Pliometria com peso"],
        "DefiniÃ§Ã£o": ["GÃªmeos sem peso", "ElevaÃ§Ã£o rÃ¡pida", "Saltos verticais", "GÃªmeos sentado leve", "Pliometria leve"],
        "ResistÃªncia": ["ElevaÃ§Ã£o 4x25", "Subida em degrau", "Corrida leve", "GÃªmeos leve", "Circuito panturrilha"]
    },
    "Casa": {
        "Emagrecimento": ["Polichinelo", "Corrida no lugar", "Agachamento", "FlexÃ£o", "Abdominal"],
        "Hipertrofia": ["FlexÃ£o com pÃ©s elevados", "Afundo", "Abdominal com peso", "Agachamento unilateral", "Prancha com braÃ§o elevado"],
        "ManutenÃ§Ã£o": ["Agachamento livre", "FlexÃ£o leve", "Abdominal simples", "Corrida leve", "Prancha"],
        "ResistÃªncia": ["Circuito funcional", "Subida em escada", "Prancha longa", "Saltos com agachamento", "Mountain climber"]
    }
}


# ---------- DIETAS POR OBJETIVO E DIA DA SEMANA ----------
dietas = {
    "Emagrecimento": {
        "Segunda": ["CafÃ©: 2 ovos + chÃ¡ verde", "AlmoÃ§o: frango grelhado + salada", "Lanche: maÃ§Ã£", "Jantar: sopa de legumes"],
        "TerÃ§a": ["CafÃ©: iogurte + chia", "AlmoÃ§o: peixe + legumes no vapor", "Lanche: castanhas", "Jantar: omelete"],
        "Quarta": ["CafÃ©: vitamina com banana e aveia", "AlmoÃ§o: peito de frango + arroz integral + salada", "Lanche: iogurte", "Jantar: salada + ovo cozido"],
        "Quinta": ["CafÃ©: ovos mexidos + cafÃ© sem aÃ§Ãºcar", "AlmoÃ§o: carne magra + purÃª de abÃ³bora", "Lanche: cenoura palito", "Jantar: sopa leve"],
        "Sexta": ["CafÃ©: pÃ£o integral + queijo branco", "AlmoÃ§o: filÃ© de peixe + arroz integral + legumes", "Lanche: maÃ§Ã£", "Jantar: salada de atum"]
    },
    "Hipertrofia": {
        "Segunda": ["CafÃ©: ovos mexidos + aveia com banana", "AlmoÃ§o: arroz + feijÃ£o + bife + salada", "Lanche: shake de whey", "Jantar: macarrÃ£o integral + frango"],
        "TerÃ§a": ["CafÃ©: pÃ£o integral + ovos", "AlmoÃ§o: arroz integral + frango + legumes", "Lanche: batata doce + ovo", "Jantar: omelete + arroz"],
        "Quarta": ["CafÃ©: tapioca com ovo", "AlmoÃ§o: arroz + carne moÃ­da + feijÃ£o", "Lanche: banana + pasta de amendoim", "Jantar: panqueca de frango"],
        "Quinta": ["CafÃ©: ovos + batata doce", "AlmoÃ§o: arroz + peito de frango + salada", "Lanche: shake com whey e aveia", "Jantar: omelete com queijo"],
        "Sexta": ["CafÃ©: pÃ£o integral + queijo + cafÃ©", "AlmoÃ§o: arroz integral + carne vermelha + legumes", "Lanche: granola com iogurte", "Jantar: wrap de frango"]
    },
    "ManutenÃ§Ã£o": {
        "Segunda": ["CafÃ©: cafÃ© com leite + pÃ£o integral", "AlmoÃ§o: arroz + frango + salada", "Lanche: iogurte + frutas", "Jantar: omelete com legumes"],
        "TerÃ§a": ["CafÃ©: vitamina de frutas", "AlmoÃ§o: arroz integral + carne + legumes", "Lanche: barra de cereal", "Jantar: sopa leve"],
        "Quarta": ["CafÃ©: ovos + cafÃ© preto", "AlmoÃ§o: feijÃ£o + arroz + bife", "Lanche: frutas", "Jantar: salada + pÃ£o integral"],
        "Quinta": ["CafÃ©: pÃ£o integral + queijo branco", "AlmoÃ§o: arroz + peixe + salada", "Lanche: castanhas", "Jantar: sopa de abÃ³bora"],
        "Sexta": ["CafÃ©: leite com achocolatado + frutas", "AlmoÃ§o: arroz + frango grelhado + legumes", "Lanche: suco natural", "Jantar: omelete"]
    },
    "ResistÃªncia": {
        "Segunda": ["CafÃ©: banana + aveia + mel", "AlmoÃ§o: arroz + carne + salada", "Lanche: suco + barra de cereal", "Jantar: panqueca de legumes"],
        "TerÃ§a": ["CafÃ©: shake com frutas e whey", "AlmoÃ§o: batata doce + frango + legumes", "Lanche: iogurte proteico", "Jantar: arroz + ovo + salada"],
        "Quarta": ["CafÃ©: pÃ£o integral + ovo mexido", "AlmoÃ§o: arroz + peixe + legumes", "Lanche: banana + castanhas", "Jantar: sopa de legumes"],
        "Quinta": ["CafÃ©: cafÃ© preto + banana + aveia", "AlmoÃ§o: arroz integral + frango + brÃ³colis", "Lanche: barra energÃ©tica", "Jantar: salada com ovos"],
        "Sexta": ["CafÃ©: ovos mexidos + pÃ£o integral", "AlmoÃ§o: arroz + carne + legumes cozidos", "Lanche: frutas + mel", "Jantar: omelete + salada"]
    }
}


# ---------- TELA PRINCIPAL ESTILIZADA COM PDF ----------
def tela_principal(username):
    st.markdown("<h1 style='color:#00BFFF;'>ZEUS - Seu Personal Trainer Virtual</h1>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/2345/2345337.png", width=100)
    with col2:
        st.markdown("<h3 style='color:#00BFFF;'>Bem-vindo ao seu painel de treinos e dietas</h3>", unsafe_allow_html=True)

    menu = ["IMC", "Treinos", "Dietas", "Suplementos", "Receitas", "Gerar PDF"]
    escolha = st.sidebar.radio("Menu", menu)

    if escolha == "IMC":
        st.subheader("Calcular IMC")
        peso = st.number_input("Digite seu peso (kg):", 0.0, 500.0, step=0.1)
        altura = st.number_input("Digite sua altura (cm):", 0.0, 250.0, step=0.1)
        if st.button("Calcular IMC"):
            imc, status = calcular_imc(peso, altura)
            st.success(f"Seu IMC Ã© {imc} ({status})")

    elif escolha == "Treinos":
        st.header("Treinos por Grupo Muscular e Objetivo")
        grupo = st.selectbox("Grupo muscular", list(treinos.keys()))
        objetivo = st.selectbox("Objetivo", list(treinos[grupo].keys()))
        st.markdown(f"<b>Treino para {grupo} - {objetivo}:</b>", unsafe_allow_html=True)
        treino_selecionado = "\n".join(treinos[grupo][objetivo])
        for ex in treinos[grupo][objetivo]:
            st.write(f"- {ex}")
        st.session_state['treino_pdf'] = treino_selecionado

    elif escolha == "Dietas":
        st.header("Dietas Semanais Personalizadas")
        objetivo_dieta = st.selectbox("Objetivo da dieta", list(dietas.keys()))
        dia = st.selectbox("Dia da semana", list(dietas[objetivo_dieta].keys()))
        st.markdown(f"<b>Dieta de {objetivo_dieta} para {dia}:</b>", unsafe_allow_html=True)
        dieta_selecionada = "\n".join(dietas[objetivo_dieta][dia])
        for item in dietas[objetivo_dieta][dia]:
            st.write(f"- {item}")
        st.session_state['dieta_pdf'] = dieta_selecionada

    elif escolha == "Suplementos":
        st.header("SugestÃµes de Suplementos")
        st.write("- Whey Protein
- Creatina
- CafeÃ­na
- MultivitamÃ­nico")

    elif escolha == "Receitas":
        st.header("Receitas Fitness")
        st.write("- Panqueca de aveia
- Frango grelhado com legumes
- Shake proteico com banana")

    elif escolha == "Gerar PDF":
        st.subheader("Gerar PDF com plano atual")
        if 'treino_pdf' in st.session_state and 'dieta_pdf' in st.session_state:
            if st.button("Gerar PDF"):
                pdf_path = gerar_pdf(st.session_state['treino_pdf'], st.session_state['dieta_pdf'])
                st.success("PDF gerado com sucesso!")
                st.markdown(f"[Clique aqui para baixar o PDF]({pdf_path})", unsafe_allow_html=True)
        else:
            st.warning("Selecione um treino e uma dieta antes de gerar o PDF.")
