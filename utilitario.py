import json

def carregar_dados_json(caminho):
    with open (caminho, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)