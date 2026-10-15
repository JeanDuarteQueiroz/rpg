from interface import criar_ficha_jogador

def main():
    jogador = criar_ficha_jogador()
    if jogador:
        print(f"Iniciando a jornada com {jogador.nome}...")
        # loop_jogo(jogador)

if __name__ == "__main__":
    main()