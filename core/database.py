import os
from dotenv import load_dotenv
import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Força o carregamento do .env
load_dotenv()

# Captura segura das variáveis
USER = os.getenv("DB_USER", "agrorisk_admin").strip()
PASS_RAW = os.getenv("DB_PASS", "Standis2020@").strip()
HOST = os.getenv("DB_HOST", "127.0.0.1").strip()
PORT = os.getenv("DB_PORT", "1521").strip()
SERVICE = os.getenv("DB_SERVICE", "xepdb1").strip()

# Codifica a senha (transforma o @ em %40)
PASS_ENCODED = urllib.parse.quote_plus(PASS_RAW)

# Formato exato exigido pelo SQLAlchemy
SQLALCHEMY_DATABASE_URL = f"oracle+oracledb://{USER}:{PASS_ENCODED}@{HOST}:{PORT}/?service_name={SERVICE}"

# Criação do Motor e da Sessão
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os nossos modelos
Base = declarative_base()
