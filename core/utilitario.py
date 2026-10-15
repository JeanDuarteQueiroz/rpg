import json
import time
import os


def menu_pronto_jogar(nome_jogador="Desconhecido"):
    while True:
        resposta = True
        
        escolha = str(input("Está pronto para jogar? S - Sim |  N - Não\n").upper().strip)
        if escolha == 'S':
            return resposta
        elif escolha == 'N':
            resposta = False
            print("É uma pena...")
            return resposta


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
    
def espera_jogador():
    input(" Precione [ENTER] pra continuar...")
    
def nome_rpg():
    print(
        '''
        ████─████─████
        █──█─█──█─█───
        ████─████─█─██
        █─█──█────█──█
        █─█──█────████ 
        '''
   )
    time.sleep(0.2)
    print(
        '''
        ████──████─███────████──█─█─███────█───█─████─████─████─███─█───█
        █──██─█──█─█──────█──█──█─█─█──────██─██─█──█─█──█─█──█─█───██─██
        █──██─█──█─███────█─██──█─█─███────█─█─█─█──█─████─████─███─█─█─█
        █──██─█──█───█────█──█──█─█─█──────█───█─█──█─█─█──█─█──█───█───█
        ████──████─███────█████─███─███────█───█─████─█─█──█─█──███─█───█
        '''
    )
    time.sleep(0.5)
    print(
        '''
        ████─████─████─████────████─████─████──█───███─█──█─███
        █──█─█──█─█──█─█──█────█────█──█─█──██─█────█──██─█─█──
        ████─████─████─████────█─██─█──█─████──█────█──█─██─███
        █────█──█─█─█──█──█────█──█─█──█─█──██─█────█──█──█───█
        █────█──█─█─█──█──█────████─████─████──███─███─█──█─███        '''
    )