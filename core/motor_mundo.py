import uuid
import copy
import random
from models.entidade import Npc

def gerir_economia_e_populacao(cidade_json: dict, npcs_ativos: list, templates_disponiveis: dict) -> list:
    """
    Avalia se a cidade tem os profissionais necessários.
    Se faltarem e houver impostos, cria novos NPCs a partir de templates.
    Retorna uma lista dos novos NPCs gerados.
    """
    cidade_id = cidade_json["id"]
    economia = cidade_json.get("economia", {})
    cotas = economia.get("cotas_populacao", {})
    impostos = economia.get("impostos_arrecadados", 0)
    custo_reposicao = economia.get("custo_reposicao", 50)
    
    # 1. Conta quantos profissionais VIVOS a cidade tem atualmente
    contagem_atual = {profissao: 0 for profissao in cotas.keys()}
    
    for npc in npcs_ativos:
        if npc.morte:
            continue
        # Verifica se o NPC pertence a esta cidade
        if npc.social.get("geografia", {}).get("nome_localidade") == cidade_id:
            prof = npc.social.get("profissao")
            if prof in contagem_atual:
                contagem_atual[prof] += 1

    novos_habitantes = []
    nomes_aleatorios = ["Fael", "Bram", "Tess", "Kael", "Lyra", "Gorin", "Mina"]

    # 2. Compara a população com as cotas e repõe se houver dinheiro
    for profissao, quantidade_necessaria in cotas.items():
        while contagem_atual[profissao] < quantidade_necessaria:
            
            if impostos < custo_reposicao:
                print(f"⚠️ [{cidade_json['nome']}] Crise! Falta {profissao}, mas a vila está sem fundos para repor!")
                break # Para de tentar repor esta profissão por falta de dinheiro
                
            template = templates_disponiveis.get(f"template_{profissao}")
            if template:
                # Paga o custo da reposição
                impostos -= custo_reposicao
                contagem_atual[profissao] += 1
                
                # Clona o template e cria a identidade única
                dados_novo_npc = copy.deepcopy(template)
                novo_id = f"{profissao}_{uuid.uuid4().hex[:6]}"
                nome_sorteado = random.choice(nomes_aleatorios)
                
                dados_novo_npc["id"] = novo_id
                dados_novo_npc["nome"] = f"{nome_sorteado} (Novo {profissao.title()})"
                dados_novo_npc["social"]["geografia"]["nome_localidade"] = cidade_id
                
                # Instancia a nova classe Npc e adiciona à lista
                novo_npc_obj = Npc.do_dict(dados_novo_npc)
                novos_habitantes.append(novo_npc_obj)
                
                print(f"🌲 [ECONOMIA] Comerciantes e impostos agiram: {novo_npc_obj.nome} foi contratado/assentado em {cidade_json['nome']}!")
            else:
                break # Se não existir um template para a profissão, sai do loop
                
    # 3. Guarda o valor atualizado dos impostos no JSON
    cidade_json["economia"]["impostos_arrecadados"] = impostos
    
    return novos_habitantes

def processar_fofocas_da_fase(npcs_da_vila: list, fase_atual: str, estacao_atual: str = "Primavera"):
    locais = {}
    for npc in npcs_da_vila:
        if npc.morte or npc.agressivo:
            continue

        # Pega o ID real do local onde o NPC está (ex: "forja_vila", "casa_grom", "taverna_local")
        local_real = npc.obter_local_atual(fase_atual, estacao_atual)

        # Se ele estiver dormindo ou isolado na própria casa, pula
        if local_real.startswith("casa_"):
            continue

        if local_real not in locais:
            locais[local_real] = []
        locais[local_real].append(npc)

    # 2. Em cada local com 2+ pessoas, rola a fofoca!
    for local, npcs_presentes in locais.items():
        if len(npcs_presentes) < 2:
            continue
            
        # Embaralha para que as conversas sejam dinâmicas
        random.shuffle(npcs_presentes)
        
        for fofoqueiro in npcs_presentes:
            if not fofoqueiro.memoria:
                continue # Não tem nada para contar
                
            # Escolhe um ouvinte aleatório no mesmo local (que não seja ele mesmo)
            ouvinte = random.choice([n for n in npcs_presentes if n != fofoqueiro])
            
            # Escolhe uma memória aleatória que o fofoqueiro conhece
            evento_id = random.choice(list(fofoqueiro.memoria.keys()))
            
            # Tenta espalhar!
            fofoqueiro.espalhar_fofoca(ouvinte, evento_id)
            
def processar_viagens_e_contratos(npcs_do_mundo: list, dicionario_eventos_globais: dict):
    # 1. Filtra apenas os NPCs que são viajantes
    viajantes = [npc for npc in npcs_do_mundo if npc.social.get("tipo_rotina") == "transito" and not npc.morte]
    
    mercadores_precisando_ajuda = []
    mercenarios_livres = []

    for npc in viajantes:
        itinerario = npc.social.get("itinerario", [])
        indice_atual = npc.social.get("indice_itinerario_atual", 0)
        
        if not itinerario or indice_atual >= len(itinerario):
            continue # Sem rota definida
            
        proximo_destino = itinerario[indice_atual]
        
        # 2. AVALIAÇÃO DE MEDO (O NPC sabe de algum perigo na próxima rota?)
        caminho_bloqueado = False
        for id_memoria, dados_memoria in npc.memoria.items():
            # Consulta o dicionário global para saber onde este evento ocorreu
            info_evento = dicionario_eventos_globais.get(id_memoria)
            if info_evento and info_evento.get("local_afetado") == proximo_destino:
                # Se o NPC for cauteloso, ele recusa-se a ir!
                if "cauteloso" in npc.social.get("diretrizes_viagem", {}).get("comportamento", ""):
                    caminho_bloqueado = True
                    break

        # 3. MUDANÇA DE ESTADO
        if caminho_bloqueado and npc.social["profissao"] == "comerciante":
            npc.social["estado_dinamico"]["estado_ativo"] = "procurando_escolta"
            mercadores_precisando_ajuda.append(npc)
        elif npc.social["profissao"] == "mercenario" and npc.social.get("faccao_lealdade") == "nenhuma":
            mercenarios_livres.append(npc)
        else:
            # 4. AVANÇAR VIAGEM SE O CAMINHO ESTIVER LIVRE
            # (Aqui você faria a lógica de somar +1 ao dia_no_local_atual e avançar o índice se atingiu o limite)
            pass

    # 5. A BOLSA DE CONTRATOS (Matchmaking)
    for mercador in mercadores_precisando_ajuda:
        # Pega mercenários que estão na mesma cidade que o mercador
        cidade_mercador = mercador.social["geografia"]["nome_localidade"]
        mercenarios_na_cidade = [m for m in mercenarios_livres if m.social["geografia"]["nome_localidade"] == cidade_mercador]
        
        if mercenarios_na_cidade:
            contratado = mercenarios_na_cidade.pop(0)
            mercenarios_livres.remove(contratado) # Tira da lista geral
            
            # Executa o pagamento usando o seu Inventario!
            moedas_pagas = mercador.inventario.remover_moedas(50)
            contratado.inventario.adicionar_moedas(moedas_pagas)
            # Vincula os destinos e limpa o medo
            contratado.social["itinerario"] = mercador.social["itinerario"].copy()
            mercador.social["estado_dinamico"]["estado_ativo"] = "viajando_com_escolta"
            
            print(f"💰 [ECONOMIA GLOBAL] {mercador.nome} contratou {contratado.nome} como escolta em {cidade_mercador}!")