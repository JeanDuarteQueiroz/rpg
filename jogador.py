import time
import dados

from utilitario import carregar_dados_json, limpar_tela, espera_jogador, menu_pronto_jogar
from antecedentes.antecedentes import exibir_menu_antecedentes, escolher_antecedente
from classes.classes import exibir_menu_classes, escolher_classe, sortear_atributos
from especies.especies import exibir_menu_especies, escolher_especies

# ESPECIES #
humano_dados = carregar_dados_json("especies/humano.json")
anao_dados = carregar_dados_json("especies/anao.json")
elfo_dados = carregar_dados_json("especies/elfo.json")

lista_especies = [
    humano_dados,
    anao_dados,
    elfo_dados
]

# CLASSE #
barbaro_dados = carregar_dados_json("classes/barbaro.json")
clerigo_dados = carregar_dados_json("classes/clerigo.json")
mago_dados = carregar_dados_json("classes/mago.json")

lista_classes = [
    barbaro_dados,
    clerigo_dados,
    mago_dados
]

# ANTECEDENTE #

nobre_dados = carregar_dados_json("antecedentes/nobre.json")
acolito_dados = carregar_dados_json("antecedentes/acolito.json")
andarilho_dados = carregar_dados_json("antecedentes/andarilho.json")
eremita_dados = carregar_dados_json("antecedentes/eremita.json")
escriba_dados = carregar_dados_json("antecedentes/escriba.json")
guarda_dados = carregar_dados_json("antecedentes/guarda.json")
guia_dados = carregar_dados_json("antecedentes/guia.json")
mercador_dados = carregar_dados_json("antecedentes/mercador.json")

lista_antecedentes = [
        acolito_dados,
        andarilho_dados,
        eremita_dados,
        escriba_dados,
        guarda_dados,
        mercador_dados,
        guia_dados,
        nobre_dados,
    ]

