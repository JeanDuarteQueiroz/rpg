from core.utilitario import espera_jogador

def exibir_ficha(personagem):
    # ESPERA UM OBJETO JOGADOR / PERSONAGEM E RENDERIZA OS DADOS NO TERMINAL #   
    print(f"{'x'.ljust(25, '-')}| FICHA DO PERSONAGEM |{'x'.rjust(25, '-')}")
    print(f" {'|'.ljust(35,' ')} {'|'.rjust(35,' ')}")
    print(f" | Nome: {personagem.nome.ljust((23), ' ')} | Vida: {personagem.hp_atual}/{str(personagem.hp_max).ljust(14, ' ')} |  CA: {str(personagem.classe_armadura).ljust(4)} |")
    print(f" | Antecedente: {str(personagem.antecedente).ljust(16, ' ')} | Classe: {str(personagem.classe).ljust(15, ' ')} |  Nível: {str(personagem.nivel).ljust(1, ' ')} |")
    print(f" | Espécie: {str(personagem.especie).ljust(20, ' ')} |  XP:{str(personagem.xp).ljust(6, ' ')}|")
    print(f" {'|'.ljust(35,' ')} {'|'.rjust(35,' ')}")
    print(f"{'x'.ljust(29, '-')}| ATRIBUTOS |{'x'.rjust(31, '-')}")
    
    for atributo, valor in personagem.atributos.items():
        print(f"   {atributo.ljust(12).upper()} :{str(valor).rjust(5, '.')}") # Ajustei o rjust para um valor fixo seguro
    
    print(f"{'x'.ljust(36,'-')}{'x'.rjust(36,'-')}")
    espera_jogador()