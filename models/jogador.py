class Jogador():
    
    def modificador(self, atributo: str) -> int: 
        valor = self.atributos.get(atributo, 10)
        return (valor - 10) // 2     
    
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
           
            #---------------| MODIFICADORES |------------------#  
        
    #--------------------------------------------------#     
    #-----------------| VIDA E XP |--------------------#     
        self.hp_max = classe.get("dado_de_vida", 1) #-------| HP INICIAL MAX
        self.hp_atual = self.hp_max #-------| HP INICIAL ATUAL
        
        self.nivel = 1 #-------| NIVEL 
        self.xp = 0 #-------| XP
        
    #---------------------------------------------------#
    #-------| PROEFICIENCIA E PERCEPÇÃO PASSIVA E CA |-------#            
        self.bonus_proeficiencia = 2
       
        self.classe_armadura = 10 + self.modificador("destreza")
        self.percepcao_passiva = 10 + self.modificador("sabedoria")
    #---------------------------------------------------#
    #------------------| PERICIAS |---------------------# 
        pericias_antecedente = set(antecedente.get("proeficiencia_pericias", []))
        pericias_classe = set(classe.get("proeficiencia_pericias", []))

        self.proeficiencia_pericias = pericias_classe | pericias_antecedente
                #-| ARMADURAS |-#
        self.proeficiencia_armadura = set(classe.get("proeficiencia_armadura", []))
                
                #-| ESCUDO |-#    
        self.proeficiencia_escudo = (classe.get("proeficiencia_escudo", False))
        
                #-| ARMAS |-#    
        self.proeficiencia_armas = set(classe.get("proeficiencia_armas", []))
    #---------------------------------------------------#
    #------------------| SALVAGUARDAS |------------------#  
        self.salvaguarda_contra_morte = {
            "Sucesso": 0,
            "Falha": 0
        }
        self.salvaguarda_atributo = set(classe.get("proeficiencia_salvaguarda", []))
    #---------------------------------------------------#
    #------------------| INVENTARIO E EQUIPAMENTO |--------------------# 
        self.armas = []
        
        self.arma_equipada = None
        
        self.armadura_equipada = None
    
    #------------------| STATUS DO PERSONAGEM |--------------------# 
    
        self.status_ativo = []
    
    #------------------| HABILIDADES E MAGIAS |--------------------# 
    
        self.habilidades = []
        
        self.espacos_magia = {
            
        }
        
        self.truques = []