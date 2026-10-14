import json
from utilitario import digitar, carregar_dados_json, limpar_tela
import time
import dados
from antecedentes.antecedentes import exibir_menu_antecedentes, escolher_antecedente


# ESPECIES #
humano_dados = carregar_dados_json("especies/humano.json")
anao_dados = carregar_dados_json("especies/anao.json")
elfo_dados = carregar_dados_json("especies/elfo.json")

# CLASSE #
barbaro_dados = carregar_dados_json("classes/barbaro.json")
clerigo_dados = carregar_dados_json("classes/clerigo.json")
mago_dados = carregar_dados_json("classes/mago.json")

# ANTECEDENTE #

nobre_dados = carregar_dados_json("antecedentes/nobre.json")
acolito_dados = carregar_dados_json("antecedentes/acolito.json")
andarilho_dados = carregar_dados_json("antecedentes/andarilho.json")
eremita_dados = carregar_dados_json("antecedentes/eremita.json")
escriba_dados = carregar_dados_json("antecedentes/escriba.json")
guarda_dados = carregar_dados_json("antecedentes/guarda.json")
guia_dados = carregar_dados_json("antecedentes/guia.json")
mercador_dados = carregar_dados_json("antecedentes/mercador.json")

antecedentes = [
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
        
        self.nome = nome # NOME JOGADOR
        self.especie = especie.get("nome") # NOME ESPECIE
        self.classe = classe.get("nome") # NOME CLASSE

        if self.atributo == True:
            self.atributos = classe.get("atributos_padrao", {}).copy() #-------| ATRIBUTOS PADRÃO
        else: 
            self.atributos = dados.rolar_dados_atributos()
            
        self.antecedente = antecedente.get("nome") # NOME ANTECEDENTE
        self.bonus_atributos_antecedente = antecedente.get("bonus_atributos", {}) #-------| ANTECEDENTE 
        
        for atributo, valor in self.bonus_atributos_antecedente.items():
            if atributo in self.atributos:
                self.atributos[atributo] += valor
         
        self.hp_max = classe.get("dado_de_vida") #-------| HP
        self.hp_atual = self.hp_max #-------| HP ATUAL
        
        self.nivel = 1 #-------| NIVEL 
        self.xp = 0 #-------| XP
        
        modificador_destreza = round((self.atributos.get("destreza") - 10 ) // 2)
        self.classe_armadura = 10 + modificador_destreza #-------| CLASSE DE ARMADURA
               
        self.subclasse = "Nenhum" #-------| SUBCLASSE
        
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

def criar_ficha_jogador ():
    
    ## ESCOLHA DO JOGADOR ##
    
    # print(f"{"="*50}")
    # print("Olá Jogador!".center(50))
    # print(f"{"="*50}")
    # print()
    # nome_personagem = str(input("Como posso te chamar?  ").title())
    # time.sleep(0.1)
    # limpar_tela()
    
    # ## ESCOLHA DA ESPECIE ##

    # print(f"{"="*60}")
    # print(f"Muito bem, {"teste"}!".center(60))
    # print(f"Por favor, escolha a 'ESPÉCIE' com a qual quer jogar!".center(60))
    # print(f"{"="*60}")
    # print()
    # print(f"{"|".rjust(20, '-')} ESPÉCIES USÁVEIS {"|".ljust(21, '-')}")
    # print()
    # print(f"  1. {humano_dados["nome"]} - {humano_dados["descricao"]}")
    # print(f"  2. {elfo_dados["nome"]} - {elfo_dados["descricao"]}")
    # print(f"  3. {anao_dados["nome"]} - {anao_dados["descricao"]}")
    # print()
    # print(f"{"|".ljust(30, '-')}{"|".rjust(30, '-')}")
    # print()
    # while True:
    #     especie_jogador = int(input(" Digite o número que representa sua escolha (Ex: 1,2,3): "))
        
    #     match especie_jogador:
    #         case 1:
    #             especie_jogador = humano_dados
    #             break
    #         case 2:
    #             especie_jogador = elfo_dados
    #             break
    #         case 3:
    #             especie_jogador = anao_dados
    #             break
    #         case _:
    #             print("\n Escolha uma opção válido!\n".center(60))
    # print("Muito bom!")
    # time.sleep(0.2)    
    # limpar_tela()

    # ## ESCOLHA DA CLASSE ##
    
    # print(f"{"="*60}")
    # print(f"Você está indo bem {"teste"}!".center(60))
    # print(f"Agora, escolha a 'CLASSE' com a qual quer jogar!".center(60))
    # print(f"{"="*60}")
    # print()
    # print(f"{"|".rjust(20, '-')} CLASSES USÁVEIS {"|".ljust(21, '-')}")
    # print()
    # print(f"  1. {barbaro_dados["nome"]} - {barbaro_dados["descricao"]}")
    # print(f"  2. {clerigo_dados["nome"]} - {clerigo_dados["descricao"]}")
    # print(f"  3. {mago_dados["nome"]} - {mago_dados["descricao"]}")
    # print()
    # print(f"{"|".ljust(30, '-')}{"|".rjust(30, '-')}")
    # print()
    # while True:
    #     classe_jogador = int(input(" Digite o número que representa sua escolha (Ex: 1,2,3): "))
        
    #     match classe_jogador:
    #         case 1:
    #             classe_jogador = barbaro_dados
    #             break
    #         case 2:
    #             classe_jogador = clerigo_dados
    #             break
    #         case 3:
    #             classe_jogador = mago_dados
    #             break
    #         case _:
    #             print("\n Escolha uma opção válido!\n".center(60))
    # print("Muito bom!\n")
    
    # print("Você deseja usar os atributos padrão da classe?")

    # while True:
    #     atributos_aleatorios = str(input("Digite 'S' para usar o padrão ou 'N' para jogar os dados:  ").upper())
        
    #     match atributos_aleatorios:
    #         case "S":
    #             atributo = True
    #             break
    #         case "N":
    #             atributo = False
    #             break
    #         case _:
    #             print("Digite uma opção válida! 'S' ou 'N' ");
                
    
    exibir_menu_antecedentes(antecedentes, nome_jogador="teste")
    antecedente = escolher_antecedente(antecedentes)
    print(antecedente)
    time.sleep(2)    
    limpar_tela()    
    
    
    
#    print(
#    '''
        
# ████─████─████────████──████─███────████──█─█─███────█───█─████─████─████─███─█───█────████─████─████─████────████─████─████──█───███─█──█─███
# █──█─█──█─█───────█──██─█──█─█──────█──█──█─█─█──────██─██─█──█─█──█─█──█─█───██─██────█──█─█──█─█──█─█──█────█────█──█─█──██─█────█──██─█─█──
# ████─████─█─██────█──██─█──█─███────█─██──█─█─███────█─█─█─█──█─████─████─███─█─█─█────████─████─████─████────█─██─█──█─████──█────█──█─██─███
# █─█──█────█──█────█──██─█──█───█────█──█──█─█─█──────█───█─█──█─█─█──█─█──█───█───█────█────█──█─█─█──█──█────█──█─█──█─█──██─█────█──█──█───█
# █─█──█────████────████──████─███────█████─███─███────█───█─████─█─█──█─█──███─█───█────█────█──█─█─█──█──█────████─████─████──███─███─█──█─███
       
#    '''
#   )
# jogador_save1 = Jogador("John", humano_dados, barbaro_dados, nobre_dados)
# jogador_save1.exibir_ficha()

criar_ficha_jogador()