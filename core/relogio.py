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
        self.ordem_estacoes = ["Primavera", "Verao", "Outono", "Inverno"]
        self.dias_por_estacao = 60 
        self.dia_da_estacao = 1 # Para saber em que dia da estação atual estamos
        self.estacoes = {
            "Primavera": {
                "descricao": "O mundo desperta. A neve derrete formando rios caudalosos. O ar cheira a terra molhada e as cores são verdes e vibrantes. Animais saem das tocas.",
                "climas_possiveis": {
                        "sol_terno": "Céu limpo com nuvens esparsas. O sol aquece sem queimar, trazendo um clima perfeito e pacífico para a jornada, destacando as cores da flora.",
                        "chuvisco_prateado": "Uma garoa fina e agradável, quase uma névoa molhada que brilha sob a luz do sol, trazendo frescor ao ambiente sem atrapalhar a caminhada.",
                        "vento_semeador": "Lufadas de vento agradáveis que carregam pólen, pétalas coloridas e sementes aos montes, criando um espetáculo visual pelo ar.",
                        "aguaceiro_de_semeio": "Uma chuva torrencial e repentina de poucas horas. Transborda riachos e lava a terra, apagando pegadas e impondo desvantagem em testes de rastreamento.",
                        "bruma_matinal": "Um nevoeiro denso e baixo que abraça o chão durante as primeiras horas do dia. Esconde perigos rastejantes e armadilhas, exigindo atenção redobrada do grupo.",
                        "tempestade_de_despertar": "Muitos raios e trovões estrondosos ecoam pelo céu, mas com pouca chuva. O barulho assusta montarias e animais de carga, exigindo testes de adestramento para evitar fuga.",
                        "granizo_fino": "Pequenas pedras de gelo caem repentinamente de nuvens isoladas. Derretem rápido, mas causam incômodo suficiente para interromper e anular os benefícios de um descanso curto ao relento.",
                        "orvalho_denso": "A umidade do ar atinge o pico ao amanhecer. Não chove, mas barracas, roupas e equipamentos amanhecem encharcados e pesados, dobrando o tempo necessário para levantar acampamento."
                    }
            },
            "Verao": {
                "descricao": "",
                "climas_possiveis": {
                    "ceu_de_anil": "Ausência total de nuvens. Um azul profundo e um sol vibrante iluminam vastas distâncias de forma cristalina, secando o ambiente.",
                    "vento_de_fornalha": "Uma corrente de ar quente e seca que sopra pelo horizonte, ressecando a vegetação rasteira e criando pequenos redemoinhos de poeira.",
                    "noite_estrelada_limpa": "A noite cai sem uma única nuvem no céu. As estrelas brilham intensamente sob o calor brando, oferecendo uma visão majestosa do cosmos.",
                    "mormaco_pesado": "O céu fica nublado e esbranquiçado. O ar é abafado e úmido. Os personagens suam muito, exigindo o dobro de água diária e testes de resistência contra exaustão ao viajar.",
                    "toro_de_estio": "Tempestade violenta e curta com pingos grossos. Traz alívio rápido, mas o volume de água repentino cria enxurradas perigosas capazes de arrastar equipamentos em áreas baixas.",
                    "chuva_de_pedra": "O choque do calor com frentes frias nas alturas gera tempestades de granizo pesadas. O gelo fere personagens desprotegidos e amassa armaduras e escudos frágeis.",
                    "aridez_velada": "Uma violenta tempestade de poeira ou areia levantada pelos ventos secos. Reduz a visibilidade a zero e impõe dano de sufocamento caso não cubram o rosto rapidamente.",
                    "noite_estufada": "A temperatura não cai com a chegada da noite. O ar fica parado, cheio de mosquitos e abafado. Recuperar pontos de vida ou espaços de magia descansando é mais difícil."
                }
            },
            "Outono": {
                "descricao": "",
                "climas_possiveis": {
                    "ceu_plumbeo": "Um teto ininterrupto de nuvens cor de chumbo. O sol não aparece, criando uma atmosfera melancólica e silenciosa, sem alterações de terreno.",
                    "vento_uivante": "Rajadas frias e constantes que assobiam por entre os galhos secos e paredões de pedra, cantando uma melodia fúnebre anunciando o fim da estação.",
                    "crepusculo_dourado": "A luz do sol filtrada pelas folhas secas cria um fim de tarde de tons vivos de cobre e ouro, banhando o mundo em uma beleza letárgica.",
                    "garoa_melancolica": "Chuva gelada, fina e infinita. O frio entra nas roupas e deprime os viajantes, impedindo a recuperação de pontos de fadiga ou exaustão enquanto estiverem sob ela.",
                    "vendaval_de_folhas": "Ventos intensos arrancam a folhagem seca em turbilhões dourados e vermelhos. A poluição visual impõe penalidades em todos os ataques à distância e testes de percepção.",
                    "tempestade_uivante": "Ventos perigosos aliados a uma chuva forte. Arranca barracas mal fixadas do chão, quebra galhos sobre a cabeça dos jogadores e impossibilita acender fogueiras sem magia.",
                    "frio_seco": "O céu está estrelado e limpo, mas a temperatura despenca para perto de zero de repente. O ar gélido racha a pele e exige testes de resistência de constituição se não houver roupas grossas.",
                    "neblina_crepuscular": "Um nevoeiro espesso que surge apenas ao cair da noite, trazendo um frio úmido e hostil. Esconde silhuetas perfeitamente, garantindo vantagem máxima para inimigos furtivos."       
                },
            },
            "Inverno": {
                "descricao": "",
                "climas_possiveis": {
                    "neve_mansa": "Flocos grandes caindo lentamente em um silêncio absoluto. Uma cena de profunda paz que cobre o chão com um manto perfeitamente intocado e branco.",
                    "ceu_de_marmore": "O céu fica de um branco-acinzentado pálido e chapado, fundindo-se de forma grandiosa com as planícies e montanhas distantes.",
                    "geada_densa": "O chão de terra e a vegetação morta amanhecem cobertos por uma bela camada estaladiça de cristais de gelo finos, brilhando como vidro ao sol.",
                    "nevasca_cega": "Ventos furiosos e neve densa. Visibilidade reduzida a menos de um metro. Impõe risco extremo de separação do grupo e desvantagem severa em testes de sobrevivência ou navegação.",
                    "chuva_congelante": "Gotas de água super-resfriada que congelam ao tocar em qualquer superfície. Transforma o chão em uma pista de gelo escorregadia, exigindo testes de destreza a cada turno de combate para não cair.",
                    "vento_navalha": "Rajadas contínuas de vento em temperaturas muito abaixo de zero que cortam como vidro. Causa dano de frio a cada hora de viagem para personagens que tiverem pele exposta.",
                    "bruma_congelada": "Nevoeiro super-resfriado e letal. Respirar fundo machuca os pulmões. Qualquer atividade vigorosa, como correr ou lutar no gás gélido, causa níveis de exaustão imediatos.",
                    "tempestade_de_gelo": "Chovem agulhas de gelo e estilhaços afiados misturados com um vento trovejante. Forçar a travessia ao ar livre inflige dano perfurante e de frio constante a cada minuto."
                },
            },        
        }
        
        # --- CONTROLE DINÂMICO DE CLIMA ---
        self.climas_ativos = [] # A fila de 10 climas sorteados
        self.clima_atual = ""
        self.dias_restantes_clima = 0
        
        # Assim que o relógio nasce, ele gera a primeira previsão do tempo
        self.gerar_previsao_estacao()
        self.avancar_clima()

    def gerar_previsao_estacao(self):
