import sys
from time import sleep

# Importações dos Motores do Jogo
# from core.banco_dados import BancoDeDados
from core.relogio import RelogioMundial
from core.gestor_cena import GestorCena
from core.motor_eventos import MotorEventos
from core.motor_combate import iniciar_combate
from interface.criar_personagem import criar_ficha_jogador

# Importações de Modelos
from models.jogador import Jogador


def rolar_dados(expressao: str, retorno: str = "total") -> int:
    """Função universal de rolagens (D20, D6, etc.) usada por todos os motores."""
    import random
    if expressao == "0": return 0
    partes = expressao.lower().split('d')
    if len(partes) != 2: return 0
    qtd = int(partes[0]) if partes[0].isdigit() else 1
    lados = int(partes[1])
    return sum(random.randint(1, lados) for _ in range(qtd))


def abrir_menu_sistema(jogador, mundo_estado) -> str:
    """O Hub Central do jogador fora do tempo do jogo (Não consome turnos/tempo)."""
    while True:
        print("\n" + "="*40)
        print(" ⛺ ACAMPAMENTO & SISTEMA ".center(40, "="))
        print("="*40)
        print("[1] 📓 Abrir Diário (Missões, Bestiário)")
        print("[2] 🎒 Abrir Ficha e Inventário")
        print("[3] 💾 Salvar Jogo (Funcionalidade em Breve)")
        print("[4] ❌ Sair para o Windows (Desistir)")
        print("[0] ⬅️ Voltar ao Jogo")
        
        escolha = input("\nAção: ").strip()
        
        if escolha == "1":
            jogador.diario.exibir_tela_diario()
            input("Pressione ENTER para voltar...")
            
        elif escolha == "2":
            jogador.inventario.exibir()
            print(f"\n--- DADOS VITAIS ---")
            print(f"HP: {jogador.hp_atual}/{jogador.hp_max} | XP: {jogador.xp}/{jogador.xp_necessario} | Nível: {jogador.nivel}")
            print(f"Classe de Armadura (CA): {jogador.classe_armadura}")
            nome_arma = jogador.arma_equipada.nome if getattr(jogador, 'arma_equipada', None) else 'Desarmado'
            print(f"Arma equipada: {nome_arma}")
            input("\nPressione ENTER para voltar...")
            
        elif escolha == "3":
            # Aqui entrará a lógica de dump (converter os dados em JSON e gravar num ficheiro)
            print("\n💾 Progresso guardado com sucesso! (Mecânica ainda em desenvolvimento)")
            sleep(1)
            
        elif escolha == "4":
            confirma = input("Tens a certeza que queres abandonar a aventura? (S/N): ").strip().upper()
            if confirma == "S":
                return "sair_jogo"
                
        elif escolha == "0":
            print("\nLevantas acampamento e preparas-te para continuar.")
            return "voltar"
            
        else:
            print("Opção inválida.")

