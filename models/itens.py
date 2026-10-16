## ARMAS, ARMADURAS, ESCUDOS E ITENS CONSUMIVEIS ##

class Item():
    def __init__(self, id_item, nome, descricao, peso, preco):
        
        self.id = id_item
        self.nome = nome
        self.descricao = descricao
        self.peso = peso
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
        dado_dano_duas_maos: str = None
    ):
        
        super().__init__(id_item, nome, descricao, peso, preco)
        self.tipo = tipo
        self.dados_de_dano = dados_de_dano
        self.tipo_dano = tipo_do_dano
        self.propriedades = set(propriedades or [])
        self.dado_dano_duas_maos = dado_dano_duas_maos
        

    def obter_dado_dano(self, com_duas_maos: bool = False) -> str:
        """Devolve o dado de duas mãos caso a arma seja versátil e seja usada com as duas mãos; caso contrário, devolve o dado padrão."""
        if "versatil" in self.propriedades and com_duas_maos and self.dado_dano_duas_maos:
            return self.dado_dano_duas_maos
        return self.dados_de_dano

    def calcular_modificador_atributo(self, portador) -> int:        
        if "acuidade" in self.propriedades:
            bonus = max(portador.modificador("destreza"), portador.modificador("forca"))
        else:
            bonus = portador.modificador("forca")
        return bonus
    
    def calcular_modificador_acerto(self, portador) -> int:
        bonus = self.calcular_modificador_atributo(portador)
        if self.tipo in portador.proficiencia_armas or self.nome in portador.proficiencia_armas:
            bonus += portador.bonus_proficiencia
        return bonus

    def calcular_modificador_dano(self, portador) -> int:
        # No D&D, o dano soma apenas o modificador do atributo (sem proficiência)
        return self.calcular_modificador_atributo(portador)
    
    @classmethod
    def do_dict(cls, dados:dict):
        return cls(
            id_item = dados.get("id", "Desconhecido"),
            nome = dados.get("nome", "Arma Sem Nome"),
            descricao = dados.get("descricao", "Uma arma..."),
            peso = dados.get("peso", 0.0),
            preco = dados.get("preco", 0.0),
            
            tipo = dados.get("tipo", "simples"),
            dados_de_dano = dados.get("dados_de_dano", "1d4"),
            tipo_do_dano = dados.get("tipo_do_dano", ""),
            propriedades = dados.get("propriedades", []),
            dado_dano_duas_maos = dados.get("dado_dano_duas_maos", None)
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
        ca_base: int
    ):
        super().__init__(id_item, nome, descricao, peso, preco)
        
        self.tipo_armadura = tipo_armadura.title()
        self.ca_base = ca_base
        
    @classmethod
    def do_dict(cls, dados: dict):
        return cls(
            id_item=dados.get("id", "Desconhecida"),
            nome=dados.get("nome", "Armadura Sem Nome"),
            descricao=dados.get("descricao", ""),
            peso=float(dados.get("peso", 2.0)),
            preco=float(dados.get("preco", 10.0)),
            tipo_armadura=dados.get("tipo_armadura", "Leve"),
            ca_base=int(dados.get("ca_base", 10))
        )
        
    def calcula_ca(self, portador) -> int:
        tipo = self.tipo_armadura.strip().lower()

        if tipo == "leve":
            return self.ca_base + portador.modificador("destreza")
        elif tipo in ("media", "média"):
            return self.ca_base + min(2, portador.modificador("destreza"))
        elif tipo == "pesada":
            return self.ca_base
        else:
            # Caso haja algum erro no cadastro do JSON, assume ao menos a CA base
            return self.ca_base
    
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