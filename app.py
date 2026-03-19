import streamlit as st
import os
import requests
import sys
from dotenv import load_dotenv

# Importações da nova SDK oficial
from google import genai
from google.genai import types

# Importar o Motor Determinístico de Laudos (RF03)
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from skills.report_skill import gerar_laudo_oficial

# ==========================================
# 1. Configuração Visual da Página
# ==========================================
st.set_page_config(page_title="AgroRisk Engine", page_icon="🌾", layout="centered")
st.title("🌾 AgroRisk Engine")
st.markdown("**Motor Agentic de Análise de Crédito Rural e Compliance**")
st.divider()

# ==========================================
# 2. Configuração de Ambiente e Chave API
# ==========================================
load_dotenv()
CHAVE_API = os.getenv("GEMINI_API_KEY")

if not CHAVE_API:
    st.error("❌ ERRO: GEMINI_API_KEY não encontrada no arquivo .env")
    st.stop()

# ==========================================
# 3. Ferramentas (Functions Calling)
# ==========================================
def consultar_zarc(municipio_ibge: int, cultura: str, tipo_solo: int) -> dict:
    """Consulta as regras do ZARC no banco de dados para verificar a elegibilidade agronômica de plantio."""
    url = "http://127.0.0.1:8000/api/v1/elegibilidade/zarc"
    payload = {"municipio_ibge": municipio_ibge, "cultura": cultura.upper(), "tipo_solo": tipo_solo}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "ERRO_API", "auditoria": str(e)}

def consultar_embargo_esg(documento: str, car: str) -> dict:
    """Consulta a blacklist de Fraude e Compliance ESG (IBAMA, MTE, Terras Indígenas)."""
    url = "http://127.0.0.1:8000/api/v1/compliance/esg"
    payload = {"documento": documento, "car": car}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "ERRO_API", "auditoria": str(e)}

def consultar_risco_climatico(municipio_ibge: int) -> dict:
    """Avalia a favorabilidade do Clima atual e índice de chuvas no município para permitir ou não plantio."""
    url = f"http://127.0.0.1:8000/api/v1/clima/risco/{municipio_ibge}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "ERRO_API", "auditoria": str(e)}

# ==========================================
# 4. Inicialização do Agente (Session State)
# ==========================================
instrucao_sistema = (
    "Você é o assistente do AgroRisk, um especialista em crédito rural. "
    "Sua função é ajudar produtores a verificar a elegibilidade de crédito baseada no ZARC. "
    "SEMPRE use a ferramenta consultar_zarc para checar o banco de dados antes de responder. "
    "Nunca invente status de elegibilidade. O IBGE de Goiânia é 5208707.\n\n"
    "REGRAS DE COMUNICAÇÃO (MUITO IMPORTANTE):\n"
    "1. Ao responder, NUNCA mencione o número do solo (ex: 'tipo 13' ou 'tipo 3').\n"
    "2. Traduza o número fornecido pelo produtor para o nome agronômico oficial:\n"
    "   - Se ele falar 1, 11 ou 12 -> Diga 'Solo Arenoso'.\n"
    "   - Se ele falar 2, 13 ou 14 -> Diga 'Solo de Textura Média'.\n"
    "   - Se ele falar 3, 15 ou 16 -> Diga 'Solo Argiloso'.\n\n"
    "REGRAS DE COMPLIANCE (CRÍTICO):\n"
    "Para aprovar qualquer crédito, você DEVE obrigatoriamente executar DUAS verificações:\n"
    "1) A viabilidade agronômica (usando consultar_zarc)\n"
    "E 2) A checagem de compliance ambiental (usando consultar_embargo_esg).\n"
    "Se o produtor não fornecer o CPF ou o número do CAR, VOCÊ DEVE PERGUNTAR antes de dar a resposta final.\n"
    "Se o compliance retornar NEGADO_COMPLIANCE, o crédito está sumariamente cancelado, não importa o ZARC.\n\n"
    "REGRAS DE CLIMA (OBRIGATÓRIO):\n"
    "Sempre consulte o Risco Climático (Ferramenta 3).\n"
    "Você DEVE, SEM EXCEÇÃO, falar sobre o clima na sua resposta ao produtor:\n"
    "- Se retornar CLIMA_FAVORAVEL: Diga explicitamente que a umidade do solo está adequada e o clima é favorável.\n"
    "- Se retornar ALERTA_CLIMATICO: Alerte sobre o risco de seca.\n"
    "- Se retornar ERRO_COORDENADAS: Avise que não foi possível verificar o clima da região.\n\n"
    "REGRAS DE LAUDO (OBRIGATÓRIO):\n"
    "Sempre que você finalizar a análise de um cliente (seja aprovando ou negando), VOCÊ DEVE OBRIGATORIAMENTE chamar "
    "a ferramenta gerar_laudo_oficial passando o resumo de todos os dados e a decisão final. "
    "Avise ao produtor que o laudo oficial foi gerado e salvo no sistema da instituição financeira."
)

if "chat_session" not in st.session_state:
    client = genai.Client(api_key=CHAVE_API)
    st.session_state.chat_session = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=instrucao_sistema,
            tools=[consultar_zarc, consultar_embargo_esg, consultar_risco_climatico, gerar_laudo_oficial],
            temperature=0.0
        )
    )

if "messages" not in st.session_state:
    st.session_state.messages = []
    # Mensagem inicial de boas-vindas do assistente
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "Olá! Sou o assistente do AgroRisk Engine. Para simularmos seu crédito, me informe sua cultura, município e tipo de solo."
    })

# ==========================================
# 5. Renderizar o Histórico na Tela
# ==========================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ==========================================
# 6. Caixa de Texto e Processamento
# ==========================================
if prompt := st.chat_input("Digite sua solicitação aqui..."):
    # 6.1. Mostrar e salvar a mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 6.2. Processar a resposta do Agente (com Spinner visual)
    with st.chat_message("assistant"):
        with st.spinner("Consultando motores de ZARC, Compliance e Clima..."):
            try:
                resposta = st.session_state.chat_session.send_message(prompt)
                st.markdown(resposta.text)
                st.session_state.messages.append({"role": "assistant", "content": resposta.text})
            except Exception as e:
                erro_msg = f"❌ Erro de comunicação com a API: {e}"
                st.error(erro_msg)
                st.session_state.messages.append({"role": "assistant", "content": erro_msg})