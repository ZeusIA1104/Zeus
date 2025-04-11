import streamlit as st

# --- Função para gerar treino ---
def gerar_treino(grupo, nivel="intermediário", objetivo="hipertrofia"):
    treinos = {
        "Peito": {
            "iniciante": ["Supino reto com barra - 3x10", "Supino inclinado com halteres - 3x10", "Crucifixo reto - 3x12"],
            "intermediário": ["Supino reto com barra - 4x8", "Supino inclinado com halteres - 4x10", "Crucifixo reto - 3x12", "Crossover - 3x15"],
            "avançado": ["Supino reto com barra - 5x5", "Supino inclinado com halteres - 4x8", "Crucifixo inclinado - 4x12", "Crossover - 4x15", "Flexão - 3x falha"]
        },
        "Perna": {
            "iniciante": ["Agachamento livre - 3x10", "Leg Press - 3x10", "Cadeira extensora - 3x12"],
            "intermediário": ["Agachamento livre - 4x10", "Leg Press - 4x12", "Cadeira extensora - 3x12", "Cadeira flexora - 3x15"],
            "avançado": ["Agachamento livre - 5x8", "Leg Press - 5x10", "Cadeira extensora - 4x12", "Cadeira flexora - 4x15", "Avanço com halteres - 3x12"]
        },
        "Costas": {
            "iniciante": ["Puxada frente - 3x10", "Remada baixa - 3x10", "Pullover - 3x12"],
            "intermediário": ["Puxada frente - 4x10", "Remada baixa - 4x10", "Remada unilateral - 3x12", "Pullover - 3x12"],
            "avançado": ["Barra fixa - 4x6", "Remada curvada - 4x10", "Remada unilateral - 4x12", "Pullover - 4x15", "Puxada fechada - 3x12"]
        },
        "Ombro": {
            "iniciante": ["Elevação lateral - 3x12", "Desenvolvimento com halteres - 3x10", "Elevação frontal - 3x12"],
            "intermediário": ["Elevação lateral - 4x12", "Desenvolvimento com barra - 4x10", "Elevação frontal - 4x12", "Crucifixo invertido - 3x15"],
            "avançado": ["Elevação lateral - 5x15", "Desenvolvimento com barra - 4x8", "Crucifixo invertido - 4x12", "Arnold press - 4x10", "Elevação frontal - 4x15"]
        },
        "Bíceps": {
            "iniciante": ["Rosca direta - 3x10", "Rosca martelo - 3x12"],
            "intermediário": ["Rosca direta - 4x10", "Rosca alternada - 4x12", "Rosca concentrada - 3x12"],
            "avançado": ["Rosca direta - 5x10", "Rosca scott - 4x12", "Rosca martelo - 4x12", "Rosca concentrada - 3x15"]
        },
        "Tríceps": {
            "iniciante": ["Tríceps corda - 3x12", "Tríceps testa - 3x10"],
            "intermediário": ["Tríceps corda - 4x12", "Tríceps testa - 4x10", "Mergulho - 3x15"],
            "avançado": ["Tríceps corda - 5x12", "Tríceps testa - 4x10", "Mergulho - 4x15", "Tríceps banco - 4x12"]
        }
    }

    nivel = nivel.lower()
    grupo = grupo.capitalize()

    if grupo in treinos and nivel in treinos[grupo]:
        treino = treinos[grupo][nivel]
        return "\\n".join(treino)
    else:
        return "Não foi possível gerar o treino com essas opções."

# --- Função para gerar dieta ---
def gerar_dieta(objetivo):
    dietas = {
        "Emagrecimento": [
            "Café da manhã: Omelete com 2 ovos, 1 fatia de pão integral, 1 xícara de café sem açúcar",
            "Lanche da manhã: 1 fruta (maçã ou banana)",
            "Almoço: 100g de frango grelhado, 2 colheres de arroz integral, salada verde à vontade",
            "Lanche da tarde: Iogurte natural sem açúcar + 1 colher de chia",
            "Jantar: Sopa de legumes + 1 ovo cozido"
        ],
        "Hipertrofia": [
            "Café da manhã: 3 ovos mexidos, 2 fatias de pão integral, 1 copo de vitamina de banana com whey",
            "Lanche da manhã: Mix de castanhas + 1 fruta",
            "Almoço: 150g de carne vermelha, 3 colheres de arroz, feijão e legumes",
            "Lanche da tarde: Sanduíche integral com frango desfiado",
            "Jantar: 150g de peixe, batata doce e brócolis"
        ],
        "Ganho de Massa": [
            "Café da manhã: Aveia com leite, banana e whey protein",
            "Lanche da manhã: 1 sanduíche natural + suco natural",
            "Almoço: 200g de frango, arroz, feijão e abóbora",
            "Lanche da tarde: Shake de whey com aveia e pasta de amendoim",
            "Jantar: 150g de carne magra, purê de batata e salada"
        ]
    }

    objetivo = objetivo.capitalize()
    if objetivo in dietas:
        return "\\n".join(dietas[objetivo])
    else:
        return "Objetivo não encontrado."

# --- Interface principal ---
st.set_page_config(page_title="Zeus - IA Fitness", layout="centered")
st.title("Zeus - Seu treinador pessoal")

aba = st.sidebar.selectbox("Escolha uma função", ["Treino", "Dieta"])

if aba == "Treino":
    st.markdown("### Monte seu treino personalizado")
    grupo = st.selectbox("Escolha o grupo muscular", ["Peito", "Perna", "Costas", "Ombro", "Bíceps", "Tríceps"])
    nivel = st.selectbox("Seu nível", ["Iniciante", "Intermediário", "Avançado"])
    objetivo = st.selectbox("Objetivo", ["Definição", "Hipertrofia", "Resistência"])

    if st.button("Gerar treino"):
        treino = gerar_treino(grupo, nivel, objetivo)
        st.text(treino)

elif aba == "Dieta":
    st.markdown("### Monte sua dieta personalizada")
    objetivo_dieta = st.selectbox("Qual seu objetivo?", ["Emagrecimento", "Hipertrofia", "Ganho de Massa"])

    if st.button("Gerar dieta"):
        dieta = gerar_dieta(objetivo_dieta)
        st.text(dieta)