# Transforma os nomes dos climas numa lista
        climas = list(self.estacoes[self.estacao_atual]["climas_possiveis"].keys())
        
        # Como temos 8 climas, precisamos de 8 pesos (ex: 3 normais, 5 perigosos)
        pesos = [3, 3, 2, 1, 1, 1, 1, 1]
        self.climas_ativos = random.choices(climas, weights=pesos, k=12 ) # Sorteio com maior probabilidade em "dias normais", sem efeitos.

    def avancar_clima(self):
        # Primeiro valida se está vazio, se tiver gera uma previsão (lista de climas), seta um clima (retirando ele da lista) e define os dias.
        if not self.climas_ativos:
            self.gerar_previsao_estacao()
            
        self.clima_atual = self.climas_ativos.pop(0)
        self.dias_restantes_clima = random.randint(1, 4)

    def obter_fase_atual(self) -> str:
        """
        Calcula a fase do dia com base nos ticks.
        Ex: se tick_atual = 4 e ticks_por_fase = 3, estamos na fase índice 1 ("Meia-manha").
        """
        indice = self.tick_atual // self.ticks_por_fase
        return self.fases_do_dia[indice]

    def avancar_tempo(self, quantidade_ticks: int):
        self.tick_atual += quantidade_ticks
        
        while self.tick_atual >= 24:
            self.tick_atual -= 24 
            self.dia_atual += 1
            self.dia_da_estacao += 1
            self.dias_restantes_clima -= 1
            
            # Se o dia da estação passar do limite, vira a estação
            if self.dia_da_estacao > self.dias_por_estacao:
                self.dia_da_estacao = 1
                self.mudar_estacao()
            
            if self.dias_restantes_clima < 1:
                self.avancar_clima()
                        
    def mudar_estacao(self):
        # Descobre qual é a estação atual e passa para a próxima na lista
        indice_atual = self.ordem_estacoes.index(self.estacao_atual)
        novo_indice = (indice_atual + 1) % len(self.ordem_estacoes)
        self.estacao_atual = self.ordem_estacoes[novo_indice]
        
        # Limpa o clima antigo para forçar o gerador a criar o clima da nova estação
        self.climas_ativos.clear()
        self.dias_restantes_clima = 0
        
        # Gera o primeiro clima da nova estação instantaneamente!
        self.avancar_clima()
        
        print(f"\n[SISTEMA] O tempo muda. A estação agora é: {self.estacao_atual.upper()}!")