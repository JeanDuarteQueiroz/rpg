## ARMAS, ARMADURAS, ESCUDOS E ITENS CONSUMIVEIS ##

class Item():
    def __init__(self, id_item, nome, descricao, peso, preco):
        
        self.id = id_item
        self.nome = nome
        self.descricao = descricao
        self.peso = peso
        self.preco = preco
    
    def usar(self, *args):
        print(f"O item '{self.nome}' não pode ser consumido diretamente. Tenta usá-lo através das opções do ambiente!")
        return False
    
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
  
class Inventario():
    def __init__(self, capacidade_peso: float = 150.0, moedas: int = 0):
        self.moedas = moedas
        self.capacidade_peso = capacidade_peso
        self.peso_atual = 0.0
        self.itens = {}

    def adicionar_item(self, item, quantidade: int = 1) -> bool:
        """Adiciona itens se houver capacidade de peso disponível."""
        if quantidade <= 0:
            return False
            
        peso_adicional = item.peso * quantidade
        
        # Opcional: Bloquear se exceder o peso (remover este IF se quiseres inventário infinito)
        if self.peso_atual + peso_adicional > self.capacidade_peso:
            print(f"Não há espaço suficiente! {quantidade}x {item.nome} é muito pesado.")
            return False

        if item.id in self.itens:
            self.itens[item.id]["quantidade"] += quantidade
        else:
            self.itens[item.id] = {"objeto": item, "quantidade": quantidade}

        self.peso_atual += peso_adicional
        return True
    
    def remover_item(self, id_item: str, quantidade: int = 1):
        """
        Remove o item e devolve a tupla (Instancia_do_Item, quantidade_removida).
        Isso é crucial para mecânicas de Vender, Deixar Cair ou Roubar.
        """
        if id_item not in self.itens or quantidade <= 0:
            return None, 0

        qtd_atual = self.itens[id_item]["quantidade"]
        qtd_remover = min(quantidade, qtd_atual) # Garante que não remove mais do que existe
        item_obj = self.itens[id_item]["objeto"]

        self.itens[id_item]["quantidade"] -= qtd_remover
        self.peso_atual -= (item_obj.peso * qtd_remover)

        # Se a quantidade chegar a zero, remove a "gaveta" do dicionário
        if self.itens[id_item]["quantidade"] <= 0:
            del self.itens[id_item]

        return item_obj, qtd_remover

    def transferir_item(self, id_item: str, quantidade: int, inventario_destino) -> bool:
        """
        A mecânica base para Roubo, Saque e Troca. 
        Tira deste inventário e tenta colocar no inventário destino.
        """
        item_obj, qtd_removida = self.remover_item(id_item, quantidade)
        
        if qtd_removida > 0:
            sucesso = inventario_destino.adicionar_item(item_obj, qtd_removida)
            if not sucesso:
                # Se o destino estiver cheio, devolve o item à origem
                self.adicionar_item(item_obj, qtd_removida)
                return False
            return True
        return False
    
    def adicionar_moedas(self, valor: int):
        if valor > 0:
            self.moedas += valor
            
    def remover_moedas(self, valor: int) -> int:
        """Remove moedas e devolve o quanto conseguiu remover (útil para roubos)."""
        if valor <= 0:
            return 0
        qtd_remover = min(valor, self.moedas)
        self.moedas -= qtd_remover
        return qtd_remover
    
    def exibir(self):
        print(f"\n--- INVENTÁRIO ---")
        print(f"Moedas de Ouro: {self.moedas}")
        print(f"Peso: {self.peso_atual:.1f} / {self.capacidade_peso:.1f} kg")
        print("-" * 18)
        
        if not self.itens:
            print("  (Vazio)")
        else:
            for id_item, dados in self.itens.items():
                obj = dados["objeto"]
                qtd = dados["quantidade"]
                peso_total_item = obj.peso * qtd
                print(f"[{qtd}x] {obj.nome.ljust(20)} | Peso: {peso_total_item:.1f} kg")
        print("-" * 18)
        
class Consumivel(Item):
    def __init__(
        self, id_item, nome, descricao, peso, preco,
        tipo_efeito: str, dados_efeito: str, bonus_fixo: int = 0, propriedades: list = None
    ):
        super().__init__(id_item, nome, descricao, peso, preco)
        self.tipo_efeito = tipo_efeito
        self.dados_efeito = dados_efeito
        self.bonus_fixo = bonus_fixo
        self.propriedades = set(propriedades or [])

    @classmethod
    def do_dict(cls, dados: dict):
        return cls(
            id_item=dados.get("id", "Desconhecido"),
            nome=dados.get("nome", "Consumível Sem Nome"),
            descricao=dados.get("descricao", ""),
            peso=dados.get("peso", 0.0),
            preco=dados.get("preco", 0.0),
            tipo_efeito=dados.get("tipo_efeito", ""),
            dados_efeito=dados.get("dados_efeito", "0"),
            bonus_fixo=dados.get("bonus_fixo", 0),
            propriedades=dados.get("propriedades", [])
        )

    def usar(self, usuario, alvo, expressao_rolagem_func):
        print(f"\n{usuario.nome} utiliza {self.nome} em {alvo.nome}!")
        
        # 1. Aplica o efeito (Cura ou Dano)
        if self.tipo_efeito == "cura":
            valor_dado = expressao_rolagem_func(self.dados_efeito, "total") if self.dados_efeito != "0" else 0
            cura_total = valor_dado + self.bonus_fixo
            alvo.curar(cura_total)
            
        elif self.tipo_efeito == "dano":
            # Ex: Um frasco de ácido
            dano_total = expressao_rolagem_func(self.dados_efeito, "total") + self.bonus_fixo
            # Assumimos dano "acido" ou "fogo" lendo do JSON no futuro
            alvo.receber_dano(dano_total, "acido") 

        # 2. Retorna True para avisar ao jogo que a ação foi concluída com sucesso
        # (Para o jogo saber que deve remover o item do inventário do usuário)
        return True