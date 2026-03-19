import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.database import Base, engine
import core.models # Garante que todas as Models estão no cache do script

def setup_auditoria():
    print("Configurando novos esquemas de auditoria (BACEN) no Oracle...")
    Base.metadata.create_all(bind=engine)
    print("✅ Setup da 'tb_auditoria_consultas' concluído!")

if __name__ == "__main__":
    setup_auditoria()
