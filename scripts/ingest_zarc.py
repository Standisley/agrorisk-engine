import sys
import os
import time
import pandas as pd
from sqlalchemy import text

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.database import engine, SessionLocal

def run_ingestion():
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "zarc_real.csv")
    start_time = time.time()
    
    try:
        print("Lendo CSV (utf-8)...")
        # low_memory=False ajuda se o CSV tiver 1 Milhão+ de linhas e tipos confusos
        df = pd.read_csv(csv_path, sep=';', encoding='utf-8', low_memory=False)
    except UnicodeDecodeError:
        print("Fallback para leitura (latin1)...")
        df = pd.read_csv(csv_path, sep=';', encoding='latin1', low_memory=False)
    except Exception as e:
        print(f"Erro ao ler o arquivo {csv_path}: {e}")
        return
        
    print(f"Linhas lidas originais: {len(df)}")
    
    # Filtra apenas as colunas úteis (Atenção aos nomes exatos do governo)
    df = df[['geocodigo', 'Nome_cultura', 'Cod_Solo']]
    
    # Renomeia para o nosso padrão de banco
    df = df.rename(columns={
        'geocodigo': 'municipio_ibge',
        'Nome_cultura': 'cultura',
        'Cod_Solo': 'tipo_solo'
    })
    
    # Remove valores nulos
    df = df.dropna()
    
    # Remove as duplicatas
    df = df.drop_duplicates()
    
    # Garante os tipos corretos para não dar erro no Oracle
    df['municipio_ibge'] = df['municipio_ibge'].astype(int)
    df['tipo_solo'] = df['tipo_solo'].astype(int)
    df['cultura'] = df['cultura'].astype(str).str.upper().str.strip()
    
    # Adiciona a coluna de status
    df['status'] = 'ELEGIVEL'
    
    print(f"Linhas únicas para inserir: {len(df)}")
    
    # Limpeza de dados antigos da base
    print("Expurgando dados anteriores do banco (TRUNCATE tb_zarc_regras)...")
    db = SessionLocal()
    try:
        db.execute(text("TRUNCATE TABLE tb_zarc_regras"))
        db.commit()
    except Exception as e:
        db.rollback()
        print("Fallback para DELETE...")
        db.execute(text("DELETE FROM tb_zarc_regras"))
        db.commit()
    finally:
        db.close()
        
    # Inserção bulk via pandas to_sql
    print("Aguarde, inserindo dados no Oracle via to_sql() em chunks de 10000...")
    df.to_sql(
        name="tb_zarc_regras",
        con=engine,
        if_exists="append",
        index=False,
        chunksize=10000
    )
    
    end_time = time.time()
    elapsed = end_time - start_time
    print(f"🎉 Processo concluído com SUCESSO! Tempo decorrido: {elapsed:.2f} segundos.")

if __name__ == "__main__":
    run_ingestion()
