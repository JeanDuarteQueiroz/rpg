import random
from time import sleep

class GestorCena:
    def __init__(self, relogio, mundo_estado, mapa_global):
        self.relogio = relogio
        self.mundo_estado = mundo_estado  # Dicionário de eventos globais
        self.mapa_global = mapa_global    # O JSON lido com todos os locais (cidades, florestas, etc)
        
        # Guarda o estado de cada cena (se o jogador já encontrou coisas ocultas lá)
        # Ex: {"cabana_rio": {"rota_oculta_rio": True}}
        self.estado_cenas = {}

    def validar_requisitos(self, requisitos: dict, jogador) -> tuple[bool, str]:
        """Avalia se o clima, itens ou eventos impedem ou liberam uma rota/segredo."""
        if not requisitos:
            return True, ""

        # Verifica o Clima
        climas_proibidos = requisitos.get("clima_proibido", [])
        if self.relogio.clima_atual in climas_proibidos:
            return False, requisitos.get("mensagem_bloqueio", "O ambiente está desfavorável devido ao clima atual.")

        # Verifica Inventário
        item_necessario = requisitos.get("item_necessario")
        if item_necessario:
            tem_item = item_necessario in jogador.inventario.itens and jogador.inventario.itens[item_necessario]["quantidade"] > 0
            if not tem_item:
                return False, requisitos.get("mensagem_bloqueio", "Falta um item necessário para prosseguir.")

        # Verifica História (Eventos Globais)
        evento_necessario = requisitos.get("evento_necessario")
        if evento_necessario:
            if not self.mundo_estado.get(evento_necessario, False):
                return False, requisitos.get("mensagem_bloqueio", "Uma condição histórica não foi cumprida.")

        return True, ""

    def observar_arredores(self, jogador, id_local: str, dados_local: dict):
        """Ação genérica que rola Percepção contra os Segredos do arquivo JSON daquela sala."""
        print("\n🔍 Observando os arredores...")
        sleep(0.5)
        print("Analisando opções no local...")
        sleep(0.5)
        
        segredos = dados_local.get("elementos_escondidos", [])
        if not segredos:
            print("Você examina cada detalhe do ambiente, mas não encontra nada de incomum.")
            return

        # Garante que este local tem uma "gaveta" de memória no estado do gestor
        if id_local not in self.estado_cenas:
            self.estado_cenas[id_local] = {}
            
        estado_local_atual = self.estado_cenas[id_local]
        encontrou_algo = False

        for segredo in segredos:
            id_seg = segredo["id_segredo"]
            
            # Se o jogador já tiver descoberto este segredo antes, pula
            if estado_local_atual.get(id_seg, False):
                continue 

            # Rola a percepção
            d20 = random.randint(1, 20)
            mod_sab = jogador.modificador("sabedoria")
            # Soma a proficiência se o Jogador for perito
            if "percepcao" in jogador.proficiencia_pericias:
                mod_sab += jogador.bonus_proficiencia
                
            total_percepcao = d20 + mod_sab
            cd_necessario = segredo.get("cd_percepcao", 10)
            
            print(f"(Percepção: Rolagem {d20} + Modificador {mod_sab} = {total_percepcao} vs CD {cd_necessario})")
            sleep(0.4)

            # Compara com a Dificuldade do JSON
            if total_percepcao >= cd_necessario:
                estado_local_atual[id_seg] = True # Salva que ele encontrou para sempre!
                encontrou_algo = True
                print(f"\n✨ {segredo.get('mensagem_sucesso', 'Você encontrou algo oculto!')}")
                
                # Valida os requisitos imediatamente para avisar se está visível, mas bloqueado
                liberado, msg_bloqueio = self.validar_requisitos(segredo.get("requisitos", {}), jogador)
                if not liberado:
                    print(f"   (No entanto) {msg_bloqueio}")
            else:
                print(f"\n{segredo.get('mensagem_falha', 'Você procura, mas nada chama a atenção.')}")

        # Se já tiver encontrado tudo o que o JSON dessa sala tem a oferecer
        if not encontrou_algo and all(estado_local_atual.get(s["id_segredo"], False) for s in segredos):
            print("Você já vasculhou este lugar por completo e conhece todos os seus segredos.")

    def exibir_menu_dinamico(self, jogador, id_local: str, dados_local: dict) -> dict:
        opcoes = {}
        contador = 1
        
        # --- AÇÕES LIVRES (Sempre visíveis) ---
        opcoes[str(contador)] = {"texto": "Observar / Analisar o ambiente", "acao": "observar", "custo": 1}
        contador += 1
        opcoes[str(contador)] = {"texto": "Abrir Ficha e Inventário", "acao": "inventario", "custo": 0}
        contador += 1
        
        # --- MOVIMENTAÇÃO (Lê as Conexões Normais do JSON) ---
        for dest_id, texto_botao in dados_local.get("conexoes", {}).items():
            opcoes[str(contador)] = {
                "texto": f"Mover: {texto_botao}",
                "acao": "mover",
                "destino": dest_id,
                "custo": 2
            }
            contador += 1
            
        # --- ROTAS E AÇÕES ESCONDIDAS (Só aparecem se descobertas no Observar) ---
        segredos = dados_local.get("elementos_escondidos", [])
        estado_local_atual = self.estado_cenas.get(id_local, {})
        
        for segredo in segredos:
            if estado_local_atual.get(segredo["id_segredo"], False):
                # O botão é montado de forma diferente se a chuva ou um item bloquearem a passagem
                liberado, msg_bloqueio = self.validar_requisitos(segredo.get("requisitos", {}), jogador)
                
                if liberado:
                    opcoes[str(contador)] = {
                        "texto": f"[DESCOBERTA] {segredo.get('texto_botao', 'Avançar')}",
                        "acao": segredo.get("tipo", "nova_rota"),
                        "destino": segredo.get("destino"),
                        "custo": 2
                    }
                else:
                    opcoes[str(contador)] = {
                        "texto": f"[BLOQUEADO] {segredo.get('texto_botao', 'Avançar')}",
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
        print("-" * 60)
        
        print(" O QUE VOCÊ FAZ?")
        for k, v in opcoes.items():
            print(f" [{k}] {v['texto']}")
            
        while True:
            resp = input("\nSua escolha: ").strip()
            if resp in opcoes:
                return opcoes[resp]
            print("Opção inválida.")