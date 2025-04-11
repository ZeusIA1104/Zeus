import streamlit as st
from fpdf import FPDF

def calcular_imc(peso, altura):
    imc = peso / (altura ** 2)
    return round(imc, 2)

def gerar_treino(objetivo):
    treinos = {
        "Hipertrofia": [
            "Supino reto - 4x10", "Supino inclinado - 4x10", "Crucifixo - 3x12", "Tríceps pulley - 3x12"
        ],
        "Emagrecimento": [
            "Circuito funcional", "Esteira 20min", "Agachamento com peso corporal - 4x20", "Flexão - 4x15"
        ],
        "Ganho de Massa Muscular": [
            "Agachamento livre - 4x10", "Levantamento terra - 4x8", "Barra fixa - 3x8", "Rosca direta - 3x12"
        ]
    }
    return treinos.get(objetivo, ["Treino não encontrado."])

def gerar_dieta(objetivo):
    dietas = {
        "Emagrecimento": [
            ("Café da manhã", "1 fatia de pão integral, 2 ovos mexidos, 200ml de café sem açúcar", 250),
            ("Almoço", "150g de frango grelhado, 100g de arroz integral, salada", 400),
            ("Jantar", "Sopa de legumes com carne magra, 1 fruta", 350)
        ],
        "Hipertrofia": [
            ("Café da manhã", "3 ovos, 2 fatias de pão integral, 1 banana", 450),
            ("Almoço", "200g de carne vermelha, 150g de arroz, feijão, legumes", 600),
            ("Jantar", "150g de frango, 100g de macarrão integral, legumes", 500)
        ],
        "Ganho de Massa Muscular": [
            ("Café da manhã", "4 claras + 2 ovos inteiros, 1 tapioca com queijo", 500),
            ("Almoço", "250g de frango, batata doce, salada", 650),
            ("Jantar", "Omelete com vegetais e aveia", 500)
        ]
    }
    return dietas.get(objetivo, [])

def gerar_pdf(treino, dieta, objetivo):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(200, 10, txt="Plano Zeus: Treino e Dieta", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=f"Objetivo: {objetivo}", ln=True)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Treino:", ln=True)
    pdf.set_font("Arial", size=11)
    for item in treino:
        pdf.cell(200, 8, txt=f"- {item}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Dieta:", ln=True)
    pdf.set_font("Arial", size=11)
    for refeicao, descricao, kcal in dieta:
        pdf.cell(200, 8, txt=f"{refeicao}: {descricao} ({kcal} kcal)", ln=True)

    pdf.output("plano_zeus.pdf")
    return "plano_zeus.pdf"

# Streamlit UI
st.title("Zeus - Seu Personal Inteligente")

nome = st.text_input("Digite seu nome:")
peso = st.number_input("Digite seu peso (kg):", min_value=30.0, max_value=200.0, step=0.1)
altura = st.number_input("Digite sua altura (m):", min_value=1.0, max_value=2.5, step=0.01)
genero = st.selectbox("Gênero:", ["Masculino", "Feminino", "Outro"])
objetivo = st.selectbox("Objetivo:", ["Hipertrofia", "Emagrecimento", "Ganho de Massa Muscular"])

if st.button("Calcular IMC"):
    imc = calcular_imc(peso, altura)
    st.success(f"Seu IMC é: {imc}")

if st.button("Gerar Plano"):
    treino = gerar_treino(objetivo)
    dieta = gerar_dieta(objetivo)

    st.subheader("Treino sugerido:")
    for t in treino:
        st.write(f"- {t}")
    
    st.subheader("Dieta sugerida:")
    for refeicao, descricao, kcal in dieta:
        st.write(f"{refeicao}: {descricao} ({kcal} kcal)")

    caminho_pdf = gerar_pdf(treino, dieta, objetivo)
    with open(caminho_pdf, "rb") as file:
        st.download_button("Baixar Plano em PDF", file, file_name="plano_zeus.pdf")
