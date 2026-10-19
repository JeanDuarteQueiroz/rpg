import sys
from time import sleep

# Importações do nosso motor
from core.gestor_cena import GestorCena
from core.motor_eventos import MotorEventos
from core.motor_combate import iniciar_combate
from models.jogador import Jogador
from models.entidade import Npc

# --- MOCK DO RELÓGIO ---
class RelogioFalso:
    def __init__(self):
        self.clima_atual = "limpo"
        self.hora = 10
    def obter_fase_atual(self):
        return "Meio-dia"
    def avancar_tempo(self, fases=1):
        pass

# --- FUNÇÃO UNIVERSAL DE DADOS ---
def rolar_dados(expressao: str, retorno: str = "total") -> int:
    import random
    if expressao == "0": return 0
    partes = expressao.lower().split('d')
    if len(partes) != 2: return 0
    qtd = int(partes[0]) if partes[0].isdigit() else 1
    lados = int(partes[1])
    return sum(random.randint(1, lados) for _ in range(qtd))

def iniciar_teste():
    print("A carregar Valenor...\n")
    
    # 1. SETUP DO ESTADO GLOBAL
    relogio = RelogioFalso()
    mundo_estado = {"goblins_derrotados": False}
    
    # 2. CRIAR O JOGADOR DE TESTE
    # Dicionários falsos para não precisarmos do JSON de classes agora
    dic_especie = {"nome": "Humano"}
    dic_classe = {"nome": "Bárbaro", "id": "barbaro", "dado_de_vida": "1d12", "atributos_padrao": {"forca": 16, "destreza": 14, "constituicao": 16, "inteligencia": 8, "sabedoria": 10, "carisma": 8}}
    dic_antecedente = {"nome": "Forasteiro"}
    
    jogador = Jogador("Kael", dic_especie, dic_classe, dic_antecedente)
    jogador.local_atual = "cabana_inicial"
    
    # Adicionamos uma espada básica para ele bater
    from models.itens import Arma
    espada = Arma("espada_curta", "Espada Enferrujada", "Arma básica", 1.0, 5.0, "simples", "1d6", "cortante")
    jogador.equipar_arma(espada)
    
    # 3. CRIAR O MAPA DE TESTE (Simulando o JSON de Mapas)
    mapas_mock = {
        "cabana_inicial": {
            "nome": "Cabana Abandonada",
            "descricao": "Uma velha cabana de madeira com buracos no teto. O cheiro de mofo é forte.",
            "conexoes": {"floresta_escura": "Sair pela porta da frente"},
            "elementos_escondidos": [
                {
                    "id_segredo": "alcapao_secreto",
                    "cd_percepcao": 10,
                    "mensagem_sucesso": "Encontraste um alçapão escondido debaixo de um tapete podre!",
                    "tipo": "nova_rota",
                    "texto_botao": "Descer pelo Alçapão",
                    "destino": "porao_secreto"
                }
            ]
        },
        "floresta_escura": {
            "nome": "Floresta Obscura",
            "descricao": "Árvores altas bloqueiam a luz do sol. O som de galhos a estalar arrepia-te a espinha.",
            "conexoes": {"cabana_inicial": "Voltar para a Cabana"}
        },
        "porao_secreto": {
            "nome": "Porão Empoeirado",
            "descricao": "Um lugar húmido e escuro. Há marcas de garras nas paredes.",
            "conexoes": {"cabana_inicial": "Subir as escadas de volta"}
        }
    }
    
    # 4. EVENTOS MOCK (Para testar quando fores para a floresta)
    eventos_mock = {
        "emboscada_teste": {
            "id": "emboscada_teste",
            "gatilhos": {"local": "floresta_escura", "chance_disparo": 100},
            "requisitos": {"evento_bloqueado": "goblins_derrotados"},
            "nos": {
                "inicio": {
                    "narrador": "Um goblin salta de trás de um arbusto com uma faca na mão!",
                    "falas": [{"orador": "Goblin Feio", "idioma": "comum", "texto": "Passa o ouro, humano gigante!"}],
                    "opcoes": [
                        {"texto": "Atacar a criatura!", "acao": "iniciar_combate", "npc_ids": ["gob_1"]},
                        {"texto": "Fugir de volta para a cabana!", "acao": "avancar_no", "destino": "fuga"}
                    ]
                },
                "fuga": {
                    "narrador": "Corres de volta, tropeçando em raízes, até bateres a porta da cabana.",
                    "opcoes": [{"texto": "Recuperar o fôlego", "acao": "mover", "destino": "cabana_inicial"}]
                }
            }
        }
    }

    # 5. INIMIGOS MOCK
    goblin = Npc("gob_1", "Goblin Feio", "Verde e irritado.", 10, 10, {"forca": 12, "destreza": 14}, {}, {})
    goblin.agressivo = True # Já nasce com vontade de te matar

    # 6. INSTANCIAR MOTORES
    gestor_cena = GestorCena(relogio, mundo_estado, mapas_mock)
    motor_eventos = MotorEventos(relogio, mundo_estado, eventos_mock)
    
    jogo_ativo = True
    
    print("="*40)
    print(" O JOGO VAI COMEÇAR! ".center(40, "="))
    print("="*40)
    sleep(1)
    
    while jogo_ativo:
        dados_sala = mapas_mock.get(jogador.local_atual, {})
        npcs_na_sala = [] # Limpamos a sala a cada turno
        
        # O Motor de Eventos tenta sequestrar a cena
        evento_disparado = motor_eventos.verificar_gatilhos(jogador, jogador.local_atual)
        
        if evento_disparado:
            resultado_evento = motor_eventos.executar_evento(evento_disparado, jogador, rolar_dados)
            
            if isinstance(resultado_evento, dict) and resultado_evento.get("acao") == "combate":
                # O evento atirou-nos um combate!
                sobreviveu = iniciar_combate(jogador, [goblin], rolar_dados)
                if not sobreviveu:
                    jogo_ativo = False
                    break
                else:
                    mundo_estado["goblins_derrotados"] = True # Marca que ganhámos o evento
                    print("A floresta volta a ficar silenciosa...")
            
            elif isinstance(resultado_evento, dict) and resultado_evento.get("acao") == "mover":
                jogador.local_atual = resultado_evento.get("destino")
                
            continue # Volta ao inicio do loop
            
        # Mestre da Exploração (Menu normal)
        escolha = gestor_cena.processar_cena(jogador, jogador.local_atual, dados_sala, npcs_na_sala, rolar_dados)
        
        if not isinstance(escolha, dict):
            continue
            
        acao = escolha.get("acao")
        
        if acao == "mover" or acao == "nova_rota":
            print(f"\n🚶 Viajas para outro local...")
            sleep(1)
            jogador.local_atual = escolha.get("destino")
            
        elif acao == "observar":
            gestor_cena.observar_arredores(jogador, jogador.local_atual, dados_sala)
            
        elif acao == "inventario":
            jogador.inventario.exibir()
            print(f"HP Atual: {jogador.hp_atual}/{jogador.hp_max}")
            print(f"Arma equipada: {jogador.arma_equipada.nome if jogador.arma_equipada else 'Nenhuma'}")

if __name__ == "__main__":
    iniciar_teste()