import json
import time
import os

def carregar_dados_json(caminho):
    with open (caminho, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)
    
def digitar(texto, velocidade=0.2, quebra_linha=True):
    for char in texto:
        print(char, end='', flush=True)
        time.sleep(velocidade)
    print()
    
    if quebra_linha:
        print()
        
def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')