import random
from time import sleep
from models.jogador import Jogador

def rolar_iniciativa(entidade, expressao_rolagem_func) -> int:
    """Rola 1d20 + Modificador de Destreza para definir a ordem de ação."""
    d20 = expressao_rolagem_func("1d20", "total")
    return d20 + entidade.modificador("destreza")

def iniciar_combate(jogador, inimigos_na_cena: list, expressao_rolagem_func):
    """O Maestro da Batalha. Controla a coreografia de turnos."""
    
    print("\n" + "="*60)
    print("⚔️  O CLIMA FICA TENSO. O COMBATE COMEÇOU! ⚔️".center(60))
    print("="*60)
    
    # 1. Filtra os hostis vivos
    hostis = [npc for npc in inimigos_na_cena if npc.agressivo and not npc.morte]
    
    if not hostis:
        print("Falso alarme. Ninguém quer lutar contigo agora.")
        return True

    # 2. Rola a Iniciativa
    fila_batalha = [{"entidade": jogador, "iniciativa": rolar_iniciativa(jogador, expressao_rolagem_func), "tipo": "jogador"}]
    for inimigo in hostis:
        fila_batalha.append({
            "entidade": inimigo, 
            "iniciativa": rolar_iniciativa(inimigo, expressao_rolagem_func), 
            "tipo": "npc"
        })
    
    fila_batalha.sort(key=lambda x: x["iniciativa"], reverse=True)
    
    print("\n[ Ordem de Iniciativa ]")
    for p in fila_batalha:
        print(f" 🗡️ {p['entidade'].nome} (Iniciativa: {p['iniciativa']})")
    sleep(1.5)

    # 3. O Loop Principal
    combate_ativo = True
    turno_numero = 1
    
    while combate_ativo:
        print(f"\n{'-'*25} TURNO {turno_numero} {'-'*25}")
        
        for p in fila_batalha:
            combatente = p["entidade"]
            
            if combatente.hp_atual <= 0:
                continue
                
            hostis_vivos = [i for i in hostis if i.hp_atual > 0 and i.agressivo]
            if jogador.hp_atual <= 0 or not hostis_vivos:
                combate_ativo = False
                break 
            
            # --- TURNO ---
            if p["tipo"] == "jogador":
                fugiu = turno_do_jogador(jogador, hostis_vivos, expressao_rolagem_func)
                if fugiu:
                    print("\n🏃 Viraste as costas e conseguiste escapar da carnificina!")
                    return True
            else:
                turno_do_npc(combatente, jogador, expressao_rolagem_func)
            
            combatente.processar_turnos_status()
            sleep(1)
                
        turno_numero += 1

    # 4. Resolução Dramática
    if jogador.hp_atual <= 0:
        print("\n☠️ A TUA VISÃO ESCURECE. FOSTE DERROTADO...")
        return False
    else:
        print("\n🏆 O SILÊNCIO VOLTA A REINAR. VITÓRIA!")
        
        # --- DISTRIBUIÇÃO DE XP ---
        xp_total = sum(npc.xp_recompensa for npc in hostis)
        jogador.ganhar_xp(xp_total)
        
        # --- GERAÇÃO DE LOOT (Futuro passo) ---
        print("\nOs corpos no chão aguardam para serem vasculhados...")
        
        return True


def turno_do_jogador(jogador, hostis_vivos, expressao_rolagem_func) -> bool:
    print(f"\nSua vez, {jogador.nome}! (HP: {jogador.hp_atual}/{jogador.hp_max})")
    
    while True:
        print("\n[1] 🗡️ Atacar")
        print("[2] ✨ Habilidade / Magia")
        print("[3] 🎒 Inventário (Consumíveis)")
        print("[4] 🏃 Tentar Fugir")
        
        escolha = input("Ação: ").strip()
        
        if escolha == "1":
            alvo = escolher_alvo(hostis_vivos)
            if alvo:
                realizar_ataque_fisico(jogador, alvo, expressao_rolagem_func, atacante_e_jogador=True)
                return False
        elif escolha == "2":
            if abrir_menu_habilidades(jogador, hostis_vivos, expressao_rolagem_func): return False
        elif escolha == "3":
            if abrir_menu_inventario_combate(jogador, hostis_vivos, expressao_rolagem_func): return False
        elif escolha == "4":
            print("\nProcuras desesperadamente uma brecha para correr...")
            sleep(1)
            return True
        else:
            print("Opção inválida.")

