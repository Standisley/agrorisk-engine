from scripts.ingest_zarc import load_zarc_data

def trigger_zarc_ingestion(filepath_or_url: str) -> dict:
    """
    Skill para ingestão dinâmica pelo agente. Pode ser chamado para atualizar
    o banco de regras de negócio lendo um arquivo ou URL (CSV/JSON).
    """
    try:
        load_zarc_data(filepath_or_url)
        return {
            "status": "SUCESSO",
            "mensagem": f"Carga de regras concluída a partir do caminho {filepath_or_url}."
        }
    except Exception as e:
        return {
            "status": "ERRO",
            "mensagem": f"Ingestão ZARC falhou devido a: {str(e)}"
        }
