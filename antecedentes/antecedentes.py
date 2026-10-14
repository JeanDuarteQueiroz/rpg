def exibir_menu_antecedentes(antecedentes, nome_jogador="teste"):
    print("=" * 60)
    print(f"Ok {nome_jogador}!".center(60))
    print("última escolha!, escolha o 'ANTECEDENTE' do seu personagem!".center(60))
    print("=" * 60)
    print()

    print(" ANTECEDENTES USÁVEIS ".center(60, "-"))
    print()

    print(f" {"   ANTECEDENTE":<20} {"BONUS ATRIBUTO":<25} {"PERICIAS":<30}")
    for numero, dados in enumerate(antecedentes, start=1):
        print(f"  {numero}. {dados['nome'].ljust(10)} | {', '.join(dados['sigla_atributos'])} | {', '.join(dados['proeficiencia_pericias'])}")
    print(f"\n|{'-' * 58}|")
    print()


def escolher_antecedente(antecedentes):
    while True:
        escolha = input("Digite o número que representa sua escolha (Ex.: 1, 2 3...): ").strip()
        
        if escolha.isdigit() and 1 <= int(escolha) <= len(antecedentes):
            return antecedentes[int(escolha)-1]
        
        print(f"\nOpção inválida. Digite um número de 1 a {len(antecedentes)}.\n")
              
    