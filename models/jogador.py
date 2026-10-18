from models.itens import Inventario

class Jogador():
    
    def __init__(self, nome, especie, classe, antecedente, atributo=True):
    #-----------------| EXIBIÇÃO |--------------------#      
        self.nome = nome # NOME JOGADOR
        self.especie = especie.get("nome", "Desconhecido") # NOME ESPECIE
        self.classe = classe.get("nome", "Desconhecido") # NOME CLASSE
        self.antecedente = antecedente.get("nome", "Desconhecido") # NOME ANTECEDENTE
        
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
    
    #------------------| STATUS DO PERSONAGEM |--------------------# 
    
        self.status_ativo = []
    
    #------------------| HABILIDADES E MAGIAS |--------------------# 
    
        self.habilidades = []
        
        self.espacos_magia = {
            1:{"total": 0, "disponiveis": 0}
        }
        
        self.truques = []
    
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
    
    