def turno_do_npc(npc, jogador, expressao_rolagem_func):
    print(f"\n> 👺 Turno de {npc.nome}...")
    sleep(1)

    mod_ataque = npc.modificador("forca")
    mod_dano = npc.modificador("forca") + npc.bonus_dano_temporario

    d20 = expressao_rolagem_func("1d20", "total")
    total_acerto = d20 + mod_ataque

    print(f"(Ataque: {d20} + {mod_ataque} = {total_acerto} vs CA {jogador.classe_armadura})")
    sleep(0.5)

    # Usa a mecânica cinematográfica
    narrar_ataque(npc, jogador, total_acerto, "Arma Grosseira", mod_dano, expressao_rolagem_func)

def realizar_ataque_fisico(atacante, alvo, expressao_rolagem_func, atacante_e_jogador=True):
    if atacante_e_jogador and atacante.arma_equipada:
        arma = atacante.arma_equipada
        nome_arma = arma.nome
        mod_acerto = arma.calcular_modificador_acerto(atacante)
        mod_dano = arma.calcular_modificador_dano(atacante) + atacante.bonus_dano_temporario
        dado_dano = arma.obter_dado_dano(com_duas_maos=not bool(atacante.escudo_equipado))
        tipo_dano = arma.tipo_dano
    else:
        nome_arma = "Punhos"
        mod_acerto = atacante.modificador("forca") + (atacante.bonus_proficiencia if atacante_e_jogador else 0)
        mod_dano = atacante.modificador("forca") + atacante.bonus_dano_temporario
        dado_dano = "1d4"
        tipo_dano = "concussao"

    print(f"\n⚔️ {atacante.nome} investe contra {alvo.nome} usando {nome_arma}!")
    sleep(0.5)

    d20 = expressao_rolagem_func("1d20", "total")
    total_acerto = d20 + mod_acerto

    print(f"(Ataque: {d20} + {mod_acerto} = {total_acerto} vs CA {alvo.classe_armadura})")
    sleep(0.5)

    narrar_ataque(atacante, alvo, total_acerto, nome_arma, mod_dano, expressao_rolagem_func, dado_dano, tipo_dano)

def narrar_ataque(atacante, defensor, total_acerto, nome_arma, mod_dano, rolagem_func, dado_dano="1d6", tipo_dano="concussao"):
    """O Mestre Narrador do Combate. Avalia por que o ataque falhou ou como acertou."""
    
    # Desmonta a CA do defensor
    esquiva_base = 10 + defensor.modificador("destreza")
    
    ca_sem_escudo = defensor.classe_armadura
    tem_escudo = False
    
    if hasattr(defensor, "escudo_equipado") and defensor.escudo_equipado:
        tem_escudo = True
        ca_sem_escudo -= defensor.escudo_equipado.bonus_ca

    # --- NARRATIVA DE FALHA ---
    if total_acerto < defensor.classe_armadura:
        if total_acerto < esquiva_base:
            # Falhou porque o alvo foi rápido
            frases = [
                f"💨 Com um movimento ágil, {defensor.nome} esquiva-se do golpe de {nome_arma}!",
                f"💨 {defensor.nome} baixa a cabeça no momento exato e o golpe passa a centímetros!",
                f"💨 A rapidez de {defensor.nome} fala mais alto. O ataque corta apenas o ar!"
            ]
            print(random.choice(frases))
            
        elif total_acerto < ca_sem_escudo:
            # Falhou porque bateu na armadura
            frases = [
                f"🛡️ O ataque resvala violentamente contra a armadura de {defensor.nome}, produzindo faíscas, mas não perfura!",
                f"🛡️ Um impacto pesado! Mas as proteções de {defensor.nome} absorvem o dano do ataque.",
                f"🛡️ A lâmina raspa na cota de malha de {defensor.nome} sem encontrar carne."
            ]
            print(random.choice(frases))
            
        elif tem_escudo:
            # Falhou porque o escudo bloqueou (Estava acima da armadura, mas abaixo da CA total com escudo)
            frases = [
                f"🪵 Um estrondo de madeira e ferro! {defensor.nome} ergue o escudo no último instante e bloqueia a morte!",
                f"🪵 {atacante.nome} ataca com fúria, mas o escudo de {defensor.nome} desvia o impacto para o chão."
            ]
            print(random.choice(frases))
        else:
            # Fallback
            print(f"🛡️ {defensor.nome} consegue repelir o ataque de raspão!")

    # --- NARRATIVA DE ACERTO ---
    else:
        dano_rolado = rolagem_func(dado_dano, "total")
        dano_final = max(1, dano_rolado + mod_dano)
        
        frases_acerto = [
            f"🩸 ACERTO! O golpe encontra uma brecha fatal e rasga a defesa de {defensor.nome}!",
            f"🩸 IMPACTO! A investida de {atacante.nome} é brutal e implacável!",
            f"🩸 O sangue espirra quando {nome_arma} atinge {defensor.nome} em cheio!"
        ]
        print(random.choice(frases_acerto))
        
        if atacante.id == "jogador":
            defensor.receber_dano(dano_final, tipo_dano, causador="jogador")
        else:
            defensor.receber_dano(dano_final, tipo_dano, causador=atacante.id)

