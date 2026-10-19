from core.utilitario import limpar_tela, espera_jogador, nome_rpg
from time import sleep
from interface.menu_criacao import exibir_menu_especies, exibir_menu_classes, exibir_menu_antecedentes, escolher_especies, escolher_classe, escolher_antecedente, sortear_atributos
from interface.ficha_view import exibir_ficha
from models.jogador import Jogador
from core.banco_dados import BancoDeDados

def criar_ficha_jogador():
    # INICIALIZA O BANCO DE DADOS ANTES DE QUALQUER COISA!
    
    print("[SISTEMA] Carregando o mapa da campanha...\n")
    sleep(0.9)
    print("[SISTEMA] Forjando sua próxima aventura...\n")
    sleep(0.9)
    print("[SISTEMA] Abrindo o portal para outro reino...\n")
    sleep(0.9)
    print("[SISTEMA] Aguardando a rolagem dos dados...\n")
    sleep(0.9)
    print("[SISTEMA] Inicializando...\n")
    sleep(1.5)
    limpar_tela()
    
    if not BancoDeDados._classes: # Garante que só inicializa uma vez
        BancoDeDados.inicializar()

    # Busca as listas diretamente do banco para os menus
    lista_especies = list(BancoDeDados._especies.values())
    lista_classes = list(BancoDeDados._classes.values())
    lista_antecedentes = list(BancoDeDados._antecedentes.values())

    ## ESCOLHA DO JOGADOR ##
    print(f"{'='*50}")
    print("Olá Jogador!".center(50))
    print(f"{'='*50}")
    print()
    nome_jogador = str(input("Como posso te chamar?  ").title())
    limpar_tela()
    
    # ## ESCOLHA DA ESPECIE ##
    exibir_menu_especies(lista_especies, nome_jogador=nome_jogador)
    especie_jogador = escolher_especies(lista_especies)

    espera_jogador()
    limpar_tela()
    
    # ## ESCOLHA DA CLASSE ##
    exibir_menu_classes(lista_classes, nome_jogador=nome_jogador)
    classe_jogador = escolher_classe(lista_classes)
    
    espera_jogador()
    limpar_tela()
    
    ## ESCOLHA DO ANTECEDENTE ##            
    exibir_menu_antecedentes(lista_antecedentes, nome_jogador=nome_jogador)
    antecedente_jogador = escolher_antecedente(lista_antecedentes)
    
    espera_jogador()
    limpar_tela()
    atributo = sortear_atributos(classe_jogador, nome_jogador=nome_jogador)
    
    print(f" Perfeito, {nome_jogador}! Essa é a sua ficha até ao momento:")
    print()
    
    # A Mágica Acontece: Cria o Jogador (O __init__ dele vai ler do Banco de Dados)
    jogador1 = Jogador(nome_jogador, especie_jogador, classe_jogador, antecedente_jogador, atributo)
    exibir_ficha(jogador1) # PAUSA ATÉ O JOGADOR DAR ENTER
          
    sleep(2)    
    limpar_tela()
    
    print("Seja bem vindo ao: ")
    sleep(2)
    nome_rpg()
    
    
    # Podes devolver o jogador1 no fim se o quiseres usar noutras partes do código
    return jogador1