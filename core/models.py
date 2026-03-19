from sqlalchemy import Column, Integer, String, Identity, DateTime
from sqlalchemy.sql import func
from core.database import Base

class ZarcRegra(Base):
    __tablename__ = "tb_zarc_regras"

    # O "Identity()" é a mágica que avisa o Oracle para fazer o Auto-Increment
    id = Column(Integer, Identity(), primary_key=True)
    municipio_ibge = Column(Integer, nullable=False)
    cultura = Column(String(50), nullable=False)
    tipo_solo = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False)

class AuditoriaConsulta(Base):
    __tablename__ = "tb_auditoria_consultas"

    id = Column(Integer, Identity(), primary_key=True)
    data_hora = Column(DateTime, default=func.now())
    municipio_ibge = Column(Integer)
    cultura = Column(String(100))
    tipo_solo = Column(Integer)
    status_resposta = Column(String(50))
    mensagem_auditoria = Column(String(255))

class EmbargoESG(Base):
    __tablename__ = "tb_embargos_esg"

    id = Column(Integer, Identity(), primary_key=True)
    documento_produtor = Column(String(50), index=True)
    numero_car = Column(String(100), index=True)
    motivo_embargo = Column(String(255))
