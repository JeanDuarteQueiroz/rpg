import random

class RelogioMundial():
    def __init__(self):
        # --- CONTROLE DE TEMPO BASE ---
        self.tick_atual = 0
        self.dia_atual = 1
        self.fases_do_dia = [
            "Amanhecer", "Meia-manha", "Meio-dia", "Meia-tarde", 
            "Entardecer", "Noite", "Alta-noite", "Madrugada"
        ]
        self.ticks_por_fase = 3 # Exemplo: A cada 3 ações, muda a fase.
        
        # --- DADOS DO MUNDO ---
        self.estacao_atual = "Primavera"
        self.estacoes = {
            "Primavera": {
                "descricao": "O mundo desperta...",
                "climas_possiveis": {
                    "sol-normal": "Um dia de sol normal",
                    "chuva-normal": "Um dia de chuva normal",
                    "sol-terno": "Céu limpo com nuvens esparsas. O sol aquece sem queimar. Clima perfeito para viagens longas.",
                    "chuvisco-prateado": "Uma garoa fina, quase uma névoa molhada, que brilha sob a luz do sol. Não atrapalha a viagem, mas deixa o terreno escorregadio.",
                    "aguaceiro-de-semeio": "Uma chuva torrencial e repentina que dura poucas horas. Transborda riachos, cria poças profundas de lama e lava os rastros do chão",
                    "bruma-matinal": "Um nevoeiro denso e baixo que abraça o chão durante a Aurora e a Matina. Esconde armadilhas e criaturas rastejantes.",
                    "vento-semeador": "Lufadas de vento agradáveis, mas que carregam pólen, pétalas e sementes aos montes. Pode causar espirros (atrapalhando furtividade) ou espalhar esporos mágicos.",
                    "tempestade-de-despertar": "Muitos raios e trovões estrondosos que ecoam pelo céu, mas com pouca ou nenhuma chuva. Assusta montarias e animais silvestres.",
                    "granizo-fino": "Pequenas pedras de gelo que caem do nada em um dia ensolarado, derretendo assim que tocam a terra quente.",
                    "orvalho-denso": "Acontece ao amanhecer. Não chove, mas a umidade do ar é tanta que as roupas de cama, as barracas e a grama amanhecem encharcadas."
                }
            }
            # Adicione depois: Verão, Outono, Inverno
        }
        
        # --- CONTROLE DINÂMICO DE CLIMA ---
        self.climas_ativos = [] # A fila de 10 climas sorteados
        self.clima_atual = ""
        self.dias_restantes_clima = 0
        
        # Assim que o relógio nasce, ele gera a primeira previsão do tempo
        self.gerar_previsao_estacao()
        self.avancar_clima()

    # ========================================== #
    #         MÉTODOS PARA VOCÊ CONSTRUIR        #
    # ========================================== #

    def gerar_previsao_estacao(self):
        """
        Sorteia 10 climas dos 'climas_possiveis' da estação atual
        e preenche a lista self.climas_ativos.
        Dica: Use random.choices() para permitir climas repetidos na fila.
        """
        climas = self.estacoes[self.estacao_atual]["climas_possiveis"]
        lista_sorteio = random.choices(climas, weights=[8,4,1,1,1,1,1,1,1,1], k=12 ) # Sorteio com maior probabilidade em "dias normais", sem efeitos.
        return lista_sorteio 

    def avancar_clima(self):
        """
        1. Verifica se a fila self.climas_ativos está vazia. Se estiver, chama gerar_previsao_estacao().
        2. Remove o primeiro item da fila (.pop(0)) e o define como self.clima_atual.
        3. Sorteia um número de 1 a 4 e atribui a self.dias_restantes_clima.
        """
        # Primeiro valida se está vazio, se tiver gera uma previsão (lista de climas), seta um clima (retirando ele da lista) e define os dias.
        if not self.climas_ativos:
            self.climas_ativos = self.gerar_previsao_estacao()
            self.clima_atual = self.climas_ativos.pop(0)
            self.dias_restantes_clima = random.randint(1, 4)
        
        elif self.dias_restantes_clima <= 0:
            self.clima_atual = self.climas_ativos.pop(0)
            self.dias_restantes_clima = random.randint(1,4)
        
        else:
            self.dias_restantes_clima -= 1 

    def obter_fase_atual(self) -> str:
        """
        Calcula a fase do dia com base nos ticks.
        Ex: se tick_atual = 4 e ticks_por_fase = 3, estamos na fase índice 1 ("Meia-manha").
        """
        indice = self.tick_atual // self.ticks_por_fase
        return self.fases_do_dia[indice]

    def avancar_tempo(self, quantidade_ticks: int):
        """
        O coração do Relógio.
        1. Soma os ticks.
        2. Calcula se ultrapassou o limite de ticks de um dia inteiro (8 fases * 3 = 24 ticks).
        3. Se virou o dia (passou da Madrugada):
            - self.dia_atual += 1
            - self.dias_restantes_clima -= 1
            - Se dias_restantes_clima <= 0, chama self.avancar_clima()
        """
        # Substitua o 'pass' pela sua lógica
        
        self.tick_atual += quantidade_ticks + self.tick_atual