def escolher_alvo(hostis_vivos):
    print("\nEscolha um alvo:")
    for i, inimigo in enumerate(hostis_vivos):
        print(f"[{i+1}] {inimigo.nome} (HP: {inimigo.hp_atual}/{inimigo.hp_max})")
    print("[0] Voltar")
    while True:
        try:
            op = int(input("Alvo: "))
            if op == 0: return None
            if 1 <= op <= len(hostis_vivos): return hostis_vivos[op-1]
        except ValueError: pass
        print("Opção inválida.")

def abrir_menu_habilidades(jogador, hostis_vivos, expressao_rolagem_func) -> bool:
    todas = jogador.habilidades + jogador.truques
    if not todas:
        print("\nNão tens habilidades de combate na memória.")
        return False
        
    print("\n--- HABILIDADES E MAGIAS ---")
    for i, hab in enumerate(todas):
        texto = f"[{i+1}] {hab.nome}"
        if hasattr(hab, "nivel") and hab.nivel > 0: texto += f" (Magia Nv {hab.nivel})"
        elif hab.usos_max > 0: texto += f" (Usos: {hab.usos_disponiveis}/{hab.usos_max})"
        print(texto)
    print("[0] Voltar")
    
    while True:
        try:
            op = int(input("Escolha: "))
            if op == 0: return False
            if 1 <= op <= len(todas):
                hab_escolhida = todas[op-1]
                alvo_hab = None
                if hab_escolhida.tipo_efeito in ["dano", "aplicar_status", "remover_status"]:
                    alvo_hab = escolher_alvo(hostis_vivos)
                    if not alvo_hab: return False 
                return hab_escolhida.executar(jogador, alvo_hab, expressao_rolagem_func)
        except ValueError: pass
        print("Opção inválida.")

def abrir_menu_inventario_combate(jogador, hostis_vivos, expressao_rolagem_func) -> bool:
    from models.itens import Consumivel
    consumiveis = [dados for id_item, dados in jogador.inventario.itens.items() if isinstance(dados["objeto"], Consumivel)]
    
    if not consumiveis:
        print("\nA tua bolsa não tem poções ou itens rápidos de combate.")
        return False
        
    print("\n--- MOCHILA DE COMBATE ---")
    for i, dados in enumerate(consumiveis):
        obj = dados["objeto"]
        print(f"[{i+1}] {obj.nome} (Qtd: {dados['quantidade']})")
    print("[0] Voltar")
    
    while True:
        try:
            op = int(input("Escolha um item: "))
            if op == 0: return False
            if 1 <= op <= len(consumiveis):
                item_obj = consumiveis[op-1]["objeto"]
                alvo_item = jogador
                if "arremesso" in item_obj.propriedades or item_obj.tipo_efeito == "dano":
                    alvo_item = escolher_alvo(hostis_vivos)
                    if not alvo_item: return False
                usou = item_obj.usar(jogador, alvo_item, expressao_rolagem_func)
                if usou:
                    jogador.inventario.remover_item(item_obj.id, 1)
                    return True
        except ValueError: pass
        print("Opção inválida.")
        
