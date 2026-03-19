from core.database import SessionLocal
from core.models import ZarcRegra

def check_zarc_policy(municipio_ibge: int, cultura: str, tipo_solo: int) -> dict:
    """
    Verifica a política ZARC (Zoneamento Agrícola de Risco Climático)
    para o respectivo município, cultura e tipo de solo.
    """
    mapa_solos = {
        1: [11, 12],
        2: [13, 14],
        3: [15, 16]
    }
    # Se o usuário mandar 1, 2 ou 3, usamos a lista mapeada. 
    # Se ele mandar 13 direto, colocamos numa lista [13] para não quebrar a busca.
    solos_busca = mapa_solos.get(tipo_solo, [tipo_solo])

    db = SessionLocal()
    try:
        regra = db.query(ZarcRegra).filter(
            ZarcRegra.municipio_ibge == municipio_ibge,
            ZarcRegra.cultura == cultura.upper(),
            ZarcRegra.tipo_solo.in_(solos_busca)
        ).first()

        if regra:
            return {
                "status": regra.status,
                "auditoria": "Regra localizada no banco."
            }
        else:
            return {
                "status": "PENDENTE DE ANÁLISE HUMANA",
                "auditoria": "Regra ZARC não encontrada para esta combinação."
            }
    except Exception as e:
        return {
            "status": "ERRO",
            "auditoria": f"Falha na consulta ao banco de dados: {str(e)}"
        }
    finally:
        db.close()
