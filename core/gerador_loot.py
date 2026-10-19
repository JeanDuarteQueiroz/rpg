import random
from core.banco_dados import BancoDeDados

def popular_inventario_com_loot(entidade_morta):
    """Lê a tabela de loot do NPC/Baú e gera os itens no inventário dele de forma procedural."""
    
    # Se já tem moedas ou itens, significa que já gerámos o loot para este corpo antes!
    if entidade_morta.inventario.moedas > 0 or entidade_morta.inventario.itens:
        return 
        
    tabela_id = getattr(entidade_morta, "tabela_loot", "loot_vazio")
    if tabela_id == "loot_vazio":
        return
        
    # ATENÇÃO: Assegura-te que o BancoDeDados carregou as tabelas_loot.json na inicialização
    tabelas = BancoDeDados._tabelas_loot 
    if tabela_id not in tabelas:
        return
        
    dados_loot = tabelas[tabela_id]
    
    # 1. Geração de Moedas
    min_m = dados_loot.get("moedas_min", 0)
    max_m = dados_loot.get("moedas_max", 0)
    if max_m > 0:
        entidade_morta.inventario.adicionar_moedas(random.randint(min_m, max_m))
    
    # 2. Itens Garantidos (Ex: Baú do tutorial que tem SEMPRE 1 pé de cabra)
    for item_g in dados_loot.get("itens_garantidos", []):
        qtd = random.randint(item_g.get("qtd_min", 1), item_g.get("qtd_max", 1))
        obj_item = BancoDeDados.obter_item(item_g["id_item"]) # Clona o item do banco!
        if obj_item and qtd > 0:
            entidade_morta.inventario.adicionar_item(obj_item, qtd)
            
    # 3. Itens Sorteados / Aleatórios (Ex: Bandidos que podem ter maçãs ou dentes de ouro)
    sorteios = dados_loot.get("itens_sorteados", {})
    for categoria, regras in sorteios.items():
        chance = regras.get("chance_categoria", 100)
        
        # Rola para ver se esta categoria dropa algo (ex: 50% de chance de ter consumíveis)
        if random.randint(1, 100) <= chance:
            opcoes = regras.get("opcoes", [])
            if not opcoes: continue
            
            # Sorteio com pesos (weight)
            pesos = [op.get("peso_base", 10) for op in opcoes]
            
            for _ in range(regras.get("rolagens_de_saque", 1)):
                escolha = random.choices(opcoes, weights=pesos, k=1)[0]
                
                if escolha["id_item"] != "nada":
                    qtd = random.randint(escolha.get("qtd_min", 1), escolha.get("qtd_max", 1))
                    obj_item = BancoDeDados.obter_item(escolha["id_item"])
                    if obj_item and qtd > 0:
                        entidade_morta.inventario.adicionar_item(obj_item, qtd)