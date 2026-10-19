from core.banco_dados import BancoDeDados
from interface.criar_personagem import criar_ficha_jogador
from interface.ficha_view import exibir_ficha

def main():
    print("=== INICIALIZANDO O JOGO ===")
    
    # 1. Inicializa o Banco de Dados (Carrega classes, habilidades, magias e itens dos JSONs)
    BancoDeDados.inicializar()
    print("\nBanco de dados carregado com sucesso!\n")
    
    # 2. Executa o fluxo de criação do personagem (Menu interativo no terminal)
    # Certifique-se de que sua função criar_ficha_jogador() retorna o objeto 'jogador1' criado.
    print("--- ETAPA 1: CRIAÇÃO DO PERSONAGEM ---")
    jogador = criar_ficha_jogador()
    
    print(f"HP antes de subir: {jogador.hp_atual}/{jogador.hp_max}")
    jogador.subir_nivel()
    print(f"HP depois de subir: {jogador.hp_atual}/{jogador.hp_max}")

if __name__ == "__main__":
    main()