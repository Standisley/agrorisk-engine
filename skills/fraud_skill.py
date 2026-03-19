from sqlalchemy import or_
from core.database import SessionLocal
from core.models import EmbargoESG

def check_esg_compliance(documento: str, car: str) -> dict:
    """
    Bloqueia propostas se houver sobreposição em propriedades e CPFs de Listas do Trabalho Escravo, IBAMA e Terras Indígenas.
    """
    db = SessionLocal()
    try:
        # Cross-validation: Basta um dos dois constar bloqueado e barramos o crédito inteiro.
        fraude = db.query(EmbargoESG).filter(
            or_(
                EmbargoESG.documento_produtor == documento,
                EmbargoESG.numero_car == car
            )
        ).first()

        if fraude:
            return {
                "status": "NEGADO_COMPLIANCE",
                "auditoria": f"Bloqueio ESG ativo: {fraude.motivo_embargo}"
            }
        
        return {
            "status": "LIBERADO",
            "auditoria": "Nada consta nas listas restritivas."
        }
    except Exception as e:
        return {
            "status": "ERRO_ANALISE",
            "auditoria": f"Não foi possível validar as premissas ESG da base de dados: {str(e)}"
        }
    finally:
        db.close()
