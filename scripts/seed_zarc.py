import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.database import Base, engine, SessionLocal
from core.models import ZarcRegra

# ... seus imports no topo ...

def seed():
    print("Limpando estrutura antiga (Drop)...")
    Base.metadata.drop_all(bind=engine)
    
    print("Criando nova estrutura (Create)...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print("Inserindo dados de Goiânia...")
        regras = [
            ZarcRegra(municipio_ibge=5208707, cultura="SOJA", tipo_solo=3, status="ELEGIVEL"),
            ZarcRegra(municipio_ibge=5208707, cultura="MILHO", tipo_solo=2, status="ELEGIVEL"),
            ZarcRegra(municipio_ibge=5208707, cultura="FEIJAO", tipo_solo=1, status="INELEGIVEL")
        ]
        db.add_all(regras)
        db.commit()
        print("✅ Carga de dados finalizada com sucesso!")
    except Exception as e:
        db.rollback()
        print(f"❌ Erro na carga de dados: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
