import json
import time
import os

def menu_pronto_jogar(nome_jogador="Aventureiro"):
    while True:
        # CORREÇÃO: () adicionados ao strip() e remoção da variável "resposta" redundante
        escolha = input(f"[{nome_jogador}] Está pronto para jogar? S - Sim |  N - Não\n").upper().strip()
        
        if escolha == 'S':
            return True
        elif escolha == 'N':
            print("É uma pena...")
            return False

def carregar_dados_json(caminho):
    with open(caminho, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)
    
def digitar(texto, velocidade=0.03, quebra_linha=True):
    # CORREÇÃO: Velocidade alterada de 0.2 para 0.03
    for char in texto:
        print(char, end='', flush=True)
        time.sleep(velocidade)
    
    print() # Fecha a linha atual de impressão
    
    if quebra_linha:
        print() # Adiciona uma linha vazia extra se desejado
        
def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')
    
def espera_jogador():
    # CORREÇÃO: Ortografia corrigida
    input(" Pressione [ENTER] para continuar...")
    
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