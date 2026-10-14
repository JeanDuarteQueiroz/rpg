import sys
from pathlib import Path
# Encontra o caminho da pasta atual (minha_pasta) e pega a pasta mãe (meu_projeto)
pasta_mae = str(Path(__file__).resolve().parent.parent)

# Adiciona a pasta mãe ao sistema de caminhos do Python
if pasta_mae not in sys.path:
    sys.path.insert(0, pasta_mae)

from utilitario import digitar
from dados import rolar_dados_atributos


def exibir_menu_classes(lista_classes, nome_jogador="Desconhecido"):
    print("=" * 60)
    print(f"Você está indo bem {nome_jogador}!".center(60))
    print(f"Agora, escolha a 'CLASSE' com a qual quer jogar!".center(60))
    print(f"{"="*60}")
    print()    
    ## Cabeçalho
    print(" CLASSES DISPONÍVEIS ".center(60, '-'))
    print()
    
    print(f"  {"CLASSE":<20} {"DESCRIÇÃO":<25}")
    for numero, dados in enumerate(lista_classes, start=1):
        print(f" {numero}. {dados["nome".ljust(10)]} - {dados["descricao"]}")
    print(f"\n|{'-' * 58}|")
    print()

def escolher_classe(lista_classes):
    while True:
        escolha = input("Digite o número que representa sua escolha (Ex.: 1, 2 3...): ").strip()
        
        if escolha.isdigit() and 1 <=int(escolha) <= len(lista_classes):
            print("\nClasse escolhida com sucesso!!\n")
            return lista_classes[int(escolha)-1]
        
        print(f"\nOpção inválida. Digite um número de 1 a {len(lista_classes)}")

def definir_atributos_manual (atributos):
    atributos_jogador = {}
    valores_disponiveis = atributos.copy()
    nome_atributos = ["forca", "constituicao", "destreza", "inteligencia", "sabedoria", "carisma"]
    
    for atributo in nome_atributos:
        while True:
            print(f"\nValores disponíveis para escolha: {valores_disponiveis}")
            escolha = int(input(f"\nQual valor deseja informar para o {atributo.title()}: "))
            if escolha in valores_disponiveis:
                atributos_jogador[atributo] = escolha
                valores_disponiveis.remove(escolha)
                break
            else: 
                print("\nValor inválido!\n")
    return atributos_jogador     
                
def sortear_atributos(classe_jogador, nome_jogador="Desconhecido"):
    print(f"\n {nome_jogador}, você escolheu a {classe_jogador["nome"]} como Classe! E agora precisa decidir...\n")
    digitar("IMPORTANTE!")
    digitar("Deseja usar os atributos padrão para sua classe ou sortear nos dados?\n")
    
    while True:
        escolha = str(input("Digite P - Padrão, ou S - Sortear:  ")).upper().strip();
        atributo = True
        atributos = []
        if escolha == 'P':
            return atributo
        elif escolha == 'S':
            atributos = rolar_dados_atributos()
            print(f"Seus atributos sorteador são: {atributos}")
            print("Deseja definir os atributos manualmente? Ordenar pela importancia da classe?")
            define = str(input("M - Manual ou C - Classe ").upper().strip())
                
            print(f"Vou organizá-los em sua ficha conforme sua classe, seguindo o livro do jogador");
            return atributos