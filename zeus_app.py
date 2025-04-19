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
                st.rerun()
        else:
            st.error("Email ou senha incorretos.")

# === PAINEL DO ADMIN PARA LIBERAR ACESSO MANUAL ===
if st.session_state["usuario"] or email == ADMIN_EMAIL:
    email_user = (
        st.session_state["usuario"][2]
        if st.session_state["usuario"]
        else ADMIN_EMAIL
    )

    if email_user == ADMIN_EMAIL:
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
