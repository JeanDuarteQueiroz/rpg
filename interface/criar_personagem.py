from core.utilitario import limpar_tela
from core.dados import sor
from time import sleep
from menu_criacao import exibir_menu_especies, exibir_menu_classes, exibir_menu_antecedentes, escolher_especies, escolher_classe, escolher_antecedente, sortear_atributos
from models.jogador import Jogador

from core.carregador_dados import (
    carregar_todas_especies,
    carregar_todas_classes,
    carregar_todos_antecedentes,
)

lista_especies = carregar_todas_especies()
lista_classes = carregar_todas_classes()
lista_antecedentes = carregar_todos_antecedentes()

def criar_ficha_jogador ():
    ## ESCOLHA DO JOGADOR ##
    print(f"{"="*50}")
    print("Olá Jogador!".center(50))
    print(f"{"="*50}")
    print()
    nome_jogador = str(input("Como posso te chamar?  ").title())
    sleep(0.1)
    limpar_tela()
    
    # ## ESCOLHA DA ESPECIE ##
    exibir_menu_especies(lista_especies, nome_jogador="Desconhecido")
    especie_jogador = escolher_especies(lista_especies)

    print()
    sleep(0.3)
    limpar_tela()
    
    # ## ESCOLHA DA CLASSE ##
    exibir_menu_classes(lista_classes, nome_jogador="Desconhecido")
    classe_jogador = escolher_classe(lista_classes)
    
    print()
    sleep(0.3)
    limpar_tela()
    
    ## ESCOLHA DO ANTECEDENTE ##            
    exibir_menu_antecedentes(lista_antecedentes, nome_jogador="Desconhecido")
    antecedente_jogador = escolher_antecedente(lista_antecedentes)
    atributo = sortear_atributos(classe_jogador, nome_jogador="Desconhecido")
    
    print(f" Perfeito, {nome_jogador}! Essa é sua ficha no até o momento:")
    print()
    jogador1 = Jogador(nome_jogador, especie_jogador, classe_jogador, antecedente_jogador, atributo)
    jogador1.exibir_ficha() #PAUSA ATÉ O JOGADOR DAR ENTER
          
    sleep(2)    
    limpar_tela()