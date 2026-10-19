from core.gestor_cena import GestorCena
from core.motor_eventos import MotorEventos
from core.motor_combate import iniciar_combate
from models.jogador import Jogador
from models.entidade import Npc
from models.itens import Arma, Item

# --- MOCK DO RELÓGIO ---
class RelogioFalso:
    def __init__(self):
        self.clima_atual = "limpo"
    def obter_fase_atual(self): return "Meio-dia"
    def avancar_tempo(self, fases=1): pass

def rolar_dados(expressao: str, retorno: str = "total") -> int:
    import random
    if expressao == "0": return 0
    partes = expressao.lower().split('d')
    if len(partes) != 2: return 0
    qtd = int(partes[0]) if partes[0].isdigit() else 1
    return sum(random.randint(1, int(partes[1])) for _ in range(qtd))

def iniciar_teste():
    relogio = RelogioFalso()
    mundo_estado = {"goblins_derrotados": False}
    
    # 1. JOGADOR
    jogador = Jogador("Kael", {"nome": "Humano"}, {"nome": "Bárbaro", "id": "barbaro", "atributos_padrao": {"forca": 16, "destreza": 14, "constituicao": 16, "inteligencia": 8, "sabedoria": 10, "carisma": 8}}, {"nome": "Forasteiro"})
    jogador.local_atual = "cabana_inicial"
    jogador.equipar_arma(Arma("espada_curta", "Espada Enferrujada", "Arma", 1.0, 5.0, "simples", "1d6", "cortante"))
    
    # 2. MAPA
    mapas_mock = {
        "cabana_inicial": {"nome": "Cabana Abandonada", "descricao": "Uma velha cabana.", "conexoes": {"floresta_escura": "Sair pela porta"}},
        "floresta_escura": {"nome": "Floresta Obscura", "descricao": "Árvores altas e assustadoras.", "conexoes": {"cabana_inicial": "Voltar para a Cabana"}}
    }
    
    # 3. EVENTO
    eventos_mock = {
        "emboscada_teste": {
            "id": "emboscada_teste",
            "gatilhos": {"local": "floresta_escura", "chance_disparo": 100},
            "requisitos": {"evento_bloqueado": "goblins_derrotados"},
            "nos": {
                "inicio": {
                    "narrador": "Um goblin salta de trás de um arbusto!",
                    "falas": [{"orador": "Goblin Feio", "idioma": "comum", "texto": "Passa o ouro!"}],
                    "opcoes": [
                        {"texto": "Atacar a criatura!", "acao": "iniciar_combate", "npc_ids": ["gob_1"]},
                    ]
                }
            }
        }
    }

    # 4. INIMIGO (Agora fixo na floresta e com Loot injetado)
    goblin = Npc("gob_1", "Goblin Feio", "Verde e irritado.", 10, 10, {"forca": 12, "destreza": 14}, {}, {})
    goblin.agressivo = True
    goblin.local_atual = "floresta_escura" # Ele "mora" aqui
    
    # Adicionamos loot manual ao bolso dele
    goblin.inventario.adicionar_moedas(23)
    goblin.inventario.adicionar_item(Item("faca_velha", "Faca Enferrujada", "Não corta nada.", 0.5, 1), 1)
    
    todos_npcs = [goblin]

    gestor_cena = GestorCena(relogio, mundo_estado, mapas_mock)
    motor_eventos = MotorEventos(relogio, mundo_estado, eventos_mock)
    
    jogo_ativo = True
    
    print("\n" + "="*40 + "\n O JOGO VAI COMEÇAR! \n" + "="*40)
    
    while jogo_ativo:
        dados_sala = mapas_mock.get(jogador.local_atual, {})
        
        # Filtra quem está realmente na sala atual do jogador
        npcs_na_sala = [n for n in todos_npcs if getattr(n, "local_atual", "") == jogador.local_atual]
        
        evento_disparado = motor_eventos.verificar_gatilhos(jogador, jogador.local_atual)
        if evento_disparado:
            resultado_evento = motor_eventos.executar_evento(evento_disparado, jogador, rolar_dados)
            if isinstance(resultado_evento, dict) and resultado_evento.get("acao") == "combate":
                sobreviveu = iniciar_combate(jogador, [n for n in npcs_na_sala if n.agressivo], rolar_dados)
                if not sobreviveu:
                    break
                else:
                    mundo_estado["goblins_derrotados"] = True 
            elif isinstance(resultado_evento, dict) and resultado_evento.get("acao") == "mover":
                jogador.local_atual = resultado_evento.get("destino")
            continue 
            
        escolha = gestor_cena.processar_cena(jogador, jogador.local_atual, dados_sala, npcs_na_sala, rolar_dados)
        
        if not isinstance(escolha, dict): continue
            
        acao = escolha.get("acao")
        if acao == "mover" or acao == "nova_rota":
            jogador.local_atual = escolha.get("destino")
        elif acao == "observar":
            gestor_cena.observar_arredores(jogador, jogador.local_atual, dados_sala)
        elif acao == "inventario":
            jogador.inventario.exibir()
        elif acao == "saquear_corpo":
            corpo = escolha.get("alvo") 
            gestor_cena.interface_de_saque(jogador, corpo) # <--- AQUI A MÁGICA ACONTECE!

if __name__ == "__main__":
    iniciar_teste()