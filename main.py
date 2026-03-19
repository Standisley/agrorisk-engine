from fastapi import FastAPI
from api.schemas import ZarcConsultaRequest, ESGConsultaRequest
from skills.zarc_skill import check_zarc_policy
from skills.fraud_skill import check_esg_compliance
from skills.climate_skill import check_climate_risk
from core.database import SessionLocal
from core.models import AuditoriaConsulta

app = FastAPI(title="AgroRisk Engine API - V1")

@app.post("/api/v1/elegibilidade/zarc")
def consultar_elegibilidade_zarc(payload: ZarcConsultaRequest):
    # Executa a habilidade/validação nativamente através da regra engine
    resultado = check_zarc_policy(
        municipio_ibge=payload.municipio_ibge,
        cultura=payload.cultura,
        tipo_solo=payload.tipo_solo
    )
    
    # Gravando Histórico de Consultas para compliance do BACEN
    db = SessionLocal()
    try:
        log_auditoria = AuditoriaConsulta(
            municipio_ibge=payload.municipio_ibge,
            cultura=payload.cultura,
            tipo_solo=payload.tipo_solo,
            status_resposta=resultado.get("status", "ERRO (DESCONHECIDO)"),
            mensagem_auditoria=resultado.get("auditoria", "Análise executada sem parecer detalhado.")
        )
        db.add(log_auditoria)
        db.commit()
    except Exception as e:
        # Registramos a falha em log e liberamos a resposta do mesmo jeito
        print(f"Alerta Severo - Falha ao gravar auditoria no banco: {str(e)}")
        db.rollback()
    finally:
        db.close()
        
    return resultado

@app.post("/api/v1/compliance/esg")
def consultar_compliance_esg(payload: ESGConsultaRequest):
    return check_esg_compliance(
        documento=payload.documento,
        car=payload.car
    )

@app.get("/api/v1/clima/risco/{municipio_ibge}")
def consultar_risco_climatico_api(municipio_ibge: int):
    return check_climate_risk(municipio_ibge)
