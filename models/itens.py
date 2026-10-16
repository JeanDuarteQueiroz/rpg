## ARMAS, ARMADURAS E ITENS CONSUMIVEIS ##
from jogador import Jogador

class Item():
    def __init__(self, id_item, nome, descricao, peso, preco):
        
        self.id = id
        self.nome = nome
        self.descricao = descricao
        self. peso = peso
        self.preco = preco
    
    
class Arma(Item):
    
    def __init__(
        self,
        id_item: str,
        nome: str,
        descricao: str,
        peso: float,
        preco: float,

        tipo: str,
        dados_de_dano: str,# 1d6, 2d4, etc
        tipo_do_dano: str, # Cortante, Concussão, Perfurante, etc
        propriedades: list = None,
    ):
        
        super().__init__(id_item, nome, descricao, peso, preco)
        self.tipo = tipo
        self.dados_de_dano = dados_de_dano
        self.tipo_dano = tipo_do_dano
        self.propriedades = set(propriedades or [])
    
    def calcular_modificador_atributo(self, portador) -> int:
        if "acuidade" in self.propriedades:
            bonus = max(portador.modificador("destreza"), portador.modificador("forca"))
        else:
            bonus = portador.modificador("forca")
        return bonus
    
    def calcular_modificador_acerto(self, portador) -> int:
        bonus = self.calcular_modificador_atributo(portador)
        if self.tipo in portador.proeficiencia_armas or self.nome in portador.proeficiencia_armas:
            bonus += portador.bonus_proeficiencia
        return bonus

    def calcular_modificador_dano(self, portador) -> int:
        # No D&D, o dano soma apenas o modificador do atributo (sem proficiência)
        return self.calcular_modificador_atributo(portador)
    
    @classmethod
    def do_dict(cls, dados:dict):
        return cls(
            id_item = dados.get("id_item", "Desconhecido"),
            nome = dados.get("nome", "Arma Sem Nome"),
            descricao = dados.get("descricao", "Uma arma..."),
            peso = dados.get("peso", 0.0),
            preco = dados.get("preco", 0.0),
            
            tipo = dados.get("tipo", "simples"),
            dados_de_dano = dados.get("dados_de_dano", "1d4"),
            tipo_de_dano = dados.get("tipo_de_dano", ""),
            propriedades = dados.get("propriedades", [])
        )
    
class Armadura(Item):
    def __init__(
        self, 
        id_item: str, 
        nome: str,
        descricao: str, 
        peso: float,
        preco: float,
        
        tipo_armadura: str,         
        ca_base: int,
        permite_destreza: bool
    ):
        super().__init__(id_item, nome, descricao, peso, preco)
        
        self.tipo_armadura = tipo_armadura
        self.ca_base = ca_base
        self.permite_destreza = permite_destreza
        
    @classmethod
    def do_dict(cls, dados: dict):
        return cls(
            id_item=dados.get("id"),
            nome=dados.get("nome"),
            descricao=dados.get("descricao", ""),
            peso=float(dados.get("peso", 2.0)),
            preco=float(dados.get("preco", 10.0)),
            bonus_ca=int(dados.get("bonus_ca", 2)),
            
            tipo_armadura = dados.get("tipo_armadura", ""),
            ca_base = int(dados.get("ca_base", 10)),
            permite_destreza = dados.get("permite_destreza", True)
        )

class Escudo(Item):

    def __init__(
        self,
        id_item: str,
        nome: str,
        descricao: str,
        peso: float,
        preco: float,
        bonus_ca: int = 2,
    ):
        super().__init__(id_item, nome, descricao, peso, preco)
        self.bonus_ca = bonus_ca

    @classmethod
    def do_dict(cls, dados: dict):
        return cls(
            id_item=dados.get("id"),
            nome=dados.get("nome"),
            descricao=dados.get("descricao", ""),
            peso=float(dados.get("peso", 2.0)),
            preco=float(dados.get("preco", 10.0)),
            bonus_ca=int(dados.get("bonus_ca", 2)),
        )