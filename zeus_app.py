import streamlit as st
import matplotlib.pyplot as plt
from fpdf import FPDF

st.set_page_config(page_title="Zeus - Personal Trainer & Nutrição IA", layout="centered")

# ---------- Funções Auxiliares ----------

def calcular_imc(peso, altura):
    """Calcula o IMC."""
    imc = peso / (altura ** 2)
    return round(imc, 2)

def classificar_imc(imc):
    """Classifica o IMC."""
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
    """Gera um PDF com o conteúdo fornecido."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=titulo, ln=True, align='C')
    pdf.ln(10)
    for linha in conteudo:
        pdf.multi_cell(0, 10, txt=linha)
    pdf_path = titulo.replace(" ", "_") + ".pdf"
    pdf.output(pdf_path)
    return pdf_path

# ---------- Treinos ----------
# Dicionário com várias opções de treino para cada grupo muscular e objetivo
treinos = {
    "Peito": {
        "Hipertrofia": [
            "Supino reto com barra - 4x10",
            "Supino inclinado com halteres - 4x10",
            "Crucifixo reto - 3x12",
            "Crossover - 3x15",
            "Supino declinado - 3x10",
            "Peck deck - 3x12"
        ],
        "Emagrecimento": [
            "Flexões explosivas - 4x15",
            "Supino leve com altas repetições - 4x20",
            "Crucifixo com elástico - 3x20",
            "Crossover contínuo - 3x20",
            "Flexão com apoio - 4x15",
            "Decline push-ups - 3x15"
        ],
        "Resistência": [
            "Flexões padrão - 4x20",
            "Supino reto leve - 3x25",
            "Crucifixo leve com halteres - 3x20",
            "Crossover com isometria - 3x30s",
            "Flexões inclinadas - 4x20",
            "Push-up holds - 3x30s"
        ],
        "Ganho de Massa Muscular": [
            "Supino reto pesado - 5x6",
            "Supino inclinado pesado - 5x6",
            "Crucifixo inclinado - 4x8",
            "Crossover pesado - 4x8",
            "Decline bench press - 4x8",
            "Pec Deck Machine - 4x10"
        ]
    },
    "Costas": {
        "Hipertrofia": [
            "Remada curvada com barra - 4x10",
            "Puxada alta na polia - 4x10",
            "Remada cavalinho - 4x10",
            "Levantamento terra - 4x8",
            "Remada unilateral com halteres - 4x10",
            "Puxada baixa na máquina - 3x12"
        ],
        "Emagrecimento": [
            "Puxada alta leve - 4x15",
            "Remada com elástico - 4x20",
            "Remada inversa - 3x20",
            "Puxada com triângulo - 3x15",
            "Burpee com remada - 4x30s",
            "Remada no TRX - 3x20"
        ],
        "Resistência": [
            "Remada leve 4x20",
            "Puxada aberta contínua - 3x25",
            "Remada serrote com peso leve - 3x20",
            "Remada no banco - 4x20",
            "Puxada com isometria - 3x30s",
            "Circuito de remada com kettlebell leve - 3x20"
        ],
        "Ganho de Massa Muscular": [
            "Barra fixa com peso adicional - 4x6",
            "Remada curvada pesada - 5x6",
            "Remada unilateral pesada - 4x8",
            "Puxada fechada - 4x8",
            "Remada baixa na máquina - 4x10",
            "Levantamento terra pesado - 4x6"
        ]
    },
    "Pernas": {
        "Hipertrofia": [
            "Agachamento livre - 4x10",
            "Leg press - 4x10",
            "Cadeira extensora - 3x12",
            "Mesa flexora - 3x12",
            "Stiff com barra - 4x8",
            "Agachamento sumô - 3x10"
        ],
        "Emagrecimento": [
            "Agachamento com peso corporal - 4x20",
            "Afundo alternado - 4x15",
            "Leg press leve - 4x15",
            "Cadeira extensora leve - 3x20",
            "Step-ups em banco - 3x15",
            "Agachamento pliométrico - 3x15"
        ],
        "Resistência": [
            "Agachamento 4x20",
            "Cadeira extensora leve - 3x20",
            "Mesa flexora leve - 3x20",
            "Afundo estático - 4x20",
            "Polichinelos com agachamento - 3x25",
            "Circuito de pernas de alta repetição"
        ],
        "Ganho de Massa Muscular": [
            "Agachamento livre pesado - 5x6",
            "Leg press pesado - 5x8",
            "Cadeira extensora pesada - 4x8",
            "Mesa flexora pesada - 4x8",
            "Avanço com halteres - 4x10",
            "Hack squat - 4x8"
        ]
    },
    "Braços": {
        "Hipertrofia": [
            "Rosca direta com barra - 4x10",
            "Rosca martelo com halteres - 4x10",
            "Rosca alternada - 4x10",
            "Rosca concentrada - 3x12",
            "Rosca Scott - 3x10",
            "Rosca 21's - 3x7 (cada segmento)"
        ],
        "Emagrecimento": [
            "Rosca com peso leve - 4x15",
            "Tríceps com corda leve - 4x15",
            "Rosca alternada leve - 4x15",
            "Flexão com pegada fechada - 3x15",
            "Extensão de tríceps leve - 3x20",
            "Circuito de braços com elásticos - 3x20"
        ],
        "Resistência": [
            "Rosca 3x20",
            "Tríceps pulley 3x20",
            "Rosca inversa 3x20",
            "Tríceps francês 3x20",
            "Rosca com halteres leves 3x25",
            "Circuito para braços com variantes"
        ],
        "Ganho de Massa Muscular": [
            "Rosca direta pesada - 5x6",
            "Rosca martelo pesada - 5x6",
            "Rosca alternada pesada - 4x8",
            "Rosca concentrada pesada - 4x8",
            "Tríceps corda pesada - 4x8",
            "Mergulho entre bancos - 4x8"
        ]
    },
    "Ombros": {
        "Hipertrofia": [
            "Elevação lateral com halteres - 4x12",
            "Desenvolvimento com barra - 4x10",
            "Elevação frontal - 3x12",
            "Remada alta - 3x12",
            "Desenvolvimento Arnold - 3x10",
            "Crucifixo invertido - 3x15"
        ],
        "Emagrecimento": [
            "Elevação lateral leve - 4x15",
            "Desenvolvimento militar leve - 4x15",
            "Elevação alternada com elástico - 3x20",
            "Circuito de ombros com peso corporal - 3x20",
            "Remada com faixa elástica - 3x20",
            "Flexões com foco nos ombros - 3x15"
        ],
        "Resistência": [
            "Elevação lateral 4x20",
            "Desenvolvimento leve 4x20",
            "Remada alta com peso leve 3x20",
            "Circuito de ombros com variações - 3x25",
            "Elevação frontal 4x20",
            "Exercícios isométricos para ombros 3x30s"
        ],
        "Ganho de Massa Muscular": [
            "Desenvolvimento com halteres pesados - 5x6",
            "Elevação lateral pesada - 4x8",
            "Arnold press pesado - 4x8",
            "Elevação frontal com barra - 4x8",
            "Desenvolvimento militar pesado - 4x6",
            "Face pull com carga - 4x10"
        ]
    },
    "Abdômen": {
        "Hipertrofia": [
            "Abdominal com peso - 4x12",
            "Crunch com bola - 4x15",
            "Elevação de pernas suspenso - 4x12",
            "Prancha dinâmica - 3x1min",
            "Abdominal oblíquo com peso - 3x12",
            "Abdominal na máquina - 3x12"
        ],
        "Emagrecimento": [
            "Abdominal tradicional - 4x20",
            "Prancha frontal - 3x1min",
            "Abdominal inverso - 4x15",
            "Prancha lateral - 3x30s",
            "Abdominal bicicleta - 4x20",
            "Abdominal com torção - 3x15"
        ],
        "Resistência": [
            "Abdominal 4x30",
            "Prancha 4x1min",
            "Abdominal isométrico 3x1min",
            "Abdominal oblíquo contínuo 3x1min",
            "Crunch contínuo 3x1min",
            "Circuito de abdômen com baixa pausa"
        ],
        "Ganho de Massa Muscular": [
            "Abdominal com peso adicional - 5x8",
            "Crunch pesado - 5x10",
            "Abdominal na máquina pesada - 4x8",
            "Elevação de pernas com peso - 4x10",
            "Prancha com carga - 4x30s",
            "Abdominal com bola medicinal - 4x10"
        ]
    }
}

def gerar_treino(grupo, objetivo_treino):
    grupo = grupo.capitalize()
    if grupo in treinos and objetivo_treino in treinos[grupo]:
        return treinos[grupo][objetivo_treino]
    else:
        return ["Nenhum treino encontrado para essa combinação."]

# ---------- Dietas ----------
dietas = {
    "Emagrecimento": {
        "Tradicional": [
            ("Café da manhã", "1 fatia de pão integral, 2 ovos mexidos, 200ml de café sem açúcar", 250),
            ("Almoço", "150g de frango grelhado, 100g de arroz integral, salada", 400),
            ("Jantar", "Sopa de legumes com 100g de carne magra, 1 fruta", 350)
        ],
        "Low Carb": [
            ("Café da manhã", "3 ovos mexidos com espinafre, 1 abacate pequeno", 300),
            ("Almoço", "150g de frango, brócolis no vapor, salada com azeite", 350),
            ("Jantar", "Peixe grelhado (150g), couve-flor cozida, salada", 300)
        ],
        "Vegetariana": [
            ("Café da manhã", "Smoothie de frutas com leite de amêndoas e 1 scoop de proteína vegetal", 280),
            ("Almoço", "150g de tofu grelhado, 100g de quinoa, legumes variados", 350),
            ("Jantar", "Salada grande com grão-de-bico (150g), abacate e verduras", 300)
        ]
    },
    "Hipertrofia": {
        "Tradicional": [
            ("Café da manhã", "3 ovos mexidos, 2 fatias de pão integral, 1 banana", 450),
            ("Almoço", "200g de carne vermelha, 150g de arroz, feijão e legumes", 600),
            ("Jantar", "150g de frango grelhado, 100g de macarrão integral, salada", 500)
        ],
        "Low Carb": [
            ("Café da manhã", "Omelete com 3 ovos, espinafre e queijo cottage", 400),
            ("Almoço", "200g de frango, salada variada com azeite, legumes no vapor", 550),
            ("Jantar", "Peixe grelhado (150g), brócolis e couve-flor", 500)
        ],
        "Vegetariana": [
            ("Café da manhã", "Smoothie de aveia com banana e proteína vegetal", 400),
            ("Almoço", "150g de grão-de-bico, 100g de quinoa, legumes cozidos", 550),
            ("Jantar", "Tofu grelhado (150g), salada colorida e abóbora assada", 500)
        ]
    },
    "Ganho de Massa Muscular": {
        "Tradicional": [
            ("Café da manhã", "4 claras + 2 ovos inteiros, 2 fatias de pão integral", 500),
            ("Almoço", "250g de frango, 150g de arroz, feijão e vegetais", 650),
            ("Jantar", "Omelete de 4 ovos com legumes e 1 batata doce", 600)
        ],
        "Low Carb": [
            ("Café da manhã", "Omelete de 3 ovos com cogumelos e abacate", 450),
            ("Almoço", "200g de salmão, salada verde com azeite", 600),
            ("Jantar", "Carne grelhada (200g) com brócolis e aspargos", 600)
        ],
        "Vegetariana": [
            ("Café da manhã", "Smoothie com proteína vegetal, aveia e frutas", 450),
            ("Almoço", "150g de lentilhas, 100g de quinoa, vegetais variados", 600),
            ("Jantar", "Tofu salteado (200g) com legumes e arroz integral", 600)
        ]
    },
    "Manutenção": {
        "Tradicional": [
            ("Café da manhã", "2 ovos mexidos, 1 fatia de pão integral, fruta", 350),
            ("Almoço", "150g de frango, 100g de arroz, salada", 450),
            ("Jantar", "Sopa leve ou salada com proteína", 350)
        ],
        "Low Carb": [
            ("Café da manhã", "Omelete de 2 ovos com legumes", 300),
            ("Almoço", "Salada grande com 150g de frango", 400),
            ("Jantar", "Peixe grelhado com vegetais", 350)
        ],
        "Vegetariana": [
            ("Café da manhã", "Iogurte com frutas e granola sem açúcar", 350),
            ("Almoço", "Salada com grão-de-bico e vegetais", 400),
            ("Jantar", "Sopa de legumes com tofu", 350)
        ]
    }
}

def montar_dieta(objetivo_dieta, tipo_alim):
    if objetivo_dieta in dietas and tipo_alim in dietas[objetivo_dieta]:
        return dietas[objetivo_dieta][tipo_alim]
    else:
        return []

# ---------- Suplementos e Receitas ----------

def dicas_suplementos(objetivo):
    if objetivo == "Emagrecimento":
        return ["Cafeína", "L-Carnitina", "Chá verde"]
    elif objetivo == "Hipertrofia":
        return ["Whey Protein", "Creatina", "BCAA", "Hipercalórico"]
    elif objetivo == "Ganho de Massa Muscular":
        return ["Whey Protein", "Creatina", "BCAA", "Multivitamínico"]
    else:
        return ["Multivitamínico", "Ômega 3", "Proteína vegetal"]

def receitas_fitness():
    return [
        "Panqueca de banana com aveia",
        "Shake proteico com morango e aveia",
        "Omelete de claras com espinafre",
        "Frango grelhado com legumes",
        "Salada de quinoa com vegetais"
    ]

# ---------- Interface e Geração de PDF ----------

def gerar_pdf(plano_treino, plano_dieta, suplemento, rec):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Plano Zeus - Treino e Dieta", ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="Treino:", ln=True)
    pdf.set_font("Arial", size=11)
    for ex in plano_treino:
        pdf.cell(200, 10, txt=f"- {ex}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="Dieta:", ln=True)
    pdf.set_font("Arial", size=11)
    for refeicao, desc, kcal in plano_dieta:
        pdf.cell(200, 10, txt=f"{refeicao}: {desc} ({kcal} kcal)", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="Suplementos:", ln=True)
    pdf.set_font("Arial", size=11)
    for s in suplemento:
        pdf.cell(200, 10, txt=f"- {s}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="Receitas:", ln=True)
    pdf.set_font("Arial", size=11)
    for r in rec:
        pdf.cell(200, 10, txt=f"- {r}", ln=True)
        
    pdf_path = "plano_zeus.pdf"
    pdf.output(pdf_path)
    return pdf_path

# ---------- Interface Streamlit ----------

st.title("ZEUS - Personal Trainer & Nutrição IA")

# Menu lateral
menu = st.sidebar.selectbox("Selecione a função", ["IMC", "Treino", "Dieta", "Suplementos e Receitas", "Gerar PDF"])

# ----- IMC -----
if menu == "IMC":
    st.header("Calculadora de IMC")
    peso = st.number_input("Peso (kg)", min_value=30.0, max_value=200.0, step=0.5)
    altura = st.number_input("Altura (m)", min_value=1.0, max_value=2.5, step=0.01)
    if st.button("Calcular IMC"):
        imc = calcular_imc(peso, altura)
        st.write(f"Seu IMC é: {imc:.2f}")
        st.write(f"Classificação: {classificar_imc(imc)}")

# ----- Treino -----
elif menu == "Treino":
    st.header("Plano de Treino Personalizado")
    grupo = st.selectbox("Grupo muscular", ["Peito", "Costas", "Pernas", "Braços", "Ombros", "Abdômen"])
    objetivo_treino = st.selectbox("Objetivo do treino", ["Hipertrofia", "Emagrecimento", "Resistência", "Ganho de Massa Muscular"])
    if st.button("Gerar Treino"):
        plano_treino = gerar_treino(grupo, objetivo_treino)
        st.subheader("Treino Sugerido:")
        for ex in plano_treino:
            st.write(f"- {ex}")

# ----- Dieta -----
elif menu == "Dieta":
    st.header("Plano Alimentar Personalizado")
    objetivo_dieta = st.selectbox("Objetivo da dieta", ["Emagrecimento", "Hipertrofia", "Ganho de Massa Muscular", "Manutenção"])
    tipo_alim = st.selectbox("Tipo de alimentação", ["Tradicional", "Low Carb", "Vegetariana", "Outro"])
    peso_dieta = st.number_input("Seu peso (kg) para dieta", min_value=30.0, max_value=200.0, step=0.5)
    if st.button("Gerar Dieta"):
        plano_dieta = montar_dieta(objetivo_dieta, tipo_alim)
        st.subheader("Dieta Sugerida:")
        for refeicao, desc, kcal in plano_dieta:
            st.write(f"*{refeicao}*: {desc} ({kcal} kcal)")
        total_calorias = sum([kcal for _, _, kcal in plano_dieta])
        st.write(f"*Total estimado de calorias:* {total_calorias} kcal")

# ----- Suplementos e Receitas -----
elif menu == "Suplementos e Receitas":
    st.header("Dicas de Suplementos e Receitas Fitness")
    objetivo_nutri = st.selectbox("Objetivo nutricional", ["Emagrecimento", "Hipertrofia", "Ganho de Massa Muscular", "Manutenção"])
    st.subheader("Suplementos Sugeridos:")
    sup = dicas_suplementos(objetivo_nutri)
    for s in sup:
        st.write(f"- {s}")
    st.subheader("Receitas Fitness:")
    rec = receitas_fitness()
    for r in rec:
        st.write(f"- {r}")

# ----- Gerar PDF -----
elif menu == "Gerar PDF":
    st.header("Gerar PDF do Plano Completo")
    st.write("Preencha os dados para gerar o PDF.")
    
    # Se o usuário já gerou planos, pode inserir aqui ou digitar manualmente:
    plano_treino_input = st.text_area("Digite seu plano de treino (uma linha por exercício):")
    plano_dieta_input = st.text_area("Digite seu plano de dieta (uma linha por refeição, com descrição e kcal):")
    suplementos_input = st.text_area("Digite os suplementos sugeridos (uma linha por item):")
    receitas_input = st.text_area("Digite as receitas (uma linha por receita):")
    
    if st.button("Gerar PDF"):
        treino_lista = plano_treino_input.splitlines() if plano_treino_input else ["Nenhum plano de treino fornecido."]
        dieta_lista = plano_dieta_input.splitlines() if plano_dieta_input else ["Nenhum plano de dieta fornecido."]
        sup_lista = suplementos_input.splitlines() if suplementos_input else ["Nenhum suplemento fornecido."]
        rec_lista = receitas_input.splitlines() if receitas_input else ["Nenhuma receita fornecida."]
        
        conteudo_pdf = []
        conteudo_pdf.append("Treino:")
        conteudo_pdf.extend(treino_lista)
        conteudo_pdf.append("")
        conteudo_pdf.append("Dieta:")
        conteudo_pdf.extend(dieta_lista)
        conteudo_pdf.append("")
        conteudo_pdf.append("Suplementos:")
        conteudo_pdf.extend(sup_lista)
        conteudo_pdf.append("")
        conteudo_pdf.append("Receitas:")
        conteudo_pdf.extend(rec_lista)
        
        pdf_path = gerar_pdf("Plano_Completo_Zeus", conteudo_pdf)
        st.success("PDF gerado com sucesso!")
        with open(pdf_path, "rb") as f:
            st.download_button("Baixar PDF", f, file_name="Plano_Completo_Zeus.pdf")
