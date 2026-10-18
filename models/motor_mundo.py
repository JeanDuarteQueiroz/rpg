import random

def processar_fofocas_da_fase(npcs_da_vila: list, fase_atual: str):
    # 1. Agrupa os NPCs pelo local onde estão agora segundo a rotina
    locais = {}
    for npc in npcs_da_vila:
        if npc.morte or npc.agressivo:
            continue
            
        atividade = npc.rotina.get(fase_atual, "dormir")
        if atividade in ("dormir", "casa"):
            continue # Ninguém fofoca com estranhos dormindo em casa
            
        if atividade not in locais:
            locais[atividade] = []
        locais[atividade].append(npc)

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