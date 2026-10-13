from atributos import ATRIBUTOS_BARBARO_PADRAO, ATRIBUTOS_CLERIGO_PADRAO, ATRIBUTOS_MAGO_PADRAO

class Especie():
    def __init__(self, nome, descricao):
        self.nome = nome
        self.descricao = descricao
        
    def __str__(self):
            return self.nome
    
class Classe():
    def __init__(self, nome, dado_vida, atributos_base):
        self.nome = nome
        self.dado_vida = dado_vida
        self.atributos_base = atributos_base
        
    def __str__(self):
            return self.nome
        
class Jogador():
    def __init__(self, nome, especie, classe):
        self.nome = nome
        self.especie = especie
        self.classe = classe
        self.nivel = 1
        self.xp = 0
        self.atributos = self.classe.atributos_base.copy()
        self.hp_max = self.classe.dado_vida
        self.hp_atual = self.hp_max
        self.antecedente = "-" 
        self.subclasse = "-"

    def exibir_ficha(self):
        nome_classe = self.classe.nome if hasattr(self.classe, "nome") else "Desconhecida"
        nome_especie = self.especie.nome if hasattr(self.especie, "nome") else "Desconhecida"
        
        forca = self.atributos.get("FORÇA", "Indisponível")
        constituicao = self.atributos.get("CONSTITUIÇÃO", "Indisponível")
        destreza = self.atributos.get("DESTREZA", "Indisponível")
        inteligencia = self.atributos.get("INTELIGÊNCIA", "Indisponível")
        sabedoria = self.atributos.get("SABEDORIA", "Indisponível")
        
        print("----------------------| FICHA DO PERSONAGEM |----------------------")
        print(f" Nome: {self.nome:<17} | Vida: {self.hp_atual}/{self.hp_max:<17} | Nível: {self.nivel}")
        print(f" Antecedente: {self.antecedente:<10} | Classe: {nome_classe}")
        print(f" Espécie: {nome_especie:<14} | SUubclasse: {self.subclasse:<14} | Xp: {self.xp}")
        print("-" * 67)
        print(" ATRIBUTOS:")
        print(f" FORÇA: {forca}")
        print(f" CONSTITUIÇÃO: {constituicao}")
        print(f" DESTREZA: {destreza}")
        print(f" INTELIGÊNCIA: {inteligencia}")
        print(f" SABEDORIA: {sabedoria}")
        print("-" * 67)

# Instâncias das Espécies e Classes
humano = Especie("Humano", "Versáteis e adaptáveis a qualquer desafio.")
elfo = Especie("Elfo", "Ágeis, perceptivos e com afinidade mágica.")
anao = Especie("Anão", "Resilientes, robustos e tradicionais.")

barbaro = Classe("Bárbaro", 12, ATRIBUTOS_BARBARO_PADRAO)
clerigo = Classe("Clérigo", 8, ATRIBUTOS_CLERIGO_PADRAO)
mago = Classe("Mago", 6, ATRIBUTOS_MAGO_PADRAO)

jogador1 = Jogador("Jean", humano, barbaro)
jogador1.exibir_ficha()