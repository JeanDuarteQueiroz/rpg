import random
from time import sleep
from core.motor_combate import iniciar_combate

class GestorCena:
    def __init__(self, relogio, mundo_estado, mapa_global):
        self.relogio = relogio
        self.mundo_estado = mundo_estado  # Dicionário de eventos globais
        self.mapa_global = mapa_global    # O JSON lido com todos os locais
        self.estado_cenas = {}            # Segredos descobertos

    def validar_requisitos(self, requisitos: dict, jogador) -> tuple[bool, str]:
        if not requisitos:
            return True, ""

        if self.relogio.clima_atual in requisitos.get("clima_proibido", []):
            return False, requisitos.get("mensagem_bloqueio", "O ambiente está desfavorável devido ao clima atual.")

        item_necessario = requisitos.get("item_necessario")
        if item_necessario:
            tem_item = item_necessario in jogador.inventario.itens and jogador.inventario.itens[item_necessario]["quantidade"] > 0
            if not tem_item:
                return False, requisitos.get("mensagem_bloqueio", "Falta um item necessário para prosseguir.")

        evento_necessario = requisitos.get("evento_necessario")
        if evento_necessario and not self.mundo_estado.get(evento_necessario, False):
            return False, requisitos.get("mensagem_bloqueio", "Uma condição histórica não foi cumprida.")

        return True, ""

    def observar_arredores(self, jogador, id_local: str, dados_local: dict):
        print("\n🔍 Observando os arredores...")
        sleep(0.5)
        
        segredos = dados_local.get("elementos_escondidos", [])
        if not segredos:
            print("Examinas cada detalhe do ambiente, mas não encontras nada de incomum.")
            return

        if id_local not in self.estado_cenas:
            self.estado_cenas[id_local] = {}
            
        estado_local = self.estado_cenas[id_local]
        encontrou_algo = False

        for segredo in segredos:
            id_seg = segredo["id_segredo"]
            if estado_local.get(id_seg, False):
                continue 

            d20 = random.randint(1, 20)
            mod_sab = jogador.modificador("sabedoria")
            if "percepcao" in jogador.proficiencia_pericias:
                mod_sab += jogador.bonus_proficiencia
                
            total_percepcao = d20 + mod_sab
            cd_necessario = segredo.get("cd_percepcao", 10)
            
            sleep(0.4)
            if total_percepcao >= cd_necessario:
                estado_local[id_seg] = True 
                encontrou_algo = True
                print(f"\n✨ {segredo.get('mensagem_sucesso', 'Encontraste algo oculto!')}")
                
                liberado, msg_bloqueio = self.validar_requisitos(segredo.get("requisitos", {}), jogador)
                if not liberado:
                    print(f"   (No entanto) {msg_bloqueio}")
            else:
                print(f"\n{segredo.get('mensagem_falha', 'Procuras com atenção, mas nada te chama a atenção.')}")

        if not encontrou_algo and all(estado_local.get(s["id_segredo"], False) for s in segredos):
            print("Já vasculhaste este lugar por completo e conheces todos os seus segredos.")

    def processar_cena(self, jogador, id_local: str, dados_local: dict, npcs_na_cena: list, expressao_rolagem_func) -> dict:
        """
        O 'Mestre da Exploração'. Varre a ameaça antes de desenhar o mapa.
        É a ponte direta com o Motor de Combate.
        """
        # 1. VARREDURA DE AMEAÇA
        hostis = [npc for npc in npcs_na_cena if npc.agressivo and not npc.morte]
        
        if hostis:
            print(f"\n⚠️ Sentes uma intenção assassina no ar! Presença hostil em {dados_local.get('nome')}!")
            sleep(1)
            # Passa a bola para o Mestre da Ação
            sobreviveu = iniciar_combate(jogador, npcs_na_cena, expressao_rolagem_func)
            
            if not sobreviveu:
                return {"acao": "game_over"}
            else:
                print("\nO local parece seguro novamente. Podes voltar a respirar e explorar.")
                sleep(1)

        # 2. MODO EXPLORAÇÃO (Se não há ameaças, mostra o menu pacífico)
        return self.exibir_menu_dinamico(jogador, id_local, dados_local, npcs_na_cena)

    def exibir_menu_dinamico(self, jogador, id_local: str, dados_local: dict, npcs_na_cena: list) -> dict:
        opcoes = {}
        contador = 1
        
        opcoes["0"] = {"texto": "⛺ Acampamento / Menu do Sistema", "acao": "menu_sistema", "custo": 0}
        
        # --- AÇÕES LIVRES ---
        opcoes[str(contador)] = {"texto": "Observar / Analisar o ambiente", "acao": "observar", "custo": 1}
        contador += 1
        opcoes[str(contador)] = {"texto": "Abrir Ficha e Inventário", "acao": "inventario", "custo": 0}
        contador += 1
        
        # --- INTERAÇÕES SOCIAIS (Lista NPCs na sala) ---
        npcs_vivos = [n for n in npcs_na_cena if not n.morte]
        for npc in npcs_vivos:
            # Se ele estivesse agressivo, o código nem chegaria aqui, logo é pacífico!
            opcoes[str(contador)] = {
                "texto": f"🗣️ Falar com {npc.nome}",
                "acao": "falar_npc",
                "alvo_id": npc.id,
                "custo": 1
            }
            contador += 1
        
        # --- MOVIMENTAÇÃO (Lê as Conexões Normais) ---
        for dest_id, texto_botao in dados_local.get("conexoes", {}).items():
            opcoes[str(contador)] = {
                "texto": f"Mover: {texto_botao}",
                "acao": "mover",
                "destino": dest_id,
                "custo": 2
            }
            contador += 1
            
        # --- ROTAS E AÇÕES ESCONDIDAS ---
        segredos = dados_local.get("elementos_escondidos", [])
        estado_local = self.estado_cenas.get(id_local, {})
        
        for segredo in segredos:
            if estado_local.get(segredo["id_segredo"], False):
                liberado, msg_bloqueio = self.validar_requisitos(segredo.get("requisitos", {}), jogador)
                
                if liberado:
                    opcoes[str(contador)] = {
                        "texto": f"🗝️ [DESCOBERTA] {segredo.get('texto_botao', 'Avançar')}",
                        "acao": segredo.get("tipo", "nova_rota"),
                        "destino": segredo.get("destino"),
                        "custo": 2
                    }
                else:
                    opcoes[str(contador)] = {
                        "texto": f"🔒 [BLOQUEADO] {segredo.get('texto_botao', 'Avançar')}",
                        "acao": "bloqueado",
                        "msg_bloqueio": msg_bloqueio,
                        "custo": 0
                    }
                contador += 1
        
        

        # --- A INTERFACE VISUAL ---
        print(f"\n{'='*60}")
        print(f"📍 {dados_local.get('nome', 'Lugar Desconhecido').center(56)}")
        print(f"🕒 Hora: {self.relogio.obter_fase_atual()} | Clima: {self.relogio.clima_atual}")
        print(f"{'='*60}")
        print(f"{dados_local.get('descricao', '')}")
        
        # --- CORPOS NO CHÃO (SAQUE) ---
        mortos = [n for n in npcs_na_cena if n.morte]
        for morto in mortos:
            opcoes[str(contador)] = {
                "texto": f"🎒 Vasculhar o corpo de {morto.nome}",
                "acao": "saquear_corpo",
                "alvo": morto, # Guardamos a referência do NPC morto!
                "custo": 1
            }
            contador += 1
            
        print("-" * 60)
        
        print(" O QUE VOCÊ FAZ?")
        for k, v in opcoes.items():
            print(f" [{k}] {v['texto']}")
            
        while True:
            resp = input("\nSua escolha: ").strip()
            if resp in opcoes:
                return opcoes[resp]
            print("Opção inválida. Tente novamente.")
    
    def interface_de_saque(self, jogador, corpo):
        """Abre o inventário do corpo e permite transferir itens para o jogador."""
        from core.gerador_loot import popular_inventario_com_loot
        
        # Garante que o corpo tem o loot gerado (só gera na primeira vez)
        popular_inventario_com_loot(corpo)
        
        print(f"\nAjoelhas-te perto de {corpo.nome} e vasculhas os pertences...")
        sleep(1)
        
        while True:
            print(f"\n{'='*40}")
            print(f" ESPÓLIOS DE {corpo.nome.upper()} ".center(40, "-"))
            print(f" Moedas de Ouro: {corpo.inventario.moedas}")
            print(f"{'='*40}")
            
            itens_lista = list(corpo.inventario.itens.values())
            
            if corpo.inventario.moedas == 0 and not itens_lista:
                print("  (Os bolsos estão completamente vazios)")
                
            for i, dados in enumerate(itens_lista):
                obj = dados["objeto"]
                qtd = dados["quantidade"]
                peso_total = obj.peso * qtd
                print(f"[{i+1}] {obj.nome.ljust(20)} (Qtd: {qtd}) | Peso: {peso_total:.1f}kg")
                
            print("-" * 40)
            if corpo.inventario.moedas > 0 or itens_lista:
                print("[T] Pegar Tudo")
            print("[0] Sair do saque")
            
            escolha = input("\nO que queres pegar? ").strip().upper()
            
            if escolha == '0':
                print("Levantas-te e deixas o corpo.")
                break
                
            elif escolha == 'T':
                # Transferir Moedas
                if corpo.inventario.moedas > 0:
                    jogador.inventario.adicionar_moedas(corpo.inventario.moedas)
                    print(f"🪙 Pegaste {corpo.inventario.moedas} moedas de ouro.")
                    corpo.inventario.remover_moedas(corpo.inventario.moedas)
                
                # Transferir Itens
                ids_para_transferir = list(corpo.inventario.itens.keys())
                for id_item in ids_para_transferir:
                    qtd = corpo.inventario.itens[id_item]["quantidade"]
                    # 1. Guardamos o nome do item ANTES de o apagar do corpo
                    nome_item = corpo.inventario.itens[id_item]["objeto"].nome 
                    
                    # 2. Fazemos a transferência
                    sucesso = corpo.inventario.transferir_item(id_item, qtd, jogador.inventario)
                    
                    # 3. Imprimimos o nome guardado!
                    if sucesso:
                        print(f"📦 Pegaste {qtd}x {nome_item}.")
                        
            else:
                try:
                    idx = int(escolha) - 1
                    if 0 <= idx < len(itens_lista):
                        id_item = itens_lista[idx]["objeto"].id
                        qtd_maxima = itens_lista[idx]["quantidade"]
                        nome_item = itens_lista[idx]["objeto"].nome
                        
                        # Transfere tudo desse item específico
                        sucesso = corpo.inventario.transferir_item(id_item, qtd_maxima, jogador.inventario)
                        if sucesso:
                            print(f"📦 Pegaste {qtd_maxima}x {nome_item}.")
                except ValueError:
                    print("Opção inválida.")