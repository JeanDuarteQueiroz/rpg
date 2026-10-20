import random
from time import sleep

class MotorEventos:
    def __init__(self, relogio, mundo_estado, banco_eventos, banco_dados):
        self.relogio = relogio
        self.mundo_estado = mundo_estado
        self.banco_eventos = banco_eventos
        self.banco_dados = banco_dados # Referência ao BancoDeDados para buscar itens/inimigos

    def traduzir_ou_embaralhar(self, texto: str, idioma: str, jogador) -> str:
        if idioma == "comum" or idioma in getattr(jogador, "idiomas_conhecidos", ["comum"]):
            return texto
        vogais, consoantes = "aeiouyAEIOUY", "bcdfghjklmnpqrstvwxzBCDFGHJKLMNPQRSTVWXZ"
        texto_estranho = "".join(
            random.choice("aeiou") if c in vogais else 
            random.choice("krtzgbl") if c in consoantes else c 
            for c in texto
        )
        return f"[{idioma.capitalize()} Desconhecido] '{texto_estranho.capitalize()}'"

    def verificar_gatilhos(self, jogador, id_local: str) -> dict:
        """Filtra qual evento deve acontecer com base nos gatilhos e requisitos globais."""
        for id_ev, evento in self.banco_eventos.items():
            gatilhos = evento.get("gatilhos", {})
            requisitos = evento.get("requisitos_globais", {})

            # 1. Gatilhos de Local e Clima
            if gatilhos.get("local") and gatilhos["local"] != id_local: continue
            if gatilhos.get("clima_necessario") and self.relogio.clima_atual not in gatilhos["clima_necessario"]: continue
            if random.randint(1, 100) > gatilhos.get("chance_disparo", 100): continue

            # 2. Requisitos Globais de História e Inventário
            if any(not self.mundo_estado.get(ev, False) for ev in requisitos.get("historia_necessaria", [])): continue
            if any(self.mundo_estado.get(ev, False) for ev in requisitos.get("historia_bloqueada", [])): continue
            if any(item not in jogador.inventario.itens for item in requisitos.get("itens_necessarios", [])): continue

            return evento # Evento validado para disparar
            
        return None

    def _validar_requisitos_ocultos(self, opcao: dict, jogador) -> bool:
        """Avalia se uma opção deve aparecer para o jogador."""
        reqs = opcao.get("req_oculto", {})
        if not reqs: return True
        
        if "percepcao_passiva" in reqs and jogador.percepcao_passiva < reqs["percepcao_passiva"]:
            return False
        if "item_necessario" in reqs and reqs["item_necessario"] not in jogador.inventario.itens:
            return False
        if "evento_necessario" in reqs and not self.mundo_estado.get(reqs["evento_necessario"], False):
            return False
            
        return True

    def executar_evento(self, evento: dict, jogador, expressao_rolagem_func) -> str | dict:
        print("\n" + "="*60)
        print(f"📖 {evento.get('nome', evento.get('id')).upper().center(56)} 📖")
        print("="*60)
        sleep(1)

        no_atual_id = "inicio"
        nos = evento.get("nos", {})

        while True:
            if no_atual_id not in nos:
                print(f"[Erro] Nó '{no_atual_id}' não encontrado.")
                return "explorar"
                
            no = nos[no_atual_id]
            
            # --- 1. NARRATIVA E MUDANÇAS DE MUNDO ---
            if "alterar_estado_mundo" in no:
                for chave, valor in no["alterar_estado_mundo"].items():
                    self.mundo_estado[chave] = valor

            if "narrador" in no:
                print(f"\n{no['narrador']}")
                sleep(1)
                
            if "falas" in no:
                print("")
                for fala in no["falas"]:
                    texto_final = self.traduzir_ou_embaralhar(fala["texto"], fala.get("idioma", "comum"), jogador)
                    print(f"🗣️ {fala.get('orador', 'Alguém')}: {texto_final}")
                    sleep(1.5)

            # --- 2. FILTRAR E EXIBIR OPÇÕES ---
            opcoes_brutas = no.get("opcoes", [])
            if not opcoes_brutas:
                return "explorar" # Beco sem saída encerra o evento
                
            opcoes_visiveis = [op for op in opcoes_brutas if self._validar_requisitos_ocultos(op, jogador)]
            
            print("\nO QUE VOCÊ FAZ?")
            for i, op in enumerate(opcoes_visiveis):
                print(f" [{i+1}] {op['texto']}")

            # --- 3. PROCESSAR A ESCOLHA ---
            while True:
                escolha_input = input("\nSua escolha: ").strip()
                if not escolha_input.isdigit() or not (1 <= int(escolha_input) <= len(opcoes_visiveis)):
                    print("Opção inválida.")
                    continue
                    
                op_escolhida = opcoes_visiveis[int(escolha_input) - 1]
                acao = op_escolhida.get("acao", "avancar")
                
                # AÇÃO: ENCERRAR
                if acao == "encerrar":
                    print("\n" + "-"*60)
                    return "explorar"
                    
                # AÇÃO: COMBATE
                elif acao == "combate":
                    return {"acao": "combate", "inimigos": op_escolhida.get("inimigos_ids", [])}
                    
                # AÇÃO: AVANÇAR (Mover de Nó)
                elif acao == "avancar":
                    no_atual_id = op_escolhida.get("destino", "inicio")
                    break 
                    
                # AÇÃO: RECEBER ITEM
                elif acao == "receber_item":
                    id_item = op_escolhida.get("id_item")
                    qtd = op_escolhida.get("quantidade", 1)
                    item_obj = self.banco_dados.obter_item(id_item) # Busca no banco
                    
                    if item_obj:
                        jogador.inventario.adicionar_item(item_obj, qtd)
                        print(f"\n🎒 [INVENTÁRIO] Você obteve: {qtd}x {item_obj.nome}!")
                        
                        if op_escolhida.get("equipar"):
                            if hasattr(item_obj, "propriedades"): # Simplificação: checa se é arma
                                jogador.equipar_arma(item_obj)
                                print(f"⚔️ Você empunhou {item_obj.nome}.")
                    else:
                        print(f"\n[Erro] Item '{id_item}' não existe no Banco de Dados.")
                        
                    no_atual_id = op_escolhida.get("destino", "inicio")
                    break

                # AÇÃO: TESTE (Perícia ou Atributo)
                elif acao == "teste":
                    tipo = op_escolhida.get("tipo_teste")
                    alvo = op_escolhida.get("alvo_teste")
                    cd = op_escolhida.get("cd", 10)
                    
                    if tipo == "atributo":
                        mod = jogador.modificador(alvo)
                        texto_teste = f"Teste de {alvo.title()}"
                    else: # pericia
                        atributo_base = op_escolhida.get("atributo_base", "sabedoria")
                        mod = jogador.modificador(atributo_base)
                        if alvo in jogador.proficiencia_pericias:
                            mod += jogador.bonus_proficiencia
                            texto_teste = f"Teste de {alvo.title()} (+Prof)"
                        else:
                            texto_teste = f"Teste de {alvo.title()}"
                            
                    d20 = expressao_rolagem_func("1d20", "total")
                    total = d20 + mod
                    
                    print(f"\n🎲 {texto_teste}: Rolaste {d20} + {mod} = {total} (CD: {cd})")
                    sleep(1.5)
                    
                    if total >= cd:
                        print("✅ Sucesso!")
                        no_atual_id = op_escolhida.get("destino_sucesso")
                    else:
                        print("❌ Falha...")
                        no_atual_id = op_escolhida.get("destino_falha")
                    break