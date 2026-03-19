import os
from datetime import datetime

def gerar_laudo_oficial(
    documento: str, 
    car: str, 
    municipio_ibge: int, 
    cultura: str, 
    tipo_solo: str, 
    status_zarc: str, 
    status_esg: str, 
    decisao_final: str
) -> dict:
    """
    Gera fisicamente e salva o laudo oficial determinístico contendo a chancela de aprovação 
    ou a negativa documentada de crédito.
    """
    agora = datetime.now()
    timestamp = agora.strftime("%Y%m%d_%H%M%S")
    
    conteudo = f"""=============== LAUDO DE ELEGIBILIDADE E CONFORMIDADE - AGRORISK ===============
DATA/HORA: {agora.strftime("%d/%m/%Y %H:%M:%S")}
PROTOCOLO: {timestamp}

DADOS DO PROPONENTE
-------------------------------------------------
CPF/CNPJ: {documento}
CAR: {car}

DADOS AGRONÔMICOS
-------------------------------------------------
Município (IBGE): {municipio_ibge}
Cultura: {cultura}
Solo: {tipo_solo}

RESULTADOS DOS MOTORES
-------------------------------------------------
Parecer ZARC (MAPA): {status_zarc}
Parecer ESG (IBAMA): {status_esg}

DECISÃO FINAL DO MOTOR MEC
-------------------------------------------------
{decisao_final.upper()}
================================================="""

    # Caminho do diretório de laudos na raiz do projeto
    pasta_laudos = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'laudos'))
    os.makedirs(pasta_laudos, exist_ok=True)
    
    nome_arquivo = f"laudo_{documento}_{timestamp}.txt"
    caminho_completo = os.path.join(pasta_laudos, nome_arquivo)
    
    with open(caminho_completo, "w", encoding="utf-8") as file:
        file.write(conteudo)
        
    return {
        "status": "LAUDO_GERADO", 
        "caminho_arquivo": f"laudos/{nome_arquivo}"
    }
