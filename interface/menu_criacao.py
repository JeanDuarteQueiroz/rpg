from core.dados import rolar_dados_atributos

#------------------- OUTROS -------------------#
def sortear_atributos(classe_jogador, nome_jogador="Desconhecido"):
    print(f"\n {nome_jogador}, você escolheu a {classe_jogador['nome']} como Classe! E agora precisa decidir...\n")
    print("IMPORTANTE!")
    print("Deseja usar os atributos padrão para sua classe ou sortear nos dados?\n")
    
    while True:
        # Ponto e vírgula removido no final
        escolha = str(input("Digite P - Padrão, ou S - Sortear:  ")).upper().strip()
        if escolha == 'P':
            return True # Retorna diretamente o booleano esperado pelo Jogador
        elif escolha == 'S':
            atributos_rolados = rolar_dados_atributos()
            print(f"Seus atributos sorteados são: {atributos_rolados}")
            atributos_finais = definir_atributos_manual(atributos_rolados) 
            return atributos_finais

def definir_atributos_manual(atributos):
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

# ----------------- ESPECIE ------------------#
def exibir_menu_especies(lista_especies, nome_jogador):
    print(f"{'='*60}")
    print(f"Muito bem, {nome_jogador}!".center(60))
    print(f"Por favor, escolha a 'ESPÉCIE' com a qual quer jogar!".center(60))
    print(f"{'='*60}")
    print()
    
    print(" ESPECIES DISPONÍVEIS ".center(60, "-"))
    print()
    
    print(f" {'ESPECIE':<20} {'BONUS ATRIBUTO':<25} {'PERICIAS':<30}")
    for numero, dados in enumerate(lista_especies, start=1):
        # Aspas simples nas chaves do dicionário dentro do f-string!
        print(f" {numero}. {dados['nome']} - [{dados.get('descricao', '')}]")
    print(f"\n|{'-' * 58}|")
    print()
    
def escolher_especies(lista_especies):
    while True:
        escolha = input("Digite o número que representa sua escolha (Ex.: 1, 2 3...): ").strip()
        
        if escolha.isdigit() and 1 <= int(escolha) <= len(lista_especies):
            print("\nEspecie escolhida com sucesso!!\n")
            return lista_especies[int(escolha) - 1]

        print(f"\nOpção inválida. Digite um número de 1 a {len(lista_especies)}.\n")

#------------------ CLASSE -------------------#
def exibir_menu_classes(lista_classes, nome_jogador="Desconhecido"):
    print("=" * 60)
    print(f"Você está indo bem {nome_jogador}!".center(60))
    print(f"Agora, escolha a 'CLASSE' com a qual quer jogar!".center(60))
    print(f"{'='*60}")
    print()    
    print(" CLASSES DISPONÍVEIS ".center(60, '-'))
    print()
    
    print(f"  {'CLASSE':<20} {'DESCRIÇÃO':<25}")
    for numero, dados in enumerate(lista_classes, start=1):
        print(f" {numero}. {dados['nome'].ljust(10)} - {dados.get('descricao', '')}")
    print(f"\n|{'-' * 58}|")
    print()

def escolher_classe(lista_classes):
    while True:
        escolha = input("Digite o número que representa sua escolha (Ex.: 1, 2 3...): ").strip()
        
        if escolha.isdigit() and 1 <= int(escolha) <= len(lista_classes):
            print("\nClasse escolhida com sucesso!!\n")
            return lista_classes[int(escolha)-1]
        
        print(f"\nOpção inválida. Digite um número de 1 a {len(lista_classes)}")

#------------------ ANTECEDENTE ------------------#
def exibir_menu_antecedentes(antecedentes, nome_jogador="teste"):
    print("=" * 60)
    print(f"Ok {nome_jogador}!".center(60))
    print("última escolha!, escolha o 'ANTECEDENTE' do seu personagem!".center(60))
    print("=" * 60)
    print()

    print(" ANTECEDENTES DISPONÍVEIS ".center(60, "-"))
    print()

    print(f" {'ANTECEDENTE':<20} {'BONUS ATRIBUTO':<25} {'PERICIAS':<30}")
    for numero, dados in enumerate(antecedentes, start=1):
        # Proteção com .get() caso o antecedente não tenha bônus ou perícias definidos
        bonus = ", ".join(dados.get('sigla_atributos', []))
        pericias = ", ".join(dados.get('proficiencia_pericias', []))
        print(f"  {numero}. {dados['nome'].ljust(10)} | {bonus} | {pericias}")
    print(f"\n|{'-' * 58}|")
    print()

def escolher_antecedente(lista_antecedentes):
    while True:
        escolha = input("Digite o número que representa sua escolha (Ex.: 1, 2 3...): ").strip()
        
        if escolha.isdigit() and 1 <= int(escolha) <= len(lista_antecedentes):
            print("\nAntecedente escolhido com sucesso!!\n")
            return lista_antecedentes[int(escolha)-1]
        
        print(f"\nOpção inválida. Digite um número de 1 a {len(lista_antecedentes)}.\n")