from models.itens import Inventario
from core.banco_dados import BancoDeDados

class Jogador():
    
    def __init__(self, nome, especie, classe, antecedente, atributo=True):
    #-----------------| EXIBIÇÃO |--------------------#    
        self.id = "jogador"  
        self.nome = nome # NOME JOGADOR
        self.especie = especie.get("nome", "Desconhecido") # NOME ESPECIE
        self.classe = classe.get("nome", "Desconhecido") # NOME CLASSE
        self.antecedente = antecedente.get("nome", "Desconhecido") # NOME ANTECEDENTE
        
        self.classe_id = classe.get("id", "desconhecido")
    #--------------------------------------------------# 
    #-----------------| ATRIBUTOS |--------------------# 
        if atributo == True:
            self.atributos = classe.get("atributos_padrao", {}).copy() #-------| ATRIBUTOS PADRÃO
        else: 
            self.atributos = atributo
        
        self.bonus_atributos_antecedente = antecedente.get("bonus_atributos", {}) #-------| ATRIBUTO ANTECEDENTE     
        for atributo, valor in self.bonus_atributos_antecedente.items():
            if atributo in self.atributos:
                self.atributos[atributo] += valor  
                
        self.atributo_conjuracao = classe.get("atributo_conjuracao", "inteligencia")
        
    #--------------------------------------------------#     
    #-----------------| VIDA E XP |--------------------#
        self.dado_de_vida = classe.get("dado_de_vida", "1d6")
        partes = self.dado_de_vida.split("d")     
        self.hp_max = max(1, int(partes[1]) + self.modificador("constituicao")) #-------| HP INICIAL MAX
              
        self.hp_atual = self.hp_max #-------| HP INICIAL ATUAL
        
        
        self.nivel = 1 #-------| NIVEL 
        self.xp = 0 #-------| XP
        self.xp_necessario = self.calcular_xp_prox_nivel()
        
    #---------------------------------------------------#
    #-------| PROFICIENCIA E PERCEPÇÃO PASSIVA E CA |-------#            
        self.bonus_proficiencia = 2
       
        self.classe_armadura = 10 + self.modificador("destreza")
        self.percepcao_passiva = 10 + self.modificador("sabedoria")
    #---------------------------------------------------#
    #------------------| PERICIAS |---------------------# 
        pericias_antecedente = set(antecedente.get("proficiencia_pericias", []))
        pericias_classe = set(classe.get("proficiencia_pericias", []))

        self.proficiencia_pericias = pericias_classe | pericias_antecedente
                #-| ARMADURAS |-#
        self.proficiencia_armadura = set(classe.get("proficiencia_armadura", []))
                
                #-| ESCUDO |-#    
        self.proficiencia_escudo = (classe.get("proficiencia_escudo", False))
        
                #-| ARMAS |-#    
        self.proficiencia_armas = set(classe.get("proficiencia_armas", []))
    #---------------------------------------------------#
    #------------------| SALVAGUARDAS |------------------#  
        self.salvaguarda_contra_morte = {
            "Sucesso": 0,
            "Falha": 0
        }
        self.salvaguarda_atributo = set(classe.get("proficiencia_salvaguarda", []))
    #---------------------------------------------------#
    #------------------| INVENTARIO E EQUIPAMENTO |--------------------# 
        self.inventario = Inventario()
        
        self.arma_equipada = None
        
        self.armadura_equipada = None
        
        self.escudo_equipado = None
        
        self.acessorios_equipados = []
    
    #------------------| STATUS DO PERSONAGEM |--------------------# 
    
        self.status_ativo = {} # Agora é um dicionário!
        self.bonus_dano_temporario = 0
    
    #------------------| HABILIDADES E MAGIAS |--------------------# 
    
        self.habilidades = []
        self.truques = []
        self.espacos_magia = {
            1: {"total": 0, "disponiveis": 0}
        }
        
        # Importa o Banco de Dados (podes colocar o import no topo do ficheiro ou dentro do método)
        from core.banco_dados import BancoDeDados
        
        # Pede os dados da classe ao Banco de Dados (ex: "barbaro")
        dados_classe = BancoDeDados.obter_classe(self.classe.lower()) # Assegura que o nome da classe casa com o ID do JSON
        
        # Pula para a progressão do nível 1
        progresso_nivel_1 = dados_classe.get("progressao_nivel", {}).get("1", {})
        
        # Atualiza o bónus de proficiência base do nível 1
        self.bonus_proficiencia = progresso_nivel_1.get("bonus_proficiencia", 2)
        
        # Carrega os IDs das habilidades iniciais e clona-as via Banco de Dados
        ids_habilidades_iniciais = progresso_nivel_1.get("habilidades_desbloqueadas", [])
        for hab_id in ids_habilidades_iniciais:
            hab_obj = BancoDeDados.obter_habilidade(hab_id)
            if hab_obj:
                self.habilidades.append(hab_obj)
    
    #------------------| RESISTENCIA E FRAQUEZAS |--------------------#
    
        self.fraquezas = []
        
        self.resistencias = []
    
    def calcular_modificador_ataque_magico(self) -> int:
        return self.modificador(self.atributo_conjuracao) + self.bonus_proficiencia

    def calcular_cd_magia(self) -> int:
        return 8 + self.bonus_proficiencia + self.modificador(self.atributo_conjuracao)    
    
    def descanso_curto(self):
      """Recupera vida e notifica tudo o que recarrega em descanso curto."""
      cura = max(1, self.hp_max // 2)
      self.curar(cura)

      # 1. Espaços de magia (se mantiver a sua regra caseira de recuperar metade)
      for nivel, dados in self.espacos_magia.items():
        recuperar = max(1, dados["total"] // 2)
        dados["disponiveis"] = min(
            dados["total"], dados["disponiveis"] + recuperar
        )

      # 2. Habilidades ativas
      for hab in self.habilidades:
        hab.recarregar("curto")

      for dados_item in self.inventario.itens.values():
        item_obj = dados_item["objeto"]
        if hasattr(item_obj, "recarregar"):
            item_obj.recarregar("curto") # ou "longo"

        print(f"{self.nome} realizou um descanso curto!")

    def descanso_longo(self):
        self.hp_atual = self.hp_max

        for nivel, dados in self.espacos_magia.items():
            dados["disponiveis"] = dados["total"]

        for hab in self.habilidades:
            hab.recarregar("longo")

        for dados_item in self.inventario.itens.values():
            item_obj = dados_item["objeto"]
            if hasattr(item_obj, "recarregar"):
                item_obj.recarregar("curto") # ou "longo" 

        print(f"{self.nome} realizou um descanso longo. Recursos renovados!")
    
    def tem_espaco_magia(self, nivel: int) -> bool:
        """Apenas consulta se há espaço disponível para o nível solicitado."""
        if nivel == 0:
            return True  # Truques não consomem espaço

        dados_nivel = self.espacos_magia.get(nivel)
        if dados_nivel and dados_nivel.get("disponiveis", 0) > 0:
            return True

        return False

    def gastar_espaco_magia(self, nivel: int) -> bool:
        """Consome efetivamente 1 espaço de magia do nível especificado."""
        if nivel == 0:
            return True  # Truque tem custo zero

        if self.tem_espaco_magia(nivel):
            self.espacos_magia[nivel]["disponiveis"] -= 1
            restantes = self.espacos_magia[nivel]["disponiveis"]
            print(
                f"{self.nome} gastou 1 espaço de magia de nível {nivel}."
                f" Restantes: {restantes}"
            )
            return True

        print(
            f"O {self.nome} não tem espaço de magia de nível {nivel} disponível!"
        )
        return False
            
    def curar(self, quantidade: int):
        if quantidade <= 0:
            return 0

        self.hp_atual = min(self.hp_max, self.hp_atual + quantidade) 
        print(f"O {self.nome} curou {quantidade} pontos de vida!")
         
    def receber_dano(self, quantidade: int, tipo_dano: str = "concussao", efeito = None) -> int:
        if quantidade <= 0:
            return 0
        
        # 1. Dano base padrão
        dano_real = quantidade
        
        # 2. Modificadores de tipo de dano
        if tipo_dano in self.fraquezas:
            dano_real = quantidade * 2
            print(f"Acerto vulnerável! O dano de {tipo_dano} foi duplicado!")
        elif tipo_dano in self.resistencias:
            dano_real = max(1, quantidade // 2)
            print(f"Resistência! O dano de {tipo_dano} foi reduzido a metade.")
            
        # 3. Aplicação do dano no HP
        self.hp_atual = max(0, self.hp_atual - dano_real)
        print(f"{self.nome} sofreu {dano_real} de dano {tipo_dano} (HP: {self.hp_atual}/{self.hp_max}).")
        
        # 4. Verificação de estado
        if self.hp_atual == 0:
            print(f"O {self.nome} caiu a 0 pontos de vida e está inconsciente!")
            
        return dano_real
    
    def equipar_arma(self, nova_arma):
        # Se a arma requer as duas mãos e o jogador tem um escudo equipado, avisa ou desequipa o escudo
        if "duas_maos" in nova_arma.propriedades and self.escudo_equipado:
            print(f"Ao equipar {nova_arma.nome} (duas mãos), o escudo foi desequipado.")
            self.escudo_equipado = None
            self.atualizar_ca()
            
        self.arma_equipada = nova_arma    
    
    def equipar_armadura(self, nova_armadura):
        self.armadura_equipada = nova_armadura
        self.atualizar_ca()
        
    def equipar_escudo(self, novo_escudo):
        if self.arma_equipada and "duas_maos" in self.arma_equipada.propriedades:
            print(
            f"Não é possível equipar escudo usando {self.arma_equipada.nome}"
            " com a propriedade (duas mãos)!"
            )
            return False
        
        self.escudo_equipado = novo_escudo
        self.atualizar_ca()
        return True
    
    def atualizar_ca(self):
        if self.armadura_equipada:
            ca = self.armadura_equipada.calcula_ca(self)
        else:
            ca = 10 + self.modificador("destreza")
          
        if self.escudo_equipado:
            ca += self.escudo_equipado.bonus_ca
        self.classe_armadura = ca    
            
    def modificador(self, atributo: str) -> int: 
        valor = self.atributos.get(atributo, 10)
        return (valor - 10) // 2     
    
    def subir_nivel(self):
        """Avança o personagem para o próximo nível e desbloqueia recompensas da classe."""
        from core.banco_dados import BancoDeDados
        
        self.nivel += 1
        print(f"\n🎉 PARABÉNS! {self.nome} alcançou o Nível {self.nivel}!")
        
        # 1. Aumenta o HP máximo (garantido independentemente do JSON de progressão)
        partes_dado = self.dado_de_vida.split("d")
        lados_dado = int(partes_dado[1])
        # Regra simplificada de ganho de HP por nível: metade do dado + mod constituição
        ganho_hp = max(1, (lados_dado // 2) + 1 + self.modificador("constituicao"))
        self.hp_max += ganho_hp
        self.hp_atual = self.hp_max # Cura total ao subir de nível (clássico de D&D)
        print(f"❤️ O seu HP Máximo aumentou em {ganho_hp} pontos! (Novo HP: {self.hp_max})")

        # 2. Busca o JSON da classe pelo ID técnico (ex: "barbaro") para desbloquear habilidades
        dados_classe = BancoDeDados.obter_classe(self.classe_id)
        progresso_atual = dados_classe.get("progressao_nivel", {}).get(str(self.nivel), {})
        
        if not progresso_atual:
            print("Aviso: Nenhuma habilidade extra ou bónus de proficiência previstos para este nível.")
            return
            
        # 3. Atualiza bónus de proficiência se houver alteração
        if "bonus_proficiencia" in progresso_atual:
            self.bonus_proficiencia = progresso_atual["bonus_proficiencia"]
            print(f"O seu Bónus de Proficiência subiu para +{self.bonus_proficiencia}!")
            
        # 4. Desbloqueia novas habilidades marciais
        novas_habilidades = progresso_atual.get("habilidades_desbloqueadas", [])
        for hab_id in novas_habilidades:
            nova_hab = BancoDeDados.obter_habilidade(hab_id)
            if nova_hab:
                self.habilidades.append(nova_hab)
                print(f"⚔️ Nova Habilidade Desbloqueada: {nova_hab.nome} - {nova_hab.descricao}")
                
        # 5. Desbloqueia espaços de magia (caso seja uma classe conjuradora)
        espacos_novos = progresso_atual.get("espacos_magia", {})
        for nivel_magia, qtd in espacos_novos.items():
            nivel_int = int(nivel_magia)
            if nivel_int not in self.espacos_magia:
                self.espacos_magia[nivel_int] = {"total": 0, "disponiveis": 0}
            
            self.espacos_magia[nivel_int]["total"] += qtd
            self.espacos_magia[nivel_int]["disponiveis"] += qtd
            print(f"✨ Ganhou {qtd} espaço(s) de magia de nível {nivel_int}!")
            
    def equipar_acessorio(self, acessorio):
        # Validações de espaço (ex: só tem 2 dedos para anéis)
        
        # Aplica os bónus reais nos atributos da ficha do jogador
        for atributo, valor in acessorio.bonus_atributos.items():
            if atributo in self.atributos:
                self.atributos[atributo] += valor
                
        self.acessorios_equipados.append(acessorio)
        print(f"💍 Você equipou {acessorio.nome} e sentiu o seu poder fluir!")

    def desequipar_acessorio(self, acessorio):
        # Retira os bónus
        for atributo, valor in acessorio.bonus_atributos.items():
            if atributo in self.atributos:
                self.atributos[atributo] -= valor
                
        self.acessorios_equipados.remove(acessorio)
    
    def aplicar_buff(self, id_buff: str, efeitos: dict):
        """Lê o dicionário do JSON e aplica os bónus na ficha do personagem."""
        # Se já tiver o buff, não aplica de novo
        if id_buff in self.status_ativo:
            return
            
        self.status_ativo[id_buff] = efeitos
        
        # Injeta as resistências na ficha
        for res in efeitos.get("resistencias_ganhas", []):
            self.resistencias.append(res)
            
        # Injeta bónus de dano (precisamos de criar self.bonus_dano_temporario = 0 no __init__)
        self.bonus_dano_temporario += efeitos.get("bonus_dano_fisico", 0)
        
        print(f"🔥 {self.nome} ativou {id_buff.replace('_', ' ').title()}! Ficha atualizada.")

    def remover_buff(self, id_buff: str):
        """Lê o dicionário guardado e retira exatamente o que foi dado."""
        if id_buff not in self.status_ativo:
            return
            
        efeitos = self.status_ativo[id_buff]
        
        # Remove as resistências da ficha
        for res in efeitos.get("resistencias_ganhas", []):
            if res in self.resistencias:
                self.resistencias.remove(res)
                
        # Remove o bónus de dano
        self.bonus_dano_temporario -= efeitos.get("bonus_dano_fisico", 0)
        
        # Apaga o status da lista
        del self.status_ativo[id_buff]
        print(f"💨 O efeito de {id_buff.replace('_', ' ').title()} passou. {self.nome} volta ao normal.")
        
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

    def calcular_xp_prox_nivel(self) -> int:
        """Tabela de XP baseada nas regras clássicas (D&D 5e)."""
        tabela_xp = {
            1: 300, 2: 900, 3: 2700, 4: 6500, 5: 14000,
            6: 23000, 7: 34000, 8: 48000, 9: 64000, 10: 85000
        }
        # Se passar do nível 10, exige um valor fixo absurdo ou calcula progressão
        return tabela_xp.get(self.nivel, self.nivel * 10000)

    def ganhar_xp(self, quantidade: int):
        if quantidade <= 0: return
        self.xp += quantidade
        print(f"🌟 Recebeste {quantidade} XP! (Total: {self.xp}/{self.xp_necessario})")
        
        # Usa um while caso o jogador ganhe muito XP de uma vez e suba 2 níveis seguidos!
        while self.xp >= self.xp_necessario:
            self.subir_nivel()
            self.xp_necessario = self.calcular_xp_prox_nivel()