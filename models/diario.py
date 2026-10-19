class Diario:
    def __init__(self):
        self.missoes = {}      # Ex: {"anel_elfico": {"nome": "O Anel do Moribundo", "status": "ativa", "etapa_atual": "Encontrar a vila.", "tipo": "principal"}}
        self.bestiario = {}    # Ex: {"goblin": {"nome": "Goblin", "encontros": 1, "abates": 5, "descricao": "Criaturas nojentas."}}
        self.conhecidos = {}   # Ex: {"anciao_elrond": {"nome": "Elrond", "faccao": "Elfos", "notas": ["Ele não confia em anões."]}}

    # --- MISSÕES ---
    def adicionar_missao(self, id_missao: str, nome: str, etapa_inicial: str, tipo: str = "secundaria"):
        if id_missao not in self.missoes:
            self.missoes[id_missao] = {
                "nome": nome,
                "status": "ativa",
                "etapa_atual": etapa_inicial,
                "tipo": "principal" if tipo.lower() == "principal" else "secundaria"
            }
            print(f"\n📜 [NOVA MISSÃO]: {nome}")
            print(f"   Objetivo: {etapa_inicial}")

    def atualizar_missao(self, id_missao: str, nova_etapa: str, concluir: bool = False, falhar: bool = False):
        if id_missao in self.missoes:
            if concluir:
                self.missoes[id_missao]["status"] = "concluida"
                self.missoes[id_missao]["etapa_atual"] = "Missão finalizada com sucesso."
                print(f"\n✅ [MISSÃO CONCLUÍDA]: {self.missoes[id_missao]['nome']}")
            elif falhar:
                self.missoes[id_missao]["status"] = "falhada"
                self.missoes[id_missao]["etapa_atual"] = "Falhaste neste objetivo."
                print(f"\n❌ [MISSÃO FALHADA]: {self.missoes[id_missao]['nome']}")
            else:
                self.missoes[id_missao]["etapa_atual"] = nova_etapa
                print(f"\n📜 [MISSÃO ATUALIZADA]: {self.missoes[id_missao]['nome']}")
                print(f"   Novo Objetivo: {nova_etapa}")

    # --- BESTIÁRIO ---
    def registrar_monstro(self, id_monstro: str, nome: str, abate: bool = False):
        if id_monstro not in self.bestiario:
            self.bestiario[id_monstro] = {"nome": nome, "encontros": 0, "abates": 0, "descricao_desbloqueada": False}
            print(f"\n📖 [BESTIÁRIO ATUALIZADO]: Uma nova criatura foi registada ({nome}).")

        if abate:
            self.bestiario[id_monstro]["abates"] += 1
            # Se matou 3, desbloqueia fraquezas no diário (Lógica ao estilo The Witcher/BG3)
            if self.bestiario[id_monstro]["abates"] == 3 and not self.bestiario[id_monstro]["descricao_desbloqueada"]:
                self.bestiario[id_monstro]["descricao_desbloqueada"] = True
                print(f"📖 [BESTIÁRIO]: Aprendeste os segredos anatómicos de {nome}!")
        else:
            self.bestiario[id_monstro]["encontros"] += 1

    # --- NPCs CONHECIDOS ---
    def conhecer_npc(self, id_npc: str, nome: str, nota: str):
        if id_npc not in self.conhecidos:
            self.conhecidos[id_npc] = {"nome": nome, "notas": []}
        if nota not in self.conhecidos[id_npc]["notas"]:
            self.conhecidos[id_npc]["notas"].append(nota)
            print(f"\n✍️ [DIÁRIO]: Nova anotação sobre {nome}.")

    # --- EXIBIÇÃO ---
    def exibir_tela_diario(self):
        print("\n" + "="*50)
        print(" 📓 O TEU DIÁRIO DE AVENTURAS ".center(50, "="))
        
        print("\n--- MISSÕES PRINCIPAIS ---")
        principais = {k: v for k, v in self.missoes.items() if v["tipo"] == "principal"}
        if not principais: print(" Nenhuma missão principal.")
        for k, v in principais.items():
            icone = "✅" if v["status"] == "concluida" else "❌" if v["status"] == "falhada" else "🔸"
            print(f" {icone} {v['nome']}\n    Objetivo: {v['etapa_atual']}")

        print("\n--- MISSÕES SECUNDÁRIAS ---")
        secundarias = {k: v for k, v in self.missoes.items() if v["tipo"] == "secundaria"}
        if not secundarias: print(" Nenhuma missão secundária.")
        for k, v in secundarias.items():
            icone = "✅" if v["status"] == "concluida" else "❌" if v["status"] == "falhada" else "🔹"
            print(f" {icone} {v['nome']}\n    Objetivo: {v['etapa_atual']}")

        print("\n--- BESTIÁRIO DE VALENOR ---")
        if not self.bestiario: print(" Ainda não conheceste criaturas.")
        for k, v in self.bestiario.items():
            print(f" 🦇 {v['nome']} (Abates: {v['abates']})")
            if v["descricao_desbloqueada"]:
                print("    [Info Desbloqueada]: Ponto fraco registado.")

        print("\n--- PESSOAS IMPORTANTES ---")
        if not self.conhecidos: print(" És um estranho neste mundo. Não conheces ninguém.")
        for k, v in self.conhecidos.items():
            print(f" 👤 {v['nome']}")
            for nota in v["notas"]:
                print(f"    - {nota}")
        print("="*50 + "\n")