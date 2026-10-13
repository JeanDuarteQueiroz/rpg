import json
import utilitario

# ESPECIES #
humano_dados = utilitario.carregar_dados_json("especies/humano.json")
anao_dados = utilitario.carregar_dados_json("especies/anao.json")
elfo_dados = utilitario.carregar_dados_json("especies/elfo.json")

# CLASSE #
barbaro_dados = utilitario.carregar_dados_json("classes/barbaro.json")

# ANTECEDENTE #
nobre_dados = utilitario.carregar_dados_json("antecedentes/nobre.json")


class Jogador():
    def __init__(self, nome, especie, classe, antecedente):
        
        self.nome = nome # NOME JOGADOR
        self.especie = especie.get("nome") # NOME ESPECIE
        self.classe = classe.get("nome") # NOME CLASSE
    
        self.atributos = classe.get("atributos_padrao", {}).copy() #-------| ATRIBUTOS PADRÃO
        
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
        
        
jogador_save1 = Jogador("John", humano_dados, barbaro_dados, nobre_dados)
jogador_save1.exibir_ficha()