class Jogador():
    def __init__(self, nome, especie, classe, antecedente, atributo=True):
    #-----------------| EXIBIÇÃO |--------------------#      
        self.nome = nome # NOME JOGADOR
        self.especie = especie.get("nome") # NOME ESPECIE
        self.classe = classe.get("nome") # NOME CLASSE
        self.antecedente = antecedente.get("nome") # NOME ANTECEDENTE
        
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
        self.hp_max = classe.get("dado_de_vida") #-------| HP INICIAL MAX
        self.hp_atual = self.hp_max #-------| HP INICIAL ATUAL
        
        self.nivel = 1 #-------| NIVEL 
        self.xp = 0 #-------| XP
    #--------------------------------------------------#
    #------------------| VIDA E XP |-------------------#      
        modificador_destreza = round((self.atributos.get("destreza") - 10 ) // 2)
        self.classe_armadura = 10 + modificador_destreza #-------| CLASSE DE ARMADURA
    #---------------------------------------------------#
    #-------| PROEFICIENCIA E PERCEPÇÃO PASSIVA |-------#            
        self.bonus_proeficiencia = 2
        modificador_sabedoria = round((self.atributos.get("destreza") - 10 ) // 2)
        self.percepcao_passiva = 10 + modificador_sabedoria
    #---------------------------------------------------#
    #------------------| PERICIAS |---------------------# 
        self.proeficiencia_pericias = {
            "Atletismo": False,
            "Acrobacia": False,
            "Furtividade": False,
            "Prestigitacao": False,
            "Arcanismo": False,
            "Historia": False,
            "Investigacao": False,
            "Natureza": False,
            "Religiao": False,
            "Lidar com Animais": False,
            "Intuicao": False,
            "Medicina": False,
            "Percepcao": False,
            "Sobrevivencia": False,
            "Atuacao": False,
            "Enganacao": False,
            "Intimidacao": False,
            "Persuasao": False,
        }
                #-| ARMADURAS |-#
        self.proeficiencia_armadura = {
            "Leve": False,
            "Media": False,
            "Pesada": False,
        }
                #-| ESCUDO |-#    
        self.proeficiencia_escudo = {
            "Escudo": False,
        }
                #-| FERRAMENTAS |-#    
        self.proeficiencia_ferramentas = []
    #---------------------------------------------------#
    #------------------| SALVAGUARDAS |------------------#  
        self.salvaguarda_contra_morte = {
            "Sucesso": 0,
            "Falha": 0
        }
        
        self.salvaguarda_atributo = {
            "forca": False,
            "constituicao": False,
            "destreza": False,
            "inteligencia": False,
            "sabedoria": False,
            "carisma": False
        }
    
    #---------------------------------------------------#
    #------------------| INVENTARIO |--------------------# 
        self.inventario = {
        #   MOEDAS   #
            "PP": 0,
            "PO": 0,
            "PL": 0,
            
        #   ITENS ESPECIAIS  #
            "Itens Especiais": {
            
            },
            "Itens Consumiveis": {
                
            },
            "Comida": {
                
            }
        }
    
    
    #------------------| SUBCLASSE |--------------------#            
        self.subclasse = "Nenhum" #-------| DESENVOLVIMENTO FUTURO
    #---------------------------------------------------#
    
    
        
    def exibir_ficha(self):
        nome_classe = self.classe
        nome_especie = self.especie
        nome_antecedente = self.antecedente
     
        print(f"{"x".ljust(25, '-')}| FICHA DO PERSONAGEM |{"x".rjust(25, '-')}")
        print(f" {"|".ljust(35,' ')} {"|".rjust(35,' ')}")
        print(f" | Nome: {self.nome.ljust((23), ' ')} | Vida: {self.hp_atual}/{str(self.hp_max).ljust(14, ' ')} |  CA: {str(self.classe_armadura).ljust(4)} |")
        print(f" | Antecedente: {nome_antecedente.ljust(16, ' ')} | Classe: {nome_classe.ljust(15, ' ')} |  Nível: {str(self.nivel).ljust(1, ' ')} |")
        print(f" | Espécie: {nome_especie.ljust(20, ' ')} | Subclasse: {self.subclasse.ljust(12)} |  XP:{str(self.xp).ljust(6, ' ')}|")
        print(f" {"|".ljust(35,' ')} {"|".rjust(35,' ')}")
        print(f"{"x".ljust(29, '-')}| ATRIBUTOS |{"x".rjust(31, '-')}")
        for atributo, valor in self.atributos.items():
            print(f"   {atributo.ljust(12).upper()} :{str(valor).rjust((valor), '.')}")
        print(f"{"x".ljust(36,'-')}{"x".rjust(36,'-')}")
        espera_jogador()

def criar_ficha_jogador ():
    ## ESCOLHA DO JOGADOR ##
    print(f"{"="*50}")
    print("Olá Jogador!".center(50))
    print(f"{"="*50}")
    print()
    nome_jogador = str(input("Como posso te chamar?  ").title())
    time.sleep(0.1)
    limpar_tela()
    
    # ## ESCOLHA DA ESPECIE ##
    exibir_menu_especies(lista_especies, nome_jogador="Desconhecido")
    especie_jogador = escolher_especies(lista_especies)

    print()
    time.sleep(0.3)
    limpar_tela()
    
    # ## ESCOLHA DA CLASSE ##
    exibir_menu_classes(lista_classes, nome_jogador="Desconhecido")
    classe_jogador = escolher_classe(lista_classes)
    
    print()
    time.sleep(0.3)
    limpar_tela()
    
    ## ESCOLHA DO ANTECEDENTE ##            
    exibir_menu_antecedentes(lista_antecedentes, nome_jogador="Desconhecido")
    antecedente_jogador = escolher_antecedente(lista_antecedentes)
    atributo = sortear_atributos()
    
    print(f" Perfeito, {nome_jogador}! Essa é sua ficha no até o momento:")
    print()
    jogador1 = Jogador(nome_jogador, especie_jogador, classe_jogador, antecedente_jogador, atributo)
    jogador1.exibir_ficha() #PAUSA ATÉ O JOGADOR DAR ENTER
    
    ## DESEJA JOGAR ##
    escolha = menu_pronto_jogar(nome_jogador)
    if escolha == True:
        print("Começa o Jogo")
    else: 
        print("Salva a Ficha criada mas não inicia")
            
    time.sleep(2)    
    limpar_tela()