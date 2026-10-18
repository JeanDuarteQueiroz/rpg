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
    ):
        self.id = id_npc
        self.nome = nome
        self.descricao = descricao
        self.hp_max = hp_max
        self.hp_atual = hp_max
        self.classe_armadura = classe_armadura
        self.atributos = atributos

        self.tags = set(tags or [])

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
            "profissao": social.get("profissao", "desempregado"),
            "nivel_habilidade": social.get("habilidade", 1),
            "ambicao": social.get("ambicao", "sobreviver"),
            "faccao_lealdade": social.get("faccao", "nenhuma"),
        }

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

        # ------------------------| INVENTARIO |--------------------------- #
        self.inventario = Inventario()

    # ----------------------------------------------------------------- #

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
        return cls(
            id_npc=dados.get("id", "npc_desconhecido"),
            nome=dados.get("nome", "Desconhecido"),
            descricao=dados.get("descricao", ""),
            hp_max=int(dados.get("hp_max", 10)),
            classe_armadura=int(dados.get("classe_armadura", 10)),
            atributos=dados.get("atributos", {}),
            psique=dados.get("psique", {}),
            social=dados.get("social", {}),
            tags=dados.get("tags", []),
        )