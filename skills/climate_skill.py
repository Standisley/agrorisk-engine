import requests
from datetime import datetime, timedelta

def buscar_coordenadas_na_web(municipio_ibge: int):
    try:
        url_ibge = f"https://servicodados.ibge.gov.br/api/v1/localidades/municipios/{municipio_ibge}"
        resp_ibge = requests.get(url_ibge, timeout=10)
        resp_ibge.raise_for_status()
        data_ibge = resp_ibge.json()
        
        nome = data_ibge["nome"]
        uf = data_ibge["microrregiao"]["mesorregiao"]["UF"]["sigla"]
        
        url_nom = f"https://nominatim.openstreetmap.org/search?city={nome}&state={uf}&country=Brazil&format=json"
        headers = {"User-Agent": "AgroRiskEngine/1.0"}
        resp_nom = requests.get(url_nom, headers=headers, timeout=10)
        resp_nom.raise_for_status()
        data_nom = resp_nom.json()
        
        if data_nom and len(data_nom) > 0:
            lat = float(data_nom[0]["lat"])
            lon = float(data_nom[0]["lon"])
            return lat, lon
            
    except Exception:
        pass
        
    return None, None

def check_climate_risk(municipio_ibge: int) -> dict:
    lat, lon = buscar_coordenadas_na_web(municipio_ibge)
    
    if lat is None or lon is None:
        return {
            "status": "ERRO_COORDENADAS",
            "auditoria": f"Não foi possível localizar as coordenadas do IBGE {municipio_ibge} na web."
        }
        
    # Período de Avaliação: Últimos 15 dias transcorridos
    end_date = datetime.now()
    start_date = end_date - timedelta(days=15)
    
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    
    # Endpoint de arquivo meteorológico real para processamento de chuva
    url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_str}&end_date={end_str}&daily=precipitation_sum&timezone=America%2FSao_Paulo"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        precipitacoes = data.get("daily", {}).get("precipitation_sum", [])
        
        # Limpa nulos eventuais em dias não consolidados e soma o volume (mm)
        total = sum([p for p in precipitacoes if p is not None])
        
        # Regra de negócio (Seca < 30mm)
        if total < 30.0:
            return {
                "status": "ALERTA_CLIMATICO",
                "auditoria": f"Estresse hídrico detectado. Acumulado de apenas {total:.2f}mm nos últimos 15 dias."
            }
        else:
            return {
                "status": "CLIMA_FAVORAVEL",
                "auditoria": f"Umidade adequada. Acumulado de {total:.2f}mm."
            }
            
    except Exception as e:
        return {
            "status": "ERRO_CLIMA",
            "auditoria": f"Falha ao checar histórico climático: {e}"
        }