def iniciar_jogo():
    """A raiz do jogo. Configura as engrenagens e lança o jogador no loop infinito."""
    
    # 1. INICIALIZAÇÃO DO BANCO DE DADOS

    # BancoDeDados.inicializar() # Descomenta quando os ficheiros JSON estiverem prontos!

    # 2. CRIAÇÃO DO ESTADO GLOBAL E RELÓGIO
    mundo_estado = {
        "jogo_iniciado": True
    }
    
    relogio = RelogioMundial()

    # 3. NASCIMENTO DO JOGADOR
    jogador = criar_ficha_jogador()
    
    # Injeção da primeira missão no Diário!
    jogador.diario.adicionar_missao(
        id_missao="prologo_valenor", 
        nome="Um Mundo Desconhecido", 
        etapa_inicial="Explorar os arredores e encontrar um local seguro.", 
        tipo="principal"
    )

    # Define o local inicial exato do jogador
    jogador.local_atual = "cena_inicial"

    # 4. PREPARAÇÃO DOS MOTORES
    # Assim que o banco de dados funcionar, troca as chaves {} pelas variáveis:
    # mapas_carregados = BancoDeDados._mapas
    # eventos_carregados = BancoDeDados._eventos
    # npcs_jogo = BancoDeDados._npcs_instanciados 
    mapas_carregados = {}    
    eventos_carregados = {}  
    npcs_jogo = []           

    gestor_cena = GestorCena(relogio, mundo_estado, mapas_carregados)
    motor_eventos = MotorEventos(relogio, mundo_estado, eventos_carregados)

    jogo_ativo = True

    print("\n" + "="*50)
    print(" A TUA AVENTURA COMEÇA AGORA ".center(50, " "))
    print("="*50)
    sleep(1)

    # ================================================================= #
    # =================| MÁQUINA DE ESTADOS (GAME LOOP) |============== #
    # ================================================================= #

    while jogo_ativo:
        
        # --- A. LER CENA ATUAL ---
        dados_sala = mapas_carregados.get(jogador.local_atual, {})

        # Fallback caso o mapa ainda não exista no JSON
        if not dados_sala:
            dados_sala = {
                "nome": "Lugar Nenhum",
                "descricao": "Estás num vazio temporal... O mapa JSON desta sala ainda não foi forjado.",
                "conexoes": {}
            }

        # Carrega apenas os NPCs que partilham a mesma sala que o jogador
        npcs_na_sala = [n for n in npcs_jogo if getattr(n, "local_atual", "") == jogador.local_atual]


        # --- B. O MESTRE DA HISTÓRIA (Eventos) ---
        evento_disparado = motor_eventos.verificar_gatilhos(jogador, jogador.local_atual)

        if evento_disparado:
            resultado_evento = motor_eventos.executar_evento(evento_disparado, jogador, rolar_dados)

            if isinstance(resultado_evento, dict):
                acao_evento = resultado_evento.get("acao")

                if acao_evento == "combate":
                    inimigos_evento = resultado_evento.get("inimigos", [])
                    sobreviveu = iniciar_combate(jogador, inimigos_evento, rolar_dados)
                    
                    if not sobreviveu:
                        jogo_ativo = False
                        break
                    else:
                        # Regista a criatura no Diário e desbloqueia fraquezas se matou muitos!
                        for inimigo in inimigos_evento:
                            jogador.diario.registrar_monstro(inimigo.id, inimigo.nome, abate=True)

                elif acao_evento == "mover":
                    jogador.local_atual = resultado_evento.get("destino")

            relogio.avancar_tempo(fases=1)
            continue # Volta ao início do loop para reagir ao que o Evento causou


        # --- C. O MESTRE DA EXPLORAÇÃO (Gestor de Cena) ---
        escolha = gestor_cena.processar_cena(jogador, jogador.local_atual, dados_sala, npcs_na_sala, rolar_dados)

        if not isinstance(escolha, dict):
            continue

        acao = escolha.get("acao")


        # --- D. PROCESSAMENTO DAS ESCOLHAS DO JOGADOR ---
        if acao == "mover" or acao == "nova_rota":
            print(f"\n🚶 Viajas em direção a novos ares...")
            sleep(1)
            jogador.local_atual = escolha.get("destino")
            relogio.avancar_tempo(fases=1)
        
        elif acao == "menu_sistema":
            retorno = abrir_menu_sistema(jogador, mundo_estado)
            if retorno == "sair_jogo":
                print("\nEncerando o motor de Valenor. Adeus, Mestre!")
                jogo_ativo = False
                break

        elif acao == "observar":
            gestor_cena.observar_arredores(jogador, jogador.local_atual, dados_sala)
            relogio.avancar_tempo(fases=1)

        elif acao == "saquear_corpo":
            corpo = escolha.get("alvo")
            gestor_cena.interface_de_saque(jogador, corpo)

        elif acao == "falar_npc":
            alvo_id = escolha.get("alvo_id")
            print(f"\n🗣️ Aproximas-te para conversar...")
            sleep(1)
            # Aqui será chamada a futura árvore de diálogo do NPC!

        elif acao == "menu_sistema":
            # Abre o acampamento para gerir fichas e saídas
            retorno = abrir_menu_sistema(jogador, mundo_estado)
            
            if retorno == "sair_jogo":
                print("\nA guardar os dados no pergaminho do tempo...")
                sleep(1)
                print("A tua lenda aguarda o teu regresso. Adeus!")
                jogo_ativo = False


# Inicia a execução do programa
if __name__ == "__main__":
    iniciar_jogo()