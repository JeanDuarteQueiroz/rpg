import random
from time import sleep

class MotorEventos:
    def __init__(self, relogio, mundo_estado, banco_eventos):
        self.relogio = relogio
        self.mundo_estado = mundo_estado
        self.banco_eventos = banco_eventos # Dicionário carregado do eventos.json

    def traduzir_ou_embaralhar(self, texto: str, idioma: str, jogador) -> str:
        """A magia dos idiomas! Se não souber a língua, ouve sons desconexos."""
        if idioma == "comum" or idioma in getattr(jogador, "idiomas_conhecidos", ["comum"]):
            return texto
            
        # O jogador não fala o idioma, vamos embaralhar o texto preservando a pontuação
        vogais = "aeiouyAEIOUY"
        consoantes = "bcdfghjklmnpqrstvwxzBCDFGHJKLMNPQRSTVWXZ"
        
        texto_estranho = ""
        for char in texto:
            if char in vogais:
                texto_estranho += random.choice("aeiou")
            elif char in consoantes:
                texto_estranho += random.choice("krtzgbl") # Sons guturais/estranhos base
            else:
                texto_estranho += char # Mantém espaços e pontuação (! ? .)
                
        return f"[{idioma.capitalize()} Desconhecido] '{texto_estranho.capitalize()}'"

    def verificar_gatilhos(self, jogador, id_local: str) -> dict:
        """Varre todos os eventos e vê qual quer sequestrar a cena."""
        # Nota: Num jogo enorme, filtrariamos por região primeiro para otimizar
        for id_ev, evento in self.banco_eventos.items():
            gatilhos = evento.get("gatilhos", {})
            requisitos = evento.get("requisitos", {})

            # 1. Verifica Requisitos de História
            ev_nec = requisitos.get("evento_necessario")
            ev_bloq = requisitos.get("evento_bloqueado")
            
            if ev_nec and not self.mundo_estado.get(ev_nec, False): continue
            if ev_bloq and self.mundo_estado.get(ev_bloq, False): continue

            # 2. Verifica Gatilhos Locais/Clima
            if gatilhos.get("local") and gatilhos["local"] != id_local: continue
            
            climas = gatilhos.get("clima_necessario", [])
            if climas and self.relogio.clima_atual not in climas: continue

            # 3. Rolagem de Sorte (Para encontros aleatórios na floresta, ex: 30%)
            chance = gatilhos.get("chance_disparo", 100)
            if random.randint(1, 100) > chance: continue

            # Passou em tudo! Este evento vai disparar!
            return evento
            
        return None # Nenhum evento ativado

    def executar_evento(self, evento: dict, jogador, expressao_rolagem_func) -> str:
        """Navega pela Árvore de Nós do Evento. Retorna 'explorar' ou 'combate'."""
        
        print("\n" + "="*60)
        print(f"📖  EVENTO: {evento.get('id').replace('_', ' ').title().center(44)}  📖")
        print("="*60)
        sleep(1)

        no_atual_id = "inicio"
        nos = evento.get("nos", {})

        while True:
            if no_atual_id not in nos:
                print("ERRO: Nó de evento não encontrado.")
                return "explorar"
                
            no = nos[no_atual_id]
            
            # --- 1. NARRADOR E MUDANÇAS DE MUNDO ---
            if "narrador" in no:
                print(f"\n{no['narrador']}")
                sleep(1)
                
            if "alterar_mundo_estado" in no:
                for chave, valor in no["alterar_mundo_estado"].items():
                    self.mundo_estado[chave] = valor

            # --- 2. FALAS DE NPCS (Com verificação de Idioma!) ---
            if "falas" in no:
                print("")
                for fala in no["falas"]:
                    texto_final = self.traduzir_ou_embaralhar(fala["texto"], fala.get("idioma", "comum"), jogador)
                    print(f"🗣️  {fala['orador']}: {texto_final}")
                    sleep(1.5)

            # --- 3. OPÇÕES DE ESCOLHA DO JOGADOR ---
            opcoes = no.get("opcoes", [])
            if not opcoes:
                # Beco sem saída sem opções, encerra automaticamente
                return "explorar"
                
            print("\nO QUE VOCÊ FAZ?")
            for i, op in enumerate(opcoes):
                print(f" [{i+1}] {op['texto']}")

            while True:
                try:
                    escolha = int(input("\nSua escolha: "))
                    if 1 <= escolha <= len(opcoes):
                        op_escolhida = opcoes[escolha-1]
                        acao = op_escolhida.get("acao")
                        
                        # Processa a acao escolhida
                        if acao == "encerrar_evento":
                            print("\n" + "-"*60)
                            return "explorar"
                            
                        elif acao == "iniciar_combate":
                            # Retorna o comando e a lista de inimigos para o Gestor de Cena iniciar o Motor de Combate!
                            return {"acao": "combate", "inimigos": op_escolhida.get("npc_ids", [])}
                            
                        elif acao == "avancar_no":
                            # Custos (Opcional, ex: Pagar pedágio)
                            if "custo_moedas" in op_escolhida:
                                if jogador.inventario.moedas >= op_escolhida["custo_moedas"]:
                                    jogador.inventario.remover_moedas(op_escolhida["custo_moedas"])
                                else:
                                    print("Não tens moedas suficientes!")
                                    continue # Impede o avanço e pede nova escolha
                                    
                            no_atual_id = op_escolhida["destino"]
                            break # Sai do loop de input e carrega o novo nó
                            
                        elif acao == "teste_atributo":
                            # Rola um atributo para ver se o jogador convence/intimide
                            atributo = op_escolhida["atributo"]
                            cd = op_escolhida["cd"]
                            mod = jogador.modificador(atributo)
                            d20 = expressao_rolagem_func("1d20", "total")
                            total = d20 + mod
                            
                            print(f"\n🎲 Teste de {atributo.title()}: Rolaste {d20} + {mod} = {total} (CD: {cd})")
                            sleep(1)
                            
                            if total >= cd:
                                print("✅ Sucesso!")
                                no_atual_id = op_escolhida["destino_sucesso"]
                            else:
                                print("❌ Falha...")
                                no_atual_id = op_escolhida["destino_falha"]
                            break
                            
                except ValueError: pass
                print("Opção inválida.")