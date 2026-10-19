from models.itens import Inventario


class Npc:
    def __init__(
        self,
        id_npc: str,
        nome: str,
        descricao: str,
        hp_max: int,
        classe_armadura: int,
        atributos: dict,
        psique: dict,
        social: dict,
        tags: list = None,
        xp_recompensa: int = 10,
        tabela_loot: str = "loot_vazio"
    ):
        self.id = id_npc
        self.nome = nome
        self.descricao = descricao
        self.hp_max = hp_max
        self.hp_atual = hp_max
        self.classe_armadura = classe_armadura
        self.atributos = atributos

        self.tags = set(tags or [])
        
        self.xp_recompensa = xp_recompensa
        self.tabela_loot = tabela_loot

        # ----------------------------------------------------------------- #
        # ----------| PSIQUE, SOCIAL, ROTINA, RELACIONAMENTO |------------- #

        self.psique = {
            "alinhamento_logico": psique.get("logica", 50),  # 0 a 100
            "percepcao_social": psique.get("percepcao", 50),
            "abertura_mudanca": psique.get("abertura", 50),
            "conhecimentos": psique.get("conhecimentos", {}),
            "tracos_personalidade": set(psique.get("tracos", [])),  # ex: ["ganancioso", "covarde"]
        }

        self.social = {
            "geografia": social.get("geografia", {
                "continente": "Valenor",
                "regiao": "Regiao Desconhecida",
                "tipo_habitat": "vila",
                "nome_localidade": "Local Desconhecido",
                "ponto_padrao": f"centro_{id_npc}"
            }),
            "profissao": social.get("profissao", "desempregado"),
            "nivel_habilidade": social.get("habilidade", 1),
            "ambicao": social.get("ambicao", "sobreviver"),
            "faccao_lealdade": social.get("faccao", "nenhuma"),
            # Mapeamento real dos nós de vivência do NPC
            "locais": social.get("locais", {
                "casa": f"casa_{self.id}",
                "trabalho": f"trabalho_{self.id}",
                "lazer": "taverna_local",
                "refeicao": "taverna_local"
            }),
            # Rotinas que mudam conforme a estação do ano
            "rotinas_por_estacao": social.get("rotinas_por_estacao", {})
        }
        # Estado dinâmico para lidar com tragédias, luto ou alertas de perigo
        self.social["estado_dinamico"] = social.get("estado_dinamico", {
            "estado_ativo": None,  # Ex: "luto_profundo", "alerta_bandidos"
            "sobrescrever_atividade": None
        })

        self.rotina = social.get(
            "rotina",
            {
                "Amanhecer": "dormir",
                "Meia-manha": "trabalhar",
                "Meio-dia": "comer",
                "Meia-tarde": "trabalhar",
                "Entardecer": "trabalhar",
                "Noite": "taverna",
                "Alta-noite": "casa",
                "Madrugada": "dormir",
            },
        )

        self.relacionamento_jogador = {
            "afinidade": 0,  # -100 (Ódio) a 100 (Amor)
            "confianca": 0,  # Afeta se ele acredita nas suas mentiras
            "respeito": 0,   # Afeta intimidação
            "medo": 0,       # Afeta se ele foge de si
            "eventos_marcantes": [],  # Lista do que o jogador fez para ele
        }

        # ---------------------------| MEMORIA |--------------------------- #
        self.memoria = {}

        # ------------------| RESISTENCIA E FRAQUEZAS |-------------------- #
        self.fraquezas = []
        self.resistencias = []

        # ---------------------------| STATUS |---------------------------- #
        self.agressivo = False
        self.fugir = False
        self.morte = False
        
        self.status_ativo = {}            
        self.bonus_dano_temporario = 0    

        # ------------------------| INVENTARIO |--------------------------- #
        self.inventario = Inventario()
        
        self.xp_recompensa = 50 
        self.tabela_loot = "loot_vazio"

    # ----------------------------------------------------------------- #

    def obter_local_atual(self, fase_atual: str, estacao_atual: str = "Primavera") -> str:
        # 1. Validação genérica de estado crítico (Anula qualquer rotina!)
        estado_critico = self.social.get("estado_dinamico", {})
        atividade_forcada = estado_critico.get("sobrescrever_atividade")
        
        if atividade_forcada:
            locais = self.social.get("locais", {})
            if atividade_forcada in ("dormir", "casa"):
                return locais.get("casa", f"casa_{self.id}")
            elif atividade_forcada == "trabalhar":
                return locais.get("trabalho", f"trabalho_{self.id}")
            return atividade_forcada 

        # 2. Verifica o Perfil Comportamental do NPC
        tipo_rotina = self.social.get("tipo_rotina", "estatica")
        
        # PERFIL C: VIAJANTE (Ignora o dia/noite, move-se pelo itinerário)
        if tipo_rotina == "transito":
            itinerario = self.social.get("itinerario", [])
            indice = self.social.get("indice_itinerario_atual", 0)
            if itinerario and indice < len(itinerario):
                return itinerario[indice]
            return "estrada_desconhecida"
            
        # Puxa a rotina base (usada para perfis Estáticos e Patrulha)
        rotinas_sazonais = self.social.get("rotinas_por_estacao", {})
        rotina_ativa = rotinas_sazonais.get(estacao_atual, self.rotina)
        atividade = rotina_ativa.get(fase_atual, "dormir")

        # PERFIL B: PATRULHEIRO (A atividade já é o nó exato do mapa!)
        if tipo_rotina == "patrulha":
            return atividade

        # PERFIL A: ESTÁTICO (Traduz a atividade genérica para um nó do mapa)
        locais = self.social.get("locais", {})
        if atividade in ("dormir", "casa"):
            return locais.get("casa", f"casa_{self.id}")
        elif atividade == "trabalhar":
            return locais.get("trabalho", f"trabalho_{self.id}")
        elif atividade in ("comer", "refeicao", "taverna"):
            return locais.get("refeicao", "taverna_local")
            
        return atividade

    def modificador(self, atributo: str) -> int:
        valor_atributo = self.atributos.get(atributo, 10)
        return (valor_atributo - 10) // 2

    def registrar_memoria(
        self,
        id_evento: str,
        causador: str,
        faccao: str = "nenhuma",
        peso_certeza: str = "fato",
        fonte: str = "presenciou",
        ilegal: bool = False,
        impacto_afinidade: int = 0,
        impacto_medo: int = 0,
        impacto_respeito: int = 0,
    ):
        tracos = self.psique["tracos_personalidade"]

        # 1. Filtro de ceticismo: ignora rumores se for desconfiado ou cético
        if peso_certeza == "rumor" and ("desconfiado" in tracos or "cetico" in tracos):
            return

        # 2. Evita registar ou aplicar impactos duplicados do mesmo evento
        if id_evento in self.memoria:
            certeza_antiga = self.memoria[id_evento]["certeza"]
            if certeza_antiga == "fato" or certeza_antiga == peso_certeza:
                return
            # Atualiza a certeza caso a nova informação seja mais forte
            self.memoria[id_evento]["certeza"] = peso_certeza
            self.memoria[id_evento]["fonte"] = fonte
        else:
            self.memoria[id_evento] = {
                "causador": causador,
                "certeza": peso_certeza,
                "fonte": fonte,
                "ilegal": ilegal,
                "faccao_lealdade": faccao,
                "impactos_base": (impacto_afinidade, impacto_medo, impacto_respeito),
            }

        # 3. Aplica os impactos emocionais ponderados pela certeza
        multiplicadores = {
            "fato": 1.0,
            "neutro": 0.5,
            "rumor": 0.25,
        }
        fator = multiplicadores.get(peso_certeza, 0.25)

        if causador == "jogador":
            nova_afinidade = self.relacionamento_jogador["afinidade"] + int(impacto_afinidade * fator)
            self.relacionamento_jogador["afinidade"] = max(-100, min(100, nova_afinidade))

            novo_medo = self.relacionamento_jogador["medo"] + int(impacto_medo * fator)
            self.relacionamento_jogador["medo"] = max(0, min(100, novo_medo))

            novo_respeito = self.relacionamento_jogador["respeito"] + int(impacto_respeito * fator)
            self.relacionamento_jogador["respeito"] = max(-100, min(100, novo_respeito))

            if id_evento not in self.relacionamento_jogador["eventos_marcantes"]:
                self.relacionamento_jogador["eventos_marcantes"].append(id_evento)

        self.avaliar_estado_emocional()

    def avaliar_estado_emocional(self):
        tracos = self.psique["tracos_personalidade"]

        if self.relacionamento_jogador["medo"] >= 80 or (
            self.hp_atual <= self.hp_max * 0.3 and "covarde" in tracos
        ):
            self.fugir = True
            self.agressivo = False
            print(f"{self.nome} entrou em pânico e tenta fugir!")

        if not self.fugir:
            if self.relacionamento_jogador["afinidade"] <= -50:
                self.agressivo = True
                print(f"{self.nome} não está a gostar das suas atitudes! Fique atento!")

    def receber_dano(self, quantidade: int, tipo_dano: str = "concussao", causador: str = "desconhecido") -> int:
        if quantidade <= 0:
            return 0

        dano_real = quantidade

        if tipo_dano in self.fraquezas:
            dano_real = quantidade * 2
            print(f"Acerto vulnerável! O dano de {tipo_dano} foi duplicado!")
        elif tipo_dano in self.resistencias:
            dano_real = max(1, quantidade // 2)
            print(f"Resistência! O dano de {tipo_dano} foi reduzido para metade.")

        self.hp_atual = max(0, self.hp_atual - dano_real)

        if self.hp_atual == 0:
            self.agressivo = False
            self.fugir = False
            self.morte = True
            print(f"{self.nome} caiu.")
        else:
            self.registrar_memoria(
                id_evento="foi_atacado",
                causador=causador,
                peso_certeza="fato",
                fonte="presenciou",
                impacto_afinidade=-30,
                impacto_medo=15,
            )

        return dano_real

    def espalhar_fofoca(self, outro_npc, id_evento: str) -> bool:
        # 1. Validações básicas
        if id_evento not in self.memoria:
            return False

        if outro_npc.morte or outro_npc.agressivo:
            return False

        memoria = self.memoria[id_evento]
        tracos = self.psique["tracos_personalidade"]
        tracos_outro = outro_npc.psique["tracos_personalidade"]

        # 2. Filtros de personalidade e lealdade ao jogador
        if "leal" in tracos or "reservado" in tracos:
            if memoria["causador"] == "jogador" and self.relacionamento_jogador["afinidade"] >= 0:
                return False

        # 3. Filtro de autopreservação e relação com guardas (crimes)
        if memoria["ilegal"]:
            compromete_npc = (
                memoria["causador"] == self.id
                or (
                    memoria["faccao_lealdade"] == self.social["faccao_lealdade"]
                    and self.social["faccao_lealdade"] != "nenhuma"
                )
            )
            if compromete_npc:
                if outro_npc.social["profissao"] == "guarda":
                    guarda_aliado = (
                        "corrupto" in tracos_outro
                        or (
                            outro_npc.social["faccao_lealdade"] == self.social["faccao_lealdade"]
                            and self.social["faccao_lealdade"] != "nenhuma"
                        )
                    )
                    if not guarda_aliado:
                        return False
                else:
                    return False

        # 4. Degradação da certeza ("Telefone sem fio")
        if memoria["certeza"] == "fato":
            nova_certeza = "neutro"
        else:
            nova_certeza = "rumor"

        # 5. Modificadores de exagero ou ponderação na transmissão
        af, med, resp = memoria["impactos_base"]
        if "fofoqueiro" in tracos or "exagerado" in tracos:
            af = int(af * 1.25)
            med = int(med * 1.25)
            resp = int(resp * 1.25)
        elif "moderado" in tracos or "ponderado" in tracos:
            af = int(af * 0.25)
            med = int(med * 0.25)
            resp = int(resp * 0.25)

        outro_npc.registrar_memoria(
            id_evento=id_evento,
            causador=memoria["causador"],
            faccao=memoria["faccao_lealdade"],
            peso_certeza=nova_certeza,
            fonte=self.nome,
            ilegal=memoria["ilegal"],
            impacto_afinidade=af,
            impacto_medo=med,
            impacto_respeito=resp,
        )

        return True

    def compartilhar_conhecimento(self, topico: str) -> str:
        conhecimentos = self.psique.get("conhecimentos", {})
        if topico not in conhecimentos:
            return f"{self.nome} não sabe nada sobre '{topico}'."

        info = conhecimentos[topico]
        dificuldade = info.get("dificuldade", 30)

        disposicao_positiva = (
            self.relacionamento_jogador["afinidade"] + self.relacionamento_jogador["confianca"]
        )
        disposicao_coercao = (
            self.relacionamento_jogador["medo"] + self.relacionamento_jogador["respeito"]
        )
        disposicao_total = max(disposicao_positiva, disposicao_coercao)

        if disposicao_total >= dificuldade:
            return info.get("texto", "")

        return f"{self.nome} parece saber de algo, mas não confia em si o suficiente para contar."

    @classmethod
    def do_dict(cls, dados: dict):
        # Cria a instância
        instancia = cls(
            id_npc=dados.get("id", "npc_desconhecido"),
            nome=dados.get("nome", "Desconhecido"),
            descricao=dados.get("descricao", ""),
            hp_max=int(dados.get("hp_max", 10)),
            classe_armadura=int(dados.get("classe_armadura", 10)),
            atributos=dados.get("atributos", {}),
            psique=dados.get("psique", {}),
            social=dados.get("social", {}),
            tags=dados.get("tags", [])
        )

        instancia.xp_recompensa = int(dados.get("xp_recompensa", 50))
        instancia.tabela_loot = dados.get("tabela_loot", "loot_vazio")
        
        return instancia

    def aplicar_status(self, id_status: str, efeitos: dict, duracao: int):
        """Lê o dicionário do JSON e aplica os bónus na ficha."""
        # Se já tiver o status, apenas renova a duração
        if id_status in self.status_ativo:
            self.status_ativo[id_status]["duracao_restante"] = duracao
            return
            
        self.status_ativo[id_status] = {
            "efeitos": efeitos,
            "duracao_restante": duracao
        }
        
        # 1. Injeta resistências
        for res in efeitos.get("resistencias_ganhas", []):
            self.resistencias.append(res)
            
        # 2. Injeta bónus de dano
        self.bonus_dano_temporario += efeitos.get("bonus_dano_fisico", 0)
        
        # 3. Injeta bónus de CA (Armadura)
        if "bonus_ca" in efeitos:
            self.classe_armadura += efeitos["bonus_ca"]
            
        print(f"🔥 {self.nome} foi afetado por {id_status.replace('_', ' ').title()}!")

    def remover_status(self, id_status: str):
        """Reverte exatamente os bónus que foram dados."""
        if id_status not in self.status_ativo:
            return
            
        efeitos = self.status_ativo[id_status]["efeitos"]
        
        for res in efeitos.get("resistencias_ganhas", []):
            if res in self.resistencias:
                self.resistencias.remove(res)
                
        self.bonus_dano_temporario -= efeitos.get("bonus_dano_fisico", 0)
        
        if "bonus_ca" in efeitos:
            self.classe_armadura -= efeitos["bonus_ca"]
            
        del self.status_ativo[id_status]
        print(f"💨 O efeito de {id_status.replace('_', ' ').title()} sobre {self.nome} dissipou-se.")

    def processar_turnos_status(self):
        """Chamado pelo Motor de Combate no final do turno deste personagem."""
        # Copiamos as chaves para uma lista para podermos apagar itens do dicionário durante o loop sem erro
        status_para_verificar = list(self.status_ativo.keys())
        
        for id_status in status_para_verificar:
            duracao = self.status_ativo[id_status]["duracao_restante"]
            
            # Duração -1 pode significar "infinito" (ex: maldições que só saem com magia)
            if duracao > 0:
                self.status_ativo[id_status]["duracao_restante"] -= 1
                
                # Se o tempo acabou, a própria ficha limpa o status!
                if self.status_ativo[id_status]["duracao_restante"] <= 0:
                    self.remover_status(id_status)