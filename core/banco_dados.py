import copy
from core.carregador_dados import carregar_arquivos_json_da_pasta
from models.habilidades import Habilidade, Magia
from models.itens import Arma, Armadura, Escudo, Item

class BancoDeDados:
    _especies = {}
    _classes = {}
    _antecedentes = {}
    
    _habilidades = {}
    _magias = {}
    
    _itens = {}
    _tabelas_loot = {}
    _eventos_globais = {}
    
    @classmethod
    def inicializar(cls):
        """Carrega todos os JSONs para a memória do jogo na inicialização."""
        # print("[SISTEMA] Inicializando Banco de Dados...")
        
        # 1. Carregar Dados de Criação
        for dados in carregar_arquivos_json_da_pasta("especies"):
            cls._especies[dados["id"]] = dados
        for dados in carregar_arquivos_json_da_pasta("classes"):
            cls._classes[dados["id"]] = dados
        for dados in carregar_arquivos_json_da_pasta("antecedentes"):
            cls._antecedentes[dados["id"]] = dados

        # 2. Carregar Habilidades e Magias
        for dados in carregar_arquivos_json_da_pasta("habilidades"):
            hab = Habilidade.do_dict(dados)
            cls._habilidades[hab.id] = hab
        for dados in carregar_arquivos_json_da_pasta("magias"):
            mag = Magia.do_dict(dados)
            cls._magias[mag.id] = mag

        # 3. Carregar Itens (Polimorfismo baseado no tipo)
        for dados in carregar_arquivos_json_da_pasta("itens"):
            tipo = dados.get("tipo_geral", "item")
            if tipo == "arma" or "dados_de_dano" in dados:
                obj = Arma.do_dict(dados)
            elif tipo == "armadura" or "ca_base" in dados:
                obj = Armadura.do_dict(dados)
            elif tipo == "escudo" or "bonus_ca" in dados:
                obj = Escudo.do_dict(dados)
            else:
                obj = Item(dados["id"], dados["nome"], dados["descricao"], dados.get("peso", 0), dados.get("preco", 0))
            cls._itens[obj.id] = obj

        # 4. Carregar Tabelas de Loot e Eventos
        # (Supondo que você crie esses arquivos na raiz da pasta dados)
        # cls._tabelas_loot = carregar_arquivo_unico("tabelas_loot.json")
        # cls._eventos_globais = carregar_arquivo_unico("eventos_globais.json")

    # --- MÉTODOS DE BUSCA E CLONAGEM ---
    @classmethod
    def obter_classe(cls, id_classe: str) -> dict:
        return copy.deepcopy(cls._classes.get(id_classe, {}))

    @classmethod
    def obter_habilidade(cls, id_habilidade: str):
        hab = cls._habilidades.get(id_habilidade)
        return copy.deepcopy(hab) if hab else None

    @classmethod
    def obter_item(cls, id_item: str):
        """Garante que se 2 goblins droparem uma Adaga, são objetos de memória diferentes"""
        item = cls._itens.get(id_item)
        return copy.deepcopy(item) if item else None
    
    @classmethod
    def obter_magia(cls, id_magia: str):
        mag = cls._magias.get(id_magia)
        return copy.deepcopy(mag) if mag else None
    
    @classmethod
    def obter_especie(cls, id_especies: str):
        especie = cls._especies.get(id_especies)
        return copy.deepcopy(especie) if especie else None

    @classmethod
    def obter_antecedente(cls, id_antecedente: str):
        antecedente = cls._antecedentes.get(id_antecedente)
        return copy.deepcopy(antecedente) if antecedente else None   