import json
from pathlib import Path


CAMINHO_RAIZ = Path(__file__).resolve().parent.parent
PASTA_DADOS = CAMINHO_RAIZ / "dados"

# FUNÇÃO GERAL #

def carregar_arquivos_json_da_pasta(subpasta: str) -> list[dict]:
     
     # Lê todos os .JSON dentro da subpasta 
     # e retorna uma lista de dicionarios com o conteúdo
     
    diretorio = PASTA_DADOS / subpasta
    lista_conteudo = []
    
    # Validação simples caso o diretório não exista.
    if not diretorio.exists():
        print(f"Aviso: Diretório {diretorio} não encontrado.")
        return lista_conteudo
    
    for arquivo in diretorio.glob("*.json"):
        try:
            with open(arquivo, "r", encoding="utf-8") as f:
                dados = json.load(f)
                lista_conteudo.append(dados)
        except json.JSONDecodeError as erro:
            print(f"Erro ao ler JSON no arquivo {arquivo.name}: {erro}")
    lista_conteudo.sort(key=lambda item: item.get("nome", ""))
    return lista_conteudo

# Funções diretas para a sua interface usar:

def carregar_todas_especies():
    return carregar_arquivos_json_da_pasta("especies")

def carregar_todas_classes():
    return carregar_arquivos_json_da_pasta("classes")

def carregar_todos_antecedentes():
    return carregar_arquivos_json_da_pasta("antecedentes")