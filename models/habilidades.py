class Habilidade():
    def __init__(
        self,
        id_habilidade: str,
        nome: str,
        descricao: str,
        tipo: str,
        tipo_recarga: str = "nenhum",  
        usos_max: int = 0,
        tipo_efeito: str = "", # "cura", "dano", "status"
        dados_efeito: str = "" # "1d10", "furia", "cego"
    ):
        self.id = id_habilidade
        self.nome = nome
        self.descricao = descricao
        self.tipo = tipo
        self.tipo_recarga = tipo_recarga
        self.usos_max = usos_max
        self.usos_disponiveis = usos_max
        
        self.tipo_efeito = tipo_efeito
        self.dados_efeito = dados_efeito
        
    def recarregar(self, tipo_descanso: str):
        """Restaura usos se o tipo de descanso for compatível."""
        if self.usos_max == 0:
            return

        if self.tipo_recarga == "curto" and tipo_descanso in ("curto", "longo"):
             self.usos_disponiveis = self.usos_max
        elif self.tipo_recarga == "longo" and tipo_descanso == "longo":
             self.usos_disponiveis = self.usos_max    
             
    def executar(self, usuario, alvo, expressao_rolagem_func):
        """Método para habilidades não-mágicas (físicas ou de classe)"""
        # 1. Validação de recursos (Usos)
        if self.usos_max > 0 and self.usos_disponiveis <= 0:
            print(f"{usuario.nome} esgotou os usos de {self.nome}! Precisa de um descanso {self.tipo_recarga}.")
            return False

        # 2. Consumo
        if self.usos_max > 0:
            self.usos_disponiveis -= 1
            
        print(f"\n{usuario.nome} utiliza a habilidade: {self.nome}!")
        
        # 3. Aplicação do Efeito Base
        if self.tipo_efeito == "cura" and self.dados_efeito:
            valor = expressao_rolagem_func(self.dados_efeito, "total")
            alvo.curar(valor)
        
        elif self.tipo_efeito == "status":
            # Adiciona o status (ex: "furia") à lista de status ativos do personagem
            if self.dados_efeito not in usuario.status_ativo:
                usuario.status_ativo.append(self.dados_efeito)
                print(f"{usuario.nome} entra no estado: {self.dados_efeito.upper()}!")
        
        elif self.tipo_efeito == "buff_temporario":
            # Passa o ID da habilidade e o dicionário de efeitos para o alvo/usuário
            usuario.aplicar_buff(self.id, self.dados_efeito)
            
        elif self.tipo_efeito == "aplicar_status":
            # O JSON deve dizer quanto tempo dura. Ex: 10 turnos
            # Se for uma magia lançada no inimigo (alvo), aplica no alvo. Se for buff, aplica no usuario.
            alvo_do_efeito = alvo if alvo else usuario
            duracao = self.dados_efeito.get("duracao_turnos", 1)
            
            alvo_do_efeito.aplicar_status(self.id, self.dados_efeito, duracao)
            
        elif self.tipo_efeito == "remover_status":
            # dados_efeito aqui seria uma string. Ex: "envenenado"
            alvo.remover_status(self.dados_efeito)
            print(f"✨ {usuario.nome} curou o estado '{self.dados_efeito}' de {alvo.nome}!")
            
        # (Se for dano direto, aplicaria aqui parecido com a cura)
        return True

    @classmethod
    def do_dict(cls, dados: dict):
        return cls(
            id_habilidade=dados.get("id", "desconhecida"),
            nome=dados.get("nome", "Habilidade Sem Nome"),
            descricao=dados.get("descricao", ""),
            tipo=dados.get("tipo", "habilidade_classe"),
            tipo_recarga=dados.get("tipo_recarga", "nenhum"),
            usos_max=int(dados.get("usos_max", 0)),
            tipo_efeito=dados.get("tipo_efeito", ""),
            dados_efeito=dados.get("dados_efeito", "")
        )   
    
