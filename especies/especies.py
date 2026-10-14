import sys
from pathlib import Path
# Encontra o caminho da pasta atual (minha_pasta) e pega a pasta mãe (meu_projeto)
pasta_mae = str(Path(__file__).resolve().parent.parent)

# Adiciona a pasta mãe ao sistema de caminhos do Python
if pasta_mae not in sys.path:
    sys.path.insert(0, pasta_mae)

def exibir_menu_especies(lista_especies, nome_jogador):
    print(f"{"="*60}")
    print(f"Muito bem, {nome_jogador}!".center(60))
    print(f"Por favor, escolha a 'ESPÉCIE' com a qual quer jogar!".center(60))
    print(f"{"="*60}")
    print()
    
    print(" ESPECIES DISPONÍVEIS ".center(60, "-"))
    print()
    
    print(f" {"   ESPECIE":<20} {"BONUS ATRIBUTO":<25} {"PERICIAS":<30}")
    for numero, dados in enumerate(lista_especies, start=1):
        print(f" {numero}. {dados["nome"]} - [{dados["descricao"]}]")
    print(f"\n|{'-' * 58}|")
    print()
    
def escolher_especies(lista_especies):
    while True:
        escolha = input("Digite o número que representa sua escolha (Ex.: 1, 2 3...): ").strip()
        
        if escolha.isdigit() and 1 <= int(escolha) <= len(lista_especies):
            print("\nEspecie escolhida com sucesso!!\n")
            return lista_especies[int(escolha) - 1]

        print(f"\nOpção inválida. Digite um número de 1 a {len(lista_especies)}.\n")
    
    