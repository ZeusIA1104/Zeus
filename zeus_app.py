import streamlit as st
from fpdf import FPDF

# Funções auxiliares
def calcular_imc(peso, altura):
    return peso / (altura ** 2)

def gerar_pdf(dieta, treino):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Plano Personalizado Zeus", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt="Treino:", ln=True)
    for item in treino:
        pdf.cell(200, 10, txt=f"- {item}", ln=True)
    pdf.ln(10)
    pdf.cell(200, 10, txt="Dieta:", ln=True)
    for item in dieta:
        pdf.cell(200, 10, txt=f"- {item}", ln=True)

    pdf_path = "/tmp/zeus_plano.pdf"
    pdf.output(pdf_path)
    return pdf_path

# Dados de treinos
treinos_por_objetivo = {
    "Hipertrofia": {
        "Peito": ["Supino reto", "Supino inclinado", "Crucifixo", "Crossover", "Flexão de braço", "Peck deck"],
        "Costas": ["Puxada frontal", "Remada curvada", "Puxada fechada", "Remada baixa", "Levantamento terra"],
        "Pernas": ["Agachamento livre", "Leg press", "Cadeira extensora", "Mesa flexora", "Afundo com halteres"],
    },
    "Emagrecimento": {
        "Full body": ["Jumping jack", "Agachamento com salto", "Burpee", "Mountain climber", "Corrida parada"],
    },
    "Ganho de Massa Muscular": {
        "Bíceps": ["Rosca direta", "Rosca martelo", "Rosca alternada", "Rosca concentrada", "Rosca Scott"],
        "Tríceps": ["Tríceps pulley", "Tríceps testa", "Mergulho entre bancos", "Tríceps corda", "Tríceps francês"],
    }
}

# Dietas por objetivo
dietas_por_objetivo = {
    "Hipertrofia": [
        "Café da manhã: 5 claras, 2 ovos, 1 banana, 40g de aveia (350 kcal)",
        "Almoço: 150g de arroz, 150g de frango, legumes (600 kcal)",
        "Jantar: 200g de carne vermelha, batata doce, salada (550 kcal)"
    ],
    "Emagrecimento": [
        "Café da manhã: 1 fatia de pão integral, 1 ovo, café sem açúcar (150 kcal)",
        "Almoço: 100g de arroz integral, 120g de frango grelhado, salada (400 kcal)",
        "Jantar: Sopa de legumes com frango desfiado (300 kcal)"
    ],
    "Ganho de Massa Muscular": [
        "Café da manhã: Shake com 1 banana, 1 scoop de whey, aveia e leite (400 kcal)",
        "Almoço: 150g arroz, 200g frango, feijão, salada (650 kcal)",
        "Jantar: Omelete com 4 ovos, aveia, 1 fatia pão integral (500 kcal)"
    ]
}

# Streamlit interface
st.title("ZEUS - Inteligência Artificial Fitness")
st.markdown("Monte seu treino e dieta personalizados.")

# Dados do usuário
with st.sidebar:
    st.header("Seus dados")
    genero = st.selectbox("Gênero", ["Masculino", "Feminino", "Outro"])
    peso = st.number_input("Peso (kg)", min_value=30.0, max_value=200.0, step=0.5)
    altura = st.number_input("Altura (m)", min_value=1.0, max_value=2.5, step=0.01)
    objetivo = st.selectbox("Objetivo", list(dietas_por_objetivo.keys()))

# IMC
if peso and altura:
    imc = calcular_imc(peso, altura)
    st.markdown(f"*Seu IMC:* {imc:.2f}")
    if imc < 18.5:
        st.info("Você está abaixo do peso.")
    elif imc < 25:
        st.success("Peso ideal!")
    elif imc < 30:
        st.warning("Sobrepeso.")
    else:
        st.error("Obesidade.")

# Treino
st.header("Plano de Treino")
treino_escolhido = []
if objetivo in treinos_por_objetivo:
    for grupo, exercicios in treinos_por_objetivo[objetivo].items():
        selecionados = st.multiselect(f"{grupo}:", exercicios)
        treino_escolhido.extend(selecionados)
else:
    st.write("Objetivo ainda sem treinos cadastrados.")

# Dieta
st.header("Plano de Dieta")
dieta_escolhida = dietas_por_objetivo[objetivo]
for item in dieta_escolhida:
    st.write(item)

# Suplementos e receitas
st.header("Dicas de Suplementos e Receitas")
if objetivo == "Hipertrofia":
    st.markdown("- Whey protein após o treino")
    st.markdown("- Creatina 3g ao dia")
    st.markdown("- Receita: Panqueca de banana com aveia e ovos")
elif objetivo == "Emagrecimento":
    st.markdown("- Cafeína pré-treino")
    st.markdown("- Chá verde ao longo do dia")
    st.markdown("- Receita: Omelete de legumes com clara de ovo")
else:
    st.markdown("- Albumina à noite")
    st.markdown("- Hipercalórico entre refeições")

# Geração do PDF
if st.button("Gerar PDF com Plano"):
    pdf_path = gerar_pdf(dieta_escolhida, treino_escolhido)
    with open(pdf_path, "rb") as f:
        st.download_button("Baixar PDF", f, file_name="zeus_plano.pdf")