class Magia(Habilidade):
    def __init__(
        self,
        id_habilidade: str,
        nome: str,
        descricao: str,
        tipo: str,
        nivel: int,
        escola: str,
        tipo_resolucao: str,
        atributo_salvaguarda: str = None,
        dados_efeito: str = "",
        tipo_dano: str = "",
    ):
        # Passa tipo_recarga="nenhum" e usos_max=0 para a classe-mãe
        super().__init__(
            id_habilidade,
            nome,
            descricao,
            tipo,
            tipo_recarga="nenhum",
            usos_max=0,
        )
        self.nivel = nivel
        self.escola = escola
        self.tipo_resolucao = tipo_resolucao 
        self.atributo_salvaguarda = atributo_salvaguarda  
        self.dados_efeito = dados_efeito  
        self.tipo_dano = tipo_dano 

    @classmethod
    def do_dict(cls, dados: dict):
        return cls(
            id_habilidade=dados.get("id", "desconhecida"),
            nome=dados.get("nome", "Magia Sem Nome"),
            descricao=dados.get("descricao", "Uma magia"),
            tipo=dados.get("tipo", "magia"),
            nivel=int(dados.get("nivel", 0)),
            escola=dados.get("escola", ""),
            tipo_resolucao=dados.get("tipo_resolucao", "ataque"),
            atributo_salvaguarda=dados.get("atributo_salvaguarda", None),
            dados_efeito=dados.get("dados_efeito", ""),
            tipo_dano=dados.get("tipo_dano", ""),
        )
    
    def executar(self, conjurador, alvo, expressao_rolagem_func):
        # Validação prévia de recursos:
        if not conjurador.tem_espaco_magia(self.nivel):
            print(
                f"{conjurador.nome} não possui espaços de magia de nível"
                f" {self.nivel} disponíveis!"
            )
            return False

        # Consome o espaço de magia (se nível > 0)
        conjurador.gastar_espaco_magia(self.nivel)

        print(f"\n{conjurador.nome} conjura {self.nome}!")

        # 1. Se for CURA
        if self.tipo_dano.lower() == "cura":
            valor_cura = expressao_rolagem_func(self.dados_efeito, "total")
            alvo.curar(valor_cura)
            print(f"{alvo.nome} recuperou {valor_cura} pontos de vida!")
            return

        # 2. Se for ATAQUE MÁGICO CONTRA CA
        if self.tipo_resolucao == "ataque":
            mod_ataque = conjurador.calcular_modificador_ataque_magico()
            d20 = expressao_rolagem_func("1d20", "total")
            total_acerto = d20 + mod_ataque
            
            print(f"Rolagem de ataque: {d20} + {mod_ataque} = {total_acerto} vs CA {alvo.classe_armadura}")
            
            if total_acerto >= alvo.classe_armadura:
                dano = expressao_rolagem_func(self.dados_efeito, "total")
                print(f"Acerto! {self.nome} causou {dano} de dano {self.tipo_dano} a {alvo.nome}.")
                alvo.receber_dano(dano, self.tipo_dano)
            else:
                print("O ataque errou!")

        # 3. Se for SALVAGUARDA (Saving Throw)
        elif self.tipo_resolucao == "salvaguarda":
            cd = conjurador.calcular_cd_magia()
            mod_resistencia = alvo.modificador(self.atributo_salvaguarda)
            
            # Se o alvo tiver proficiência na salvaguarda, soma a proficiência
            if self.atributo_salvaguarda in alvo.salvaguarda_atributo:
                mod_resistencia += alvo.bonus_proficiencia
                
            d20 = expressao_rolagem_func("1d20", "total")
            total_salvaguarda = d20 + mod_resistencia
            
            print(f"{alvo.nome} tenta salvaguarda de {self.atributo_salvaguarda.title()}: {d20} + {mod_resistencia} = {total_salvaguarda} vs CD {cd}")
            
            dano = expressao_rolagem_func(self.dados_efeito, "total")
            if total_salvaguarda >= cd:
                # Na regra clássica do D&D, quem passa toma metade do dano
                dano_reduzido = dano // 2
                print(f"Sucesso na salvaguarda! Dano reduzido pela metade: {dano_reduzido} de dano {self.tipo_dano}.")
                alvo.receber_dano(dano_reduzido, self.tipo_dano)
            else:
                print(f"Falha na salvaguarda! {alvo.nome} sofreu {dano} de dano {self.tipo_dano}.")
                alvo.receber_dano(dano, self.tipo_dano)

        elif self.tipo_efeito == "aplicar_status":
            # O JSON deve dizer quanto tempo dura. Ex: 10 turnos
            # Se for uma magia lançada no inimigo (alvo), aplica no alvo. Se for buff, aplica no usuario.
            alvo_do_efeito = alvo if alvo else conjurador
            duracao = self.dados_efeito.get("duracao_turnos", 1)
            
            alvo_do_efeito.aplicar_status(self.id, self.dados_efeito, duracao)
            
        elif self.tipo_efeito == "remover_status":
            # dados_efeito aqui seria uma string. Ex: "envenenado"
            alvo.remover_status(self.dados_efeito)
            print(f"✨ {conjurador.nome} curou o estado '{self.dados_efeito}' de {alvo.nome}!")