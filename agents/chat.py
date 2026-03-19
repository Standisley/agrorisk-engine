import os
import requests
import sys
from dotenv import load_dotenv

# Importações da nova SDK oficial
from google import genai
from google.genai import types

# Importar o Motor Determinístico de Laudos (RF03)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from skills.report_skill import gerar_laudo_oficial

# 1. Carregar variáveis de ambiente
load_dotenv()
CHAVE_API = os.getenv("GEMINI_API_KEY")

if not CHAVE_API:
    print("❌ ERRO: GEMINI_API_KEY não encontrada no arquivo .env")
    exit()

# Instanciar o novo cliente
client = genai.Client(api_key=CHAVE_API)

# 2. A Ferramenta (A ponte com a nossa API)
def consultar_zarc(municipio_ibge: int, cultura: str, tipo_solo: int) -> dict:
    """
    Consulta as regras do ZARC no banco de dados para verificar a elegibilidade agronômica de plantio.
    """
    url = "http://127.0.0.1:8000/api/v1/elegibilidade/zarc"
    payload = {
        "municipio_ibge": municipio_ibge,
        "cultura": cultura.upper(),
        "tipo_solo": tipo_solo
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "ERRO_API", "auditoria": str(e)}

def consultar_embargo_esg(documento: str, car: str) -> dict:
    """
    Consulta a blacklist de Fraude e Compliance ESG (IBAMA, MTE, Terras Indígenas).
    """
    url = "http://127.0.0.1:8000/api/v1/compliance/esg"
    payload = {
        "documento": documento,
        "car": car
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "ERRO_API", "auditoria": str(e)}

def consultar_risco_climatico(municipio_ibge: int) -> dict:
    """
    Avalia a favorabilidade do Clima atual e índice de chuvas no município para permitir ou não plantio.
    """
    url = f"http://127.0.0.1:8000/api/v1/clima/risco/{municipio_ibge}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "ERRO_API", "auditoria": str(e)}

# 3. Instruções e Configuração do Agente
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
    "REGRAS DE CLIMA:\n"
    "Sempre que for analisar um crédito, você deve consultar o ZARC, o ESG e OBRIGATORIAMENTE o Risco Climático (Ferramenta 3). "
    "Se houver ALERTA_CLIMATICO, você não precisa negar o crédito (se as outras passarem), mas DEVE alertar o "
    "produtor sobre o risco de seca e incluir uma cláusula de advertência climática no laudo final.\n\n"
    "REGRAS DE LAUDO (OBRIGATÓRIO):\n"
    "Sempre que você finalizar a análise de um cliente (seja aprovando ou negando), VOCÊ DEVE OBRIGATORIAMENTE chamar "
    "a ferramenta gerar_laudo_oficial passando o resumo de todos os dados e a decisão final. "
    "Avise ao produtor que o laudo oficial foi gerado e salvo no sistema da instituição financeira."
)

# Criar a sessão de chat com a ferramenta embutida usando a sintaxe moderna e passando as skills determinísticas e de laudo
chat = client.chats.create(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction=instrucao_sistema,
        tools=[consultar_zarc, consultar_embargo_esg, consultar_risco_climatico, gerar_laudo_oficial],
        temperature=0.0 # Respostas precisas e sem alucinação
    )
)

print("🤖 Agente AgroRisk V2 iniciado! (Digite 'sair' para encerrar)")
print("-" * 50)

# 4. O Loop da Conversa
while True:
    mensagem = input("Produtor: ")
    if mensagem.lower() in ['sair', 'exit', 'quit']:
        break
        
    try:
        # A mágica do Function Calling acontece aqui automaticamente em cascata (Laudos incluídos)
        resposta = chat.send_message(mensagem)
        print(f"\nAgroRisk: {resposta.text}\n")
    except Exception as e:
        print(f"\n[Erro de Comunicação]: {e}\n")