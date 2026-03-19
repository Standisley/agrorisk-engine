import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.database import Base, engine, SessionLocal
from core.models import EmbargoESG

def run_seed_esg():
    print("Atualizando esquema do Oracle com novas tabelas de Compliance / ESG...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print("Semeando listas restritivas (IBAMA/MTE)...")
        if db.query(EmbargoESG).count() == 0:
            lista_negra = [
                EmbargoESG(
                    documento_produtor="111.111.111-11", 
                    numero_car="GO-5208707-1234", 
                    motivo_embargo="Desmatamento Ilegal (IBAMA)"
                ),
                EmbargoESG(
                    documento_produtor="222.222.222-22", 
                    numero_car="MT-5103403-9999", 
                    motivo_embargo="Sobreposição com Terra Indígena"
                )
            ]
            db.add_all(lista_negra)
            db.commit()
            print("Massa de bloqueios ESG inserida com sucesso!")
        else:
            print("Registros ESG ja semeados no banco previamente. Ignorando.")
    except Exception as e:
        print(f"Erro na insercao ESG: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_seed_esg()
