from pydantic import BaseModel

class ZarcConsultaRequest(BaseModel):
    municipio_ibge: int
    cultura: str
    tipo_solo: int

class ESGConsultaRequest(BaseModel):
    documento: str
    car: str
