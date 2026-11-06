"""Interface desktop do Trilha Cidadã: visual escuro, histórico e avaliações."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, simpledialog
from pathlib import Path
from datetime import datetime
import threading
import time
import webbrowser


class TrilhaCidadaApp:
    # Paleta escura de baixo brilho e contraste confortável.
    FUNDO = "#0D131D"
    SIDEBAR = "#101925"
    TOPO = "#121C29"
    CARTAO = "#172332"
    CARTAO_2 = "#1D2B3B"
    CARTAO_ATIVO = "#24374A"
    TEXTO = "#E7EDF5"
    TEXTO_SUAVE = "#A8B6C7"
    TEXTO_MUTED = "#7D8DA2"
    DESTAQUE = "#3AB7A5"
    DESTAQUE_CLARO = "#8BE0D5"
    AZUL = "#81AFFF"
    ALERTA = "#E7B86E"
    ERRO = "#F08080"
    BORDA = "#2A394B"
    FONTE = "{Segoe UI}"

    def __init__(self, assistente):
        self.assistente = assistente
        self.root = tk.Tk()
        try:
            self.versao = Path(__file__).with_name("VERSION").read_text(encoding="utf-8").strip()
        except OSError:
            self.versao = "4.5.0"
        self.root.title(f"Trilha Cidadã V{self.versao} | Trabalho, direitos e oportunidades")
        self.root.geometry("1280x820")
        self.root.minsize(1050, 680)
        self.root.configure(bg=self.FUNDO)

        self.nav_botoes = {}
        self.pagina_ativa = None
        self.resultado_atual = None
        self.pergunta_atual = ""
        self.status_atual = None
        self.inicio_busca = None
        self.tentativas_busca = 0
        self.busca_em_andamento = False
        self.botao_busca = None
        self.filtro_historico = "Todas"
        self.busca_historico_var = tk.StringVar(value="")
        self.orientacao_aberta = None
        self.tempo_inicio_orientacao = None

        self._configurar_estilos()
        self._montar_estrutura()
        self.root.protocol("WM_DELETE_WINDOW", self.fechar)
        self.mostrar_inicio()

    def _configurar_estilos(self):
        self.root.option_add("*Font", f"{self.FONTE} 10")
        self.root.option_add("*Button.Cursor", "hand2")
        self.root.option_add("*Entry.Font", (self.FONTE, 11))

    # ------------------------------------------------------------------
    # Estrutura global e componentes visuais
    # ------------------------------------------------------------------
    def _montar_estrutura(self):
        self.sidebar = tk.Frame(self.root, bg=self.SIDEBAR, width=252)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        marca = tk.Frame(self.sidebar, bg=self.SIDEBAR)
        marca.pack(fill="x", padx=24, pady=(28, 30))
        tk.Label(marca, text="✦", font=(self.FONTE, 22, "bold"), fg=self.DESTAQUE, bg=self.SIDEBAR).pack(anchor="w")
        tk.Label(marca, text="TRILHA CIDADÃ", font=(self.FONTE, 15, "bold"), fg=self.TEXTO, bg=self.SIDEBAR).pack(anchor="w", pady=(5, 0))
        tk.Label(marca, text="INFORMAÇÃO QUE ABRE CAMINHOS", font=(self.FONTE, 7, "bold"), fg=self.TEXTO_MUTED, bg=self.SIDEBAR).pack(anchor="w", pady=(4, 0))

        self._rotulo_grupo("INÍCIO")
        self._botao_nav("⌂", "Visão geral", self.mostrar_inicio)
        self._rotulo_grupo("ATENDIMENTO")
        self._botao_nav("＋", "Fazer uma pergunta", self.mostrar_busca)
        self._botao_nav("▦", "Explorar categorias", self.mostrar_categorias)
        self._botao_nav("◷", "Histórico de perguntas", self.mostrar_historico)
        self._rotulo_grupo("QUALIDADE")
        self._botao_nav("★", "Avaliações", self.mostrar_avaliacoes)
        self._botao_nav("▤", "Indicadores", self.mostrar_indicadores)
        self._rotulo_grupo("INFORMAÇÕES")
        self._botao_nav("ⓘ", "Fontes e transparência", self.mostrar_fontes)

        rodape = tk.Frame(self.sidebar, bg=self.SIDEBAR)
        rodape.pack(side="bottom", fill="x", padx=19, pady=19)
        tk.Frame(rodape, bg=self.BORDA, height=1).pack(fill="x", pady=(0, 13))
        tk.Label(rodape, text="PRIVACIDADE EM PRIMEIRO LUGAR", font=(self.FONTE, 8, "bold"), fg=self.DESTAQUE_CLARO, bg=self.SIDEBAR).pack(anchor="w")
        tk.Label(
            rodape,
            text="Não informe CPF, telefone, e-mail\nou senhas durante o atendimento.",
            justify="left", font=(self.FONTE, 8), fg=self.TEXTO_SUAVE,
            bg=self.SIDEBAR, wraplength=205,
        ).pack(anchor="w", pady=(6, 0))

        self.area = tk.Frame(self.root, bg=self.FUNDO)
        self.area.pack(side="left", fill="both", expand=True)

        topo = tk.Frame(self.area, bg=self.TOPO, height=62, highlightthickness=1, highlightbackground=self.BORDA)
        topo.pack(side="top", fill="x")
        topo.pack_propagate(False)
        tk.Label(
            topo, text="CENTRAL DE ORIENTAÇÃO  /  TRILHA CIDADÃ",
            font=(self.FONTE, 8, "bold"), fg=self.TEXTO_SUAVE, bg=self.TOPO,
        ).pack(side="left", padx=28)

        status = tk.Frame(topo, bg=self.TOPO)
        status.pack(side="right", padx=26)
        ia_configurada = bool(self.assistente.expansor_ia)
        cor_status = self.DESTAQUE if ia_configurada else self.ALERTA
        texto_status = "OLLAMA CLOUD CONFIGURADO" if ia_configurada else "BUSCA LOCAL"
        tk.Label(status, text="●", font=(self.FONTE, 9, "bold"), fg=cor_status, bg=self.TOPO).pack(side="left", padx=(0, 7))
        tk.Label(status, text=texto_status, font=(self.FONTE, 8, "bold"), fg=cor_status, bg=self.TOPO).pack(side="left")
        tk.Label(status, text=f"  ·  V{self.versao}", font=(self.FONTE, 8), fg=self.TEXTO_MUTED, bg=self.TOPO).pack(side="left", padx=(7, 0))

        corpo = tk.Frame(self.area, bg=self.FUNDO)
        corpo.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(corpo, bg=self.FUNDO, highlightthickness=0, bd=0)
        self.rolagem = tk.Scrollbar(
            corpo, orient="vertical", command=self.canvas.yview,
            bg=self.CARTAO_2, troughcolor=self.FUNDO, activebackground=self.DESTAQUE,
            bd=0, width=10, highlightthickness=0,
        )
        self.canvas.configure(yscrollcommand=self.rolagem.set)
        self.rolagem.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.conteudo = tk.Frame(self.canvas, bg=self.FUNDO, padx=34, pady=28)
        self.janela_conteudo = self.canvas.create_window((0, 0), window=self.conteudo, anchor="nw")
        self.conteudo.bind("<Configure>", lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self.janela_conteudo, width=e.width))
        self.canvas.bind_all("<MouseWheel>", self._rolar)
        self.root.bind("<Control-l>", lambda _e: self.mostrar_busca())
        self.root.bind("<Control-L>", lambda _e: self.mostrar_busca())

    def _rotulo_grupo(self, texto):
        tk.Label(
            self.sidebar, text=texto, font=(self.FONTE, 7, "bold"),
            fg=self.TEXTO_MUTED, bg=self.SIDEBAR,
        ).pack(anchor="w", padx=22, pady=(11, 6))

    def _botao_nav(self, simbolo, texto, comando):
        botao = tk.Button(
            self.sidebar, text=f"{simbolo}     {texto}", command=comando,
            anchor="w", bd=0, relief="flat", cursor="hand2",
            bg=self.SIDEBAR, fg=self.TEXTO_SUAVE,
            activebackground=self.CARTAO_ATIVO, activeforeground=self.TEXTO,
            font=(self.FONTE, 9), padx=17, pady=10,
            highlightthickness=0, borderwidth=0,
        )
        botao.pack(fill="x", padx=10, pady=2)
        self.nav_botoes[texto] = botao

    def _rolar(self, evento):
        if getattr(evento, "delta", 0):
            self.canvas.yview_scroll(int(-1 * (evento.delta / 120)), "units")

    def _set_nav_ativa(self, texto):
        self.pagina_ativa = texto
        for nome, botao in self.nav_botoes.items():
            ativo = nome == texto
            botao.configure(
                bg=self.CARTAO_ATIVO if ativo else self.SIDEBAR,
                fg=self.DESTAQUE_CLARO if ativo else self.TEXTO_SUAVE,
                font=(self.FONTE, 9, "bold" if ativo else "normal"),
                highlightthickness=0,
            )

    def _limpar(self):
        for widget in self.conteudo.winfo_children():
            widget.destroy()
        self.canvas.yview_moveto(0)

    def _cabecalho(self, titulo, subtitulo, etiqueta=None):
        topo = tk.Frame(self.conteudo, bg=self.FUNDO)
        topo.pack(fill="x", pady=(0, 22))
        if etiqueta:
            tk.Label(topo, text=etiqueta.upper(), font=(self.FONTE, 7, "bold"), fg=self.DESTAQUE_CLARO, bg=self.FUNDO).pack(anchor="w", pady=(0, 7))
        tk.Label(topo, text=titulo, font=(self.FONTE, 23, "bold"), fg=self.TEXTO, bg=self.FUNDO).pack(anchor="w")
        tk.Label(topo, text=subtitulo, font=(self.FONTE, 9), fg=self.TEXTO_SUAVE, bg=self.FUNDO, wraplength=1000, justify="left").pack(anchor="w", pady=(6, 0))

    def _painel(self, pai, padding=16, cor=None):
        return tk.Frame(
            pai, bg=cor or self.CARTAO, padx=padding, pady=padding,
            highlightthickness=1, highlightbackground=self.BORDA,
        )

    def _cartao_metrica(self, pai, titulo, valor, detalhe, cor=None):
        quadro = self._painel(pai, 15)
        tk.Label(quadro, text=titulo.upper(), font=(self.FONTE, 7, "bold"), fg=self.TEXTO_MUTED, bg=self.CARTAO).pack(anchor="w")
        tk.Label(quadro, text=valor, font=(self.FONTE, 21, "bold"), fg=cor or self.TEXTO, bg=self.CARTAO).pack(anchor="w", pady=(5, 0))
        tk.Label(quadro, text=detalhe, font=(self.FONTE, 8), fg=self.TEXTO_SUAVE, bg=self.CARTAO).pack(anchor="w", pady=(3, 0))
        return quadro

    def _botao(self, pai, texto, comando, cor=None, fg=None, compacto=False):
        fundo = cor or self.DESTAQUE
        frente = fg or (self.SIDEBAR if fundo == self.DESTAQUE else self.TEXTO)
        return tk.Button(
            pai, text=texto, command=comando, cursor="hand2", bd=0,
            bg=fundo, fg=frente, activebackground=self.CARTAO_ATIVO,
            activeforeground=self.TEXTO, font=(self.FONTE, 8, "bold"),
            padx=13 if compacto else 16, pady=7 if compacto else 10,
            highlightthickness=0, relief="flat",
        )

    def _texto(self, pai, conteudo, altura=8):
        caixa = tk.Text(
            pai, height=altura, wrap="word", bg=self.CARTAO_2, fg=self.TEXTO,
            insertbackground=self.TEXTO, relief="flat", bd=0,
            padx=15, pady=14, font=(self.FONTE, 10),
            highlightthickness=1, highlightbackground=self.BORDA,
            selectbackground=self.CARTAO_ATIVO, selectforeground=self.TEXTO,
        )
        caixa.insert("1.0", conteudo)
        caixa.configure(state="disabled")
        return caixa

    def _label(self, pai, texto, tamanho=9, peso="normal", cor=None, **kwargs):
        return tk.Label(
            pai, text=texto, font=(self.FONTE, tamanho, peso),
            fg=cor or self.TEXTO, bg=kwargs.pop("bg", self.CARTAO), **kwargs,
        )

    @staticmethod
    def _data_legivel(valor):
        try:
            data = datetime.fromisoformat(str(valor))
            return data.astimezone().strftime("%d/%m/%Y · %H:%M")
        except (TypeError, ValueError):
            return str(valor or "Data não disponível")

    def _titulo_orientacao(self, identificador):
        if not identificador:
            return "Orientação geral ou não vinculada a um registro específico"
        for item in self.assistente.base.orientacoes:
            if item.id == identificador:
                return item.titulo
        return "Orientação não disponível nesta versão da base"

    # ------------------------------------------------------------------
    # Encerramento
    # ------------------------------------------------------------------
    def fechar(self):
        nota = simpledialog.askinteger(
            "Avalie o Trilha Cidadã",
            "De 1 a 5, quão fácil foi utilizar o assistente?",
            minvalue=1, maxvalue=5, parent=self.root,
        )
        if nota is None:
            sair = messagebox.askyesno(
                "Encerrar sem avaliação?",
                "A avaliação ajuda a equipe a melhorar o sistema. Deseja sair sem avaliar?",
                parent=self.root,
            )
            if not sair:
                return
        else:
            salvo = self.assistente.registrar_facilidade(nota)
            if not salvo:
                messagebox.showwarning(
                    "Avaliação não salva",
                    "A nota foi considerada nesta sessão, mas não foi possível confirmar a gravação em disco.",
                    parent=self.root,
                )
        try:
            self.assistente.exportar_csv()
        except OSError as erro:
            messagebox.showerror("Falha na exportação", f"Não foi possível exportar os atendimentos:\n{erro}", parent=self.root)
        self.root.destroy()

    # ------------------------------------------------------------------
    # Visão geral
    # ------------------------------------------------------------------
    def mostrar_inicio(self):
        self._set_nav_ativa("Visão geral")
        self._limpar()
        self._cabecalho(
            "Orientação clara para sua vida profissional.",
            "Acesse informações sobre emprego, direitos, qualificação e próximos passos.",
            "Seu espaço de orientação",
        )

        hero = tk.Frame(self.conteudo, bg="#142F3A", highlightthickness=1, highlightbackground="#285766")
        hero.pack(fill="x", pady=(0, 18))
        bloco = tk.Frame(hero, bg="#142F3A")
        bloco.pack(side="left", fill="both", expand=True, padx=22, pady=19)
        tk.Label(bloco, text="TRILHA CIDADÃ  ·  ASSISTENTE COM IA", font=(self.FONTE, 7, "bold"), fg=self.DESTAQUE_CLARO, bg="#142F3A").pack(anchor="w")
        tk.Label(bloco, text="Qual é o próximo passo\nque você precisa dar?", font=(self.FONTE, 18, "bold"), fg=self.TEXTO, bg="#142F3A", justify="left").pack(anchor="w", pady=(7, 6))
        tk.Label(bloco, text="Pergunte com suas próprias palavras. A IA ajuda a interpretar; as orientações mostram suas fontes.", font=(self.FONTE, 8), fg="#B7C9D2", bg="#142F3A", wraplength=610, justify="left").pack(anchor="w")
        self._botao(hero, "COMEÇAR UMA PERGUNTA  →", self.mostrar_busca).pack(side="right", padx=22, pady=24)

        dados = self.assistente.indicadores()
        cards = tk.Frame(self.conteudo, bg=self.FUNDO)
        cards.pack(fill="x", pady=(0, 18))
        itens = [
            ("Atendimentos", str(dados["total"]), "Perguntas registradas", self.AZUL),
            ("Resolução", f"{dados['taxa_resolucao']:.0f}%" if dados["total"] else "—", "Respostas que ajudaram", self.DESTAQUE),
            ("Facilidade", f"{dados['facilidade_media']:.1f}/5" if dados["total_avaliacoes"] else "—", f"{dados['total_avaliacoes']} avaliações", self.ALERTA),
            ("Base verificada", str(len(self.assistente.base.orientacoes)), "Orientações cadastradas", self.DESTAQUE_CLARO),
        ]
        for i, item in enumerate(itens):
            card = self._cartao_metrica(cards, *item)
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 9, 0))
            cards.grid_columnconfigure(i, weight=1, uniform="metricas")

        titulo_atalhos = tk.Frame(self.conteudo, bg=self.FUNDO)
        titulo_atalhos.pack(fill="x", pady=(0, 9))
        self._label(titulo_atalhos, "Acesso rápido", 11, "bold", bg=self.FUNDO).pack(side="left")
        self._label(titulo_atalhos, "O que você precisa fazer agora?", 8, cor=self.TEXTO_MUTED, bg=self.FUNDO).pack(side="left", padx=10)
        atalhos = tk.Frame(self.conteudo, bg=self.FUNDO)
        atalhos.pack(fill="x", pady=(0, 19))
        opcoes = [
            ("＋", "Perguntar à IA", "Tire uma dúvida em linguagem natural", self.mostrar_busca),
            ("◷", "Ver histórico", "Retome perguntas anteriores", self.mostrar_historico),
            ("★", "Minhas avaliações", "Veja os retornos registrados", self.mostrar_avaliacoes),
        ]
        for i, (icone, nome, descricao, acao) in enumerate(opcoes):
            quadro = self._painel(atalhos, 14)
            quadro.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 9, 0))
            tk.Label(quadro, text=icone, font=(self.FONTE, 17, "bold"), fg=self.DESTAQUE, bg=self.CARTAO).pack(anchor="w")
            tk.Label(quadro, text=nome, font=(self.FONTE, 10, "bold"), fg=self.TEXTO, bg=self.CARTAO).pack(anchor="w", pady=(5, 2))
            tk.Label(quadro, text=descricao, font=(self.FONTE, 8), fg=self.TEXTO_SUAVE, bg=self.CARTAO).pack(anchor="w")
            self._botao(quadro, "ABRIR  →", acao, self.CARTAO_2, self.DESTAQUE_CLARO, compacto=True).pack(anchor="w", pady=(11, 0))
            atalhos.grid_columnconfigure(i, weight=1, uniform="atalhos")

        duas_colunas = tk.Frame(self.conteudo, bg=self.FUNDO)
        duas_colunas.pack(fill="x")
        recentes = self._painel(duas_colunas, 16)
        recentes.pack(side="left", fill="both", expand=True, padx=(0, 9))
        cabecalho = tk.Frame(recentes, bg=self.CARTAO)
        cabecalho.pack(fill="x", pady=(0, 10))
        tk.Label(cabecalho, text="Perguntas recentes", font=(self.FONTE, 10, "bold"), fg=self.TEXTO, bg=self.CARTAO).pack(side="left")
        self._botao(cabecalho, "VER HISTÓRICO", self.mostrar_historico, self.CARTAO_2, self.DESTAQUE_CLARO, compacto=True).pack(side="right")
        historico = sorted(self.assistente.historico, key=lambda x: x.get("data", ""), reverse=True)[:5]
        if historico:
            for item in historico:
                self._linha_pergunta(recentes, item, compacto=True)
        else:
            self._label(recentes, "As perguntas que você fizer aparecerão aqui.", 8, cor=self.TEXTO_SUAVE).pack(anchor="w", pady=8)

        resumo = self._painel(duas_colunas, 16)
        resumo.configure(width=290)
        resumo.pack(side="left", fill="y")
        tk.Label(resumo, text="EXPLORE POR ASSUNTO", font=(self.FONTE, 8, "bold"), fg=self.TEXTO_MUTED, bg=self.CARTAO).pack(anchor="w", pady=(0, 9))
        descricoes = {
            "Currículo e entrevista": "Currículo e preparação para entrevistas",
            "Direitos e proteção": "Canais de orientação e denúncia",
            "Direitos trabalhistas": "Salário, férias, demissão e benefícios",
            "Jovem Aprendiz": "Contrato, requisitos e jornada",
            "Primeiros passos": "Carteira e primeiro emprego",
            "Programas de inclusão": "Programas sociais e inclusão produtiva",
            "Vagas e qualificação": "Vagas, cursos e qualificação",
        }
        for categoria in self.assistente.base.categorias():
            linha = tk.Frame(resumo, bg=self.CARTAO)
            linha.pack(fill="x", pady=4)
            tk.Label(linha, text="•", font=(self.FONTE, 11, "bold"), fg=self.DESTAQUE, bg=self.CARTAO).pack(side="left")
            texto = tk.Frame(linha, bg=self.CARTAO)
            texto.pack(side="left", fill="x", expand=True, padx=7)
            tk.Label(texto, text=categoria, font=(self.FONTE, 8, "bold"), fg=self.TEXTO, bg=self.CARTAO, anchor="w").pack(anchor="w")
            tk.Label(texto, text=descricoes.get(categoria, "Orientações oficiais"), font=(self.FONTE, 7), fg=self.TEXTO_MUTED, bg=self.CARTAO, anchor="w").pack(anchor="w")
            for widget in (linha, texto, *texto.winfo_children()):
                widget.bind("<Button-1>", lambda _e, cat=categoria: self.mostrar_categoria(cat))
                widget.configure(cursor="hand2")

        tk.Label(self.conteudo, text="Este assistente não é um canal oficial. Confira a fonte indicada antes de tomar decisões.", font=(self.FONTE, 8), fg=self.TEXTO_MUTED, bg=self.FUNDO).pack(anchor="w", pady=(17, 0))

    # ------------------------------------------------------------------
    # Busca / resposta
    # ------------------------------------------------------------------
    def mostrar_busca(self):
        self._set_nav_ativa("Fazer uma pergunta")
        self._limpar()
        self.inicio_busca = time.time()
        self.tentativas_busca = 0
        self._cabecalho(
            "Como podemos ajudar?",
            "Escreva sua dúvida do seu jeito. Não precisa conhecer termos técnicos.",
            "Atendimento inteligente",
        )
        painel = self._painel(self.conteudo, 17)
        painel.pack(fill="x", pady=(0, 14))
        tk.Label(painel, text="SUA PERGUNTA", font=(self.FONTE, 7, "bold"), fg=self.TEXTO_MUTED, bg=self.CARTAO).pack(anchor="w", pady=(0, 8))
        linha = tk.Frame(painel, bg=self.CARTAO)
        linha.pack(fill="x")
        self.entrada = tk.Entry(
            linha, font=(self.FONTE, 11), bg=self.CARTAO_2, fg=self.TEXTO,
            insertbackground=self.TEXTO, relief="flat", bd=0,
            highlightthickness=1, highlightbackground=self.BORDA,
            highlightcolor=self.DESTAQUE,
        )
        self.entrada.pack(side="left", fill="x", expand=True, ipady=13, ipadx=11, padx=(0, 10))
        self.entrada.bind("<Return>", lambda _e: self.buscar_na_interface())
        self.entrada.bind("<Escape>", lambda _e: self.entrada.delete(0, "end"))
        self.botao_busca = self._botao(linha, "PERGUNTAR À IA  →", self.buscar_na_interface)
        self.botao_busca.pack(side="right")
        status_ia = "IA Cloud pronta para interpretar sua pergunta." if self.assistente.expansor_ia else "IA Cloud não configurada. A busca local continua disponível."
        cor_ia = self.DESTAQUE
        tk.Label(painel, text=f"●  {status_ia}", font=(self.FONTE, 8), fg=cor_ia if self.assistente.expansor_ia else self.ALERTA, bg=self.CARTAO).pack(anchor="w", pady=(11, 0))

        tk.Label(self.conteudo, text="EXEMPLOS PARA COMEÇAR", font=(self.FONTE, 7, "bold"), fg=self.TEXTO_MUTED, bg=self.FUNDO).pack(anchor="w", pady=(6, 8))
        sugestoes = tk.Frame(self.conteudo, bg=self.FUNDO)
        sugestoes.pack(fill="x")
        exemplos = [
            "Como conseguir meu primeiro emprego?",
            "Tenho direito ao seguro-desemprego?",
            "Como pedir demissão?",
            "A empresa precisa pagar meu transporte?",
        ]
        for i, exemplo in enumerate(exemplos):
            self._botao(sugestoes, exemplo, lambda texto=exemplo: self._usar_sugestao(texto), self.CARTAO_2, self.TEXTO_SUAVE, compacto=True).grid(row=i // 2, column=i % 2, sticky="ew", padx=(0 if i % 2 == 0 else 8, 0), pady=4)
            sugestoes.grid_columnconfigure(i % 2, weight=1)

        privacidade = tk.Frame(self.conteudo, bg=self.CARTAO_2, padx=12, pady=10)
        privacidade.pack(fill="x", pady=(10, 13))
        tk.Label(privacidade, text="PRIVACIDADE", font=(self.FONTE, 7, "bold"), fg=self.ALERTA, bg=self.CARTAO_2).pack(anchor="w")
        tk.Label(privacidade, text="Não envie CPF, telefone, e-mail, endereço ou senhas. A pergunta e o catálogo de orientações são enviados ao provedor de IA quando a conexão Cloud está ativa.", font=(self.FONTE, 8), fg=self.TEXTO_SUAVE, bg=self.CARTAO_2, wraplength=950, justify="left").pack(anchor="w", pady=(4, 0))

        self.resultado_frame = tk.Frame(self.conteudo, bg=self.FUNDO)
        self.resultado_frame.pack(fill="both", expand=True)
        tk.Label(self.conteudo, text="Enter envia  ·  Esc limpa  ·  Ctrl+L abre uma nova pergunta", font=(self.FONTE, 8), fg=self.TEXTO_MUTED, bg=self.FUNDO).pack(anchor="w", pady=(12, 0))
        self.entrada.focus_set()

    def _usar_sugestao(self, pergunta):
        self.entrada.delete(0, "end")
        self.entrada.insert(0, pergunta)
        self.entrada.focus_set()

    def buscar_na_interface(self):
        pergunta = self.entrada.get().strip()
        if not pergunta:
            messagebox.showwarning("Pergunta vazia", "Digite uma dúvida para realizar a busca.", parent=self.root)
            return
        if self.assistente.contem_dados_pessoais(pergunta):
            messagebox.showwarning("Proteção de dados", "Não informe CPF, telefone, e-mail ou outros dados pessoais. Sua pergunta não foi armazenada.", parent=self.root)
            return
        if self.busca_em_andamento:
            return
        for widget in self.resultado_frame.winfo_children():
            widget.destroy()
        if self.inicio_busca is None:
            self.inicio_busca = time.time()
            self.tentativas_busca = 0
        self.tentativas_busca += 1
        inicio = self.inicio_busca
        self.pergunta_atual = pergunta
        self.busca_em_andamento = True
        if self.botao_busca:
            self.botao_busca.configure(state="disabled", text="IA ANALISANDO...")
        tk.Label(
            self.resultado_frame,
            text="✦  Interpretando sua pergunta e consultando as orientações verificadas...",
            font=(self.FONTE, 9, "bold"), fg=self.AZUL, bg=self.FUNDO,
        ).pack(anchor="w", pady=15)
        self.resultado_frame.update_idletasks()

        def executar():
            try:
                resultados, status = self.assistente.buscar_pergunta(pergunta)
                erro = ""
            except Exception as exc:
                resultados, status, erro = [], "erro_inesperado", str(exc)
            try:
                self.root.after(0, lambda: self._concluir_busca_na_interface(pergunta, inicio, resultados, status, erro))
            except tk.TclError:
                pass

        threading.Thread(target=executar, name="trilha-cidada-ia", daemon=True).start()

    def _concluir_busca_na_interface(self, pergunta, inicio, resultados, status, erro=""):
        self.busca_em_andamento = False
        if self.botao_busca and self.botao_busca.winfo_exists():
            self.botao_busca.configure(state="normal", text="PERGUNTAR À IA  →")
        for widget in self.resultado_frame.winfo_children():
            widget.destroy()
        self.status_atual = status
        self.resultado_atual = None

        if status == "base_vazia":
            self._aviso_resultado("A base de conhecimento está vazia.", "Confira o arquivo de orientações e tente novamente.", self.ALERTA)
            return
        if status == "fora_escopo":
            self._aviso_resultado(
                "Esse assunto está fora do foco do Trilha Cidadã.",
                "Nosso assistente é especializado em emprego, empregabilidade, currículo, entrevistas, qualificação, Jovem Aprendiz e direitos do trabalhador.",
                self.ALERTA,
            )
            return
        if status == "erro_inesperado":
            self._aviso_resultado("Não foi possível concluir a consulta.", erro or "Ocorreu uma falha inesperada.", self.ERRO)
            return

        if status == "encontrado":
            pontos, orientacao = resultados[0]
            self.resultado_atual = orientacao
            caixa = self._painel(self.resultado_frame, 18)
            caixa.pack(fill="x", pady=(0, 12))
            topo = tk.Frame(caixa, bg=self.CARTAO)
            topo.pack(fill="x", pady=(0, 10))
            if getattr(orientacao, "gerada_por_ia", False):
                selo, cor_selo = "✦  RESPOSTA ORGANIZADA PELA IA", self.AZUL
            elif self.assistente.ultimo_erro_ia:
                selo, cor_selo = "BASE LOCAL  ·  IA INDISPONÍVEL", self.ALERTA
            else:
                selo, cor_selo = "BUSCA PONTUADA  ·  BASE VERIFICADA", self.DESTAQUE
            tk.Label(topo, text=selo, font=(self.FONTE, 7, "bold"), fg=cor_selo, bg=self.CARTAO).pack(side="left")
            if not getattr(orientacao, "gerada_por_ia", False):
                tk.Label(topo, text=f"{('ALTA' if pontos >= 6 else 'MÉDIA')} · {pontos} pontos", font=(self.FONTE, 7, "bold"), fg=self.TEXTO_MUTED, bg=self.CARTAO).pack(side="right")

            explicacao = self.assistente.explicar_busca(pergunta, orientacao)
            if explicacao.get("termos_corrigidos"):
                tk.Label(caixa, text="AJUSTE DE DIGITAÇÃO  ·  " + ", ".join(explicacao["termos_corrigidos"]), font=(self.FONTE, 8, "bold"), fg=self.AZUL, bg=self.CARTAO).pack(anchor="w", pady=(0, 9))
            tk.Label(caixa, text=orientacao.titulo, font=(self.FONTE, 15, "bold"), fg=self.TEXTO, bg=self.CARTAO, wraplength=940, justify="left").pack(anchor="w")
            tk.Label(caixa, text=orientacao.categoria, font=(self.FONTE, 8, "bold"), fg=self.DESTAQUE_CLARO, bg=self.CARTAO).pack(anchor="w", pady=(5, 12))
            tk.Label(caixa, text=orientacao.resposta, font=(self.FONTE, 10), fg=self.TEXTO, bg=self.CARTAO, wraplength=950, justify="left").pack(anchor="w", pady=(0, 14))
            tk.Label(caixa, text="DOCUMENTOS OU INFORMAÇÕES ÚTEIS", font=(self.FONTE, 7, "bold"), fg=self.TEXTO_MUTED, bg=self.CARTAO).pack(anchor="w")
            docs = getattr(orientacao, "documentos", []) or ["Consulte a fonte oficial indicada."]
            tk.Label(caixa, text="  •  " + "\n  •  ".join(docs), font=(self.FONTE, 8), fg=self.TEXTO_SUAVE, bg=self.CARTAO, justify="left").pack(anchor="w", pady=(5, 11))
            tk.Label(caixa, text=f"ONDE: {orientacao.onde}", font=(self.FONTE, 8), fg=self.TEXTO, bg=self.CARTAO, wraplength=950, justify="left").pack(anchor="w", pady=(0, 8))
            tk.Label(caixa, text=f"Verificação: {orientacao.verificado_em}", font=(self.FONTE, 7), fg=self.TEXTO_MUTED, bg=self.CARTAO, wraplength=950, justify="left").pack(anchor="w", pady=(0, 9))

            links = []
            if orientacao.fonte:
                links.append(("Abrir fonte oficial", orientacao.fonte))
            for fonte_extra in getattr(orientacao, "fontes_adicionais", []):
                url = fonte_extra.get("url", "")
                if url and url not in [item[1] for item in links]:
                    nome = fonte_extra.get("titulo", "Fonte oficial adicional")
                    data = fonte_extra.get("verificado_em", "")
                    if data:
                        nome += f" · verificado em {data}"
                    links.append((nome, url))
            for nome, url in links:
                link = tk.Label(caixa, text=f"↗  {nome}", font=(self.FONTE, 8, "bold", "underline"), fg=self.AZUL, bg=self.CARTAO, cursor="hand2")
                link.pack(anchor="w", pady=(0, 6))
                link.bind("<Button-1>", lambda _e, endereco=url: webbrowser.open(endereco))
            if getattr(orientacao, "aviso_ia", ""):
                tk.Label(caixa, text=orientacao.aviso_ia, font=(self.FONTE, 8, "italic"), fg=self.ALERTA, bg=self.CARTAO, wraplength=950, justify="left").pack(anchor="w", pady=(4, 8))
            tk.Label(caixa, text="Este assistente não é um canal oficial. Confira a fonte antes de tomar decisões.", font=(self.FONTE, 7, "italic"), fg=self.TEXTO_MUTED, bg=self.CARTAO).pack(anchor="w", pady=(4, 0))

            alternativas = [item for item in resultados[1:3] if item[0] >= 3]
            if alternativas:
                mais = self._painel(self.resultado_frame, 13)
                mais.pack(fill="x", pady=(0, 10))
                tk.Label(mais, text="TAMBÉM PODE SER ÚTIL", font=(self.FONTE, 7, "bold"), fg=self.TEXTO_MUTED, bg=self.CARTAO).pack(anchor="w", pady=(0, 7))
                for pts, alternativa in alternativas:
                    tk.Label(mais, text=f"•  {alternativa.titulo}  ·  {pts} pontos", font=(self.FONTE, 8), fg=self.TEXTO_SUAVE, bg=self.CARTAO).pack(anchor="w", pady=2)

            acoes = self._painel(self.resultado_frame, 14)
            acoes.pack(fill="x", pady=(0, 15))
            tk.Label(acoes, text="Essa resposta resolveu sua dúvida?", font=(self.FONTE, 9, "bold"), fg=self.TEXTO, bg=self.CARTAO).pack(side="left", padx=(0, 14))
            self._botao(acoes, "SIM, AJUDOU", lambda: self._finalizar_atendimento(True, inicio)).pack(side="left", padx=4)
            self._botao(acoes, "NÃO", lambda: self._finalizar_atendimento(False, inicio), self.CARTAO_2, self.TEXTO).pack(side="left", padx=4)
        elif status == "ia_indisponivel":
            self._aviso_resultado(
                "A IA não conseguiu responder e a busca local não encontrou uma orientação segura.",
                f"Diagnóstico: {self.assistente.ultimo_erro_ia or 'Sem detalhes disponíveis.'}", self.ALERTA,
                acao=("TENTAR NOVAMENTE", self.buscar_na_interface),
            )
        else:
            sugestoes = [item for item in resultados[:2] if item[0] > 0]
            texto = "Não encontramos conteúdo verificado suficiente para essa pergunta. Se ela estiver relacionada a emprego ou direitos do trabalhador, a dúvida pode orientar uma próxima revisão da base. Consulte também o MTE pelo portal oficial ou pelo telefone 158."
            if sugestoes:
                texto += "\n\nAssuntos próximos:\n" + "\n".join(f"• {item.titulo}" for _p, item in sugestoes)
            self._aviso_resultado(
                "Ainda não encontramos uma orientação segura.", texto, self.ALERTA,
                acao=("EXPLORAR CATEGORIAS", self.mostrar_categorias),
                acao_secundaria=("REGISTRAR COMO NÃO RESOLVIDA", lambda: self._finalizar_atendimento(False, inicio)),
            )

    def _aviso_resultado(self, titulo, descricao, cor, acao=None, acao_secundaria=None):
        caixa = self._painel(self.resultado_frame, 18)
        caixa.pack(fill="x", pady=(0, 12))
        tk.Label(caixa, text=titulo, font=(self.FONTE, 13, "bold"), fg=cor, bg=self.CARTAO, wraplength=950, justify="left").pack(anchor="w")
        tk.Label(caixa, text=descricao, font=(self.FONTE, 9), fg=self.TEXTO_SUAVE, bg=self.CARTAO, wraplength=950, justify="left").pack(anchor="w", pady=(8, 0))
        if acao:
            self._botao(caixa, acao[0], acao[1]).pack(anchor="w", pady=(13, 0))
        if acao_secundaria:
            self._botao(caixa, acao_secundaria[0], acao_secundaria[1], self.CARTAO_2, self.TEXTO).pack(anchor="w", pady=(8, 0))

    def _finalizar_atendimento(self, ajudou, inicio):
        try:
            salvo = self.assistente.registrar(
                "pergunta", self.pergunta_atual, self.resultado_atual,
                self.status_atual == "encontrado", ajudou,
                max(1, self.tentativas_busca), time.time() - inicio,
            )
        except ValueError as erro:
            messagebox.showerror("Não foi possível registrar", str(erro), parent=self.root)
            return
        if salvo:
            messagebox.showinfo("Atendimento registrado", "Obrigado pelo retorno. Sua avaliação foi salva sem dados pessoais.", parent=self.root)
        else:
            messagebox.showwarning("Atendimento desta sessão", "O atendimento foi contabilizado nesta sessão, mas não foi possível confirmar a gravação em disco.", parent=self.root)
        self.mostrar_historico()

    # ------------------------------------------------------------------
    # Histórico de perguntas
    # ------------------------------------------------------------------
    def _linha_pergunta(self, pai, registro, compacto=False):
        linha = tk.Frame(pai, bg=self.CARTAO, highlightthickness=1, highlightbackground=self.BORDA, padx=11, pady=9)
        linha.pack(fill="x", pady=4)
        pergunta = registro.get("pergunta", "Pergunta sem texto")
        tk.Label(linha, text=pergunta, font=(self.FONTE, 9, "bold"), fg=self.TEXTO, bg=self.CARTAO, wraplength=850 if not compacto else 620, justify="left").pack(anchor="w")
        if compacto:
            subtexto = f"{self._data_legivel(registro.get('data'))}  ·  {'Ajudou' if registro.get('ajudou') == 'sim' else 'Não ajudou'}"
        else:
            titulo = self._titulo_orientacao(registro.get("id_orientacao"))
            subtexto = f"{titulo}  ·  {self._data_legivel(registro.get('data'))}"
        tk.Label(linha, text=subtexto, font=(self.FONTE, 7), fg=self.TEXTO_MUTED, bg=self.CARTAO, wraplength=850 if not compacto else 620, justify="left").pack(anchor="w", pady=(4, 0))
        if not compacto:
            tags = tk.Frame(linha, bg=self.CARTAO)
            tags.pack(fill="x", pady=(8, 0))
            encontrado = registro.get("encontrou") == "sim"
            ajudou = registro.get("ajudou") == "sim"
            self._tag(tags, "RESPOSTA ENCONTRADA" if encontrado else "SEM RESPOSTA", self.DESTAQUE if encontrado else self.ALERTA).pack(side="left", padx=(0, 6))
            self._tag(tags, "AJUDOU" if ajudou else "NÃO AJUDOU", self.DESTAQUE if ajudou else self.ALERTA).pack(side="left")
            self._botao(tags, "DETALHES", lambda item=registro: self._detalhe_historico(item), self.CARTAO_2, self.TEXTO, compacto=True).pack(side="right")
        return linha

    def _tag(self, pai, texto, cor):
        return tk.Label(pai, text=texto, font=(self.FONTE, 7, "bold"), fg=cor, bg=self.CARTAO_2, padx=8, pady=4)

    def mostrar_historico(self):
        self._set_nav_ativa("Histórico de perguntas")
        self._limpar()
        self._cabecalho("Histórico de perguntas", "Consulte o que foi perguntado, veja os resultados e retome uma dúvida anterior.", "Seus atendimentos")

        controles = self._painel(self.conteudo, 13)
        controles.pack(fill="x", pady=(0, 13))
        self._label(controles, "PESQUISAR POR PERGUNTA OU ORIENTAÇÃO", 7, "bold", cor=self.TEXTO_MUTED, bg=self.CARTAO).pack(anchor="w", pady=(0, 7))
        linha_controles = tk.Frame(controles, bg=self.CARTAO)
        linha_controles.pack(fill="x")
        busca = tk.Entry(controles, textvariable=self.busca_historico_var, font=(self.FONTE, 10), bg=self.CARTAO_2, fg=self.TEXTO, insertbackground=self.TEXTO, relief="flat", bd=0, highlightthickness=1, highlightbackground=self.BORDA)
        busca.pack(in_=linha_controles, side="left", fill="x", expand=True, ipady=9, padx=(0, 10))
        busca.bind("<KeyRelease>", lambda _e: self._render_historico_lista())
        filtros = tk.Frame(linha_controles, bg=self.CARTAO)
        filtros.pack(side="right")
        for nome in ("Todas", "Encontradas", "Não resolvidas"):
            cor = self.DESTAQUE if self.filtro_historico == nome else self.CARTAO_2
            fg = self.SIDEBAR if self.filtro_historico == nome else self.TEXTO_SUAVE
            self._botao(filtros, nome.upper(), lambda f=nome: self._definir_filtro_historico(f), cor, fg, compacto=True).pack(side="left", padx=2)
        self._label(self.conteudo, f"{len(self.assistente.historico)} atendimento(s) registrado(s)", 8, cor=self.TEXTO_MUTED, bg=self.FUNDO).pack(anchor="w", pady=(0, 6))
        self.lista_historico = tk.Frame(self.conteudo, bg=self.FUNDO)
        self.lista_historico.pack(fill="both", expand=True)
        self._render_historico_lista()

    def _definir_filtro_historico(self, filtro):
        self.filtro_historico = filtro
        self.mostrar_historico()

    def _render_historico_lista(self):
        if not hasattr(self, "lista_historico") or not self.lista_historico.winfo_exists():
            return
        for widget in self.lista_historico.winfo_children():
            widget.destroy()
        termo = self.busca_historico_var.get().strip().casefold()
        registros = sorted(self.assistente.historico, key=lambda x: x.get("data", ""), reverse=True)
        if self.filtro_historico == "Encontradas":
            registros = [x for x in registros if x.get("encontrou") == "sim"]
        elif self.filtro_historico == "Não resolvidas":
            registros = [x for x in registros if x.get("ajudou") != "sim"]
        if termo:
            registros = [x for x in registros if termo in x.get("pergunta", "").casefold() or termo in self._titulo_orientacao(x.get("id_orientacao")).casefold()]
        if not registros:
            texto = "Nenhum atendimento corresponde ao filtro." if self.assistente.historico else "Seu histórico ainda está vazio. Faça uma pergunta para começar a registrar os atendimentos."
            self._label(self.lista_historico, texto, 9, cor=self.TEXTO_SUAVE, bg=self.FUNDO, wraplength=900, justify="left").pack(anchor="w", pady=16)
            return
        for registro in registros:
            self._linha_pergunta(self.lista_historico, registro)

    def _detalhe_historico(self, registro):
        janela = tk.Toplevel(self.root)
        janela.title("Detalhes do atendimento")
        janela.geometry("620x480")
        janela.configure(bg=self.FUNDO)
        janela.transient(self.root)
        janela.grab_set()
        corpo = tk.Frame(janela, bg=self.FUNDO, padx=24, pady=22)
        corpo.pack(fill="both", expand=True)
        tk.Label(corpo, text="DETALHES DO ATENDIMENTO", font=(self.FONTE, 8, "bold"), fg=self.DESTAQUE_CLARO, bg=self.FUNDO).pack(anchor="w")
        tk.Label(corpo, text=registro.get("pergunta", ""), font=(self.FONTE, 15, "bold"), fg=self.TEXTO, bg=self.FUNDO, wraplength=550, justify="left").pack(anchor="w", pady=(10, 17))
        linhas = [
            ("Data", self._data_legivel(registro.get("data"))),
            ("Orientação", self._titulo_orientacao(registro.get("id_orientacao"))),
            ("Busca", "Orientação encontrada" if registro.get("encontrou") == "sim" else "Nenhuma orientação suficiente"),
            ("Avaliação", "Ajudou" if registro.get("ajudou") == "sim" else "Não ajudou"),
            ("Tempo", f"{registro.get('tempo_segundos', '—')} segundo(s)"),
            ("Tentativas", str(registro.get("tentativas", "—"))),
        ]
        for rotulo, valor in linhas:
            bloco = tk.Frame(corpo, bg=self.CARTAO, padx=12, pady=9)
            bloco.pack(fill="x", pady=3)
            tk.Label(bloco, text=rotulo.upper(), font=(self.FONTE, 7, "bold"), fg=self.TEXTO_MUTED, bg=self.CARTAO).pack(anchor="w")
            tk.Label(bloco, text=valor, font=(self.FONTE, 9), fg=self.TEXTO, bg=self.CARTAO, wraplength=520, justify="left").pack(anchor="w", pady=(3, 0))
        botoes = tk.Frame(corpo, bg=self.FUNDO)
        botoes.pack(fill="x", pady=(14, 0))
        self._botao(botoes, "FAZER PERGUNTA NOVAMENTE", lambda: self._refazer_pergunta(registro, janela)).pack(side="left")
        self._botao(botoes, "FECHAR", janela.destroy, self.CARTAO_2, self.TEXTO).pack(side="right")

    def _refazer_pergunta(self, registro, janela=None):
        pergunta = registro.get("pergunta", "")
        if janela:
            janela.destroy()
        self.mostrar_busca()
        self.entrada.insert(0, pergunta)
        self.entrada.focus_set()

    # ------------------------------------------------------------------
    # Histórico de avaliações
    # ------------------------------------------------------------------
    def mostrar_avaliacoes(self):
        self._set_nav_ativa("Avaliações")
        self._limpar()
        self._cabecalho("Avaliações e feedback", "Veja como as respostas foram avaliadas e como as pessoas avaliaram a facilidade de uso.", "Melhoria contínua")
        historico = self.assistente.historico
        avaliacoes = self.assistente.avaliacoes
        votos_sim = sum(1 for item in historico if item.get("ajudou") == "sim")
        votos_nao = sum(1 for item in historico if item.get("ajudou") == "nao")
        notas = [int(item.get("facilidade", 0) or 0) for item in avaliacoes]
        media = sum(notas) / len(notas) if notas else 0
        cards = tk.Frame(self.conteudo, bg=self.FUNDO)
        cards.pack(fill="x", pady=(0, 16))
        metricas = [
            ("Ajudou", str(votos_sim), "Respostas avaliadas positivamente", self.DESTAQUE),
            ("Não ajudou", str(votos_nao), "Respostas que precisam de revisão", self.ALERTA),
            ("Facilidade média", f"{media:.1f}/5" if notas else "—", f"{len(notas)} avaliação(ões) de experiência", self.AZUL),
            ("Feedbacks", str(votos_sim + votos_nao + len(notas)), "Registros de avaliação", self.TEXTO),
        ]
        for i, item in enumerate(metricas):
            card = self._cartao_metrica(cards, *item)
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 9, 0))
            cards.grid_columnconfigure(i, weight=1, uniform="reviews")

        nota_info = self._painel(self.conteudo, 13, self.CARTAO_2)
        nota_info.pack(fill="x", pady=(0, 13))
        tk.Label(nota_info, text="DOIS TIPOS DE FEEDBACK", font=(self.FONTE, 8, "bold"), fg=self.DESTAQUE_CLARO, bg=self.CARTAO_2).pack(anchor="w")
        tk.Label(nota_info, text="•  Avaliação da resposta: indica se aquela orientação resolveu a dúvida.\n•  Facilidade de uso: nota de 1 a 5 registrada ao encerrar o programa.", font=(self.FONTE, 8), fg=self.TEXTO_SUAVE, bg=self.CARTAO_2, justify="left").pack(anchor="w", pady=(6, 0))

        tk.Label(self.conteudo, text="HISTÓRICO DE AVALIAÇÕES", font=(self.FONTE, 8, "bold"), fg=self.TEXTO_MUTED, bg=self.FUNDO).pack(anchor="w", pady=(5, 8))
        eventos = []
        for item in historico:
            eventos.append({
                "data": item.get("data", ""),
                "tipo": "Resposta avaliada",
                "texto": item.get("pergunta", "Pergunta sem texto"),
                "nota": "Ajudou" if item.get("ajudou") == "sim" else "Não ajudou",
                "cor": self.DESTAQUE if item.get("ajudou") == "sim" else self.ALERTA,
                "detalhe": "Orientação encontrada" if item.get("encontrou") == "sim" else "Sem orientação suficiente",
            })
        for item in avaliacoes:
            nota = int(item.get("facilidade", 0) or 0)
            eventos.append({
                "data": item.get("data", ""),
                "tipo": "Experiência avaliada",
                "texto": f"Avaliação de facilidade de uso: {nota}/5",
                "nota": f"{'★' * nota}{'☆' * (5 - nota)}",
                "cor": self.AZUL if nota >= 4 else self.ALERTA,
                "detalhe": "Nota registrada ao encerrar o assistente",
            })
        eventos.sort(key=lambda x: x.get("data", ""), reverse=True)
        if not eventos:
            self._painel_vazio(self.conteudo, "Nenhuma avaliação registrada ainda.", "As avaliações aparecerão aqui depois que as pessoas utilizarem o assistente.")
        else:
            for evento in eventos:
                card = self._painel(self.conteudo, 12)
                card.pack(fill="x", pady=4)
                topo = tk.Frame(card, bg=self.CARTAO)
                topo.pack(fill="x")
                tk.Label(topo, text=evento["tipo"].upper(), font=(self.FONTE, 7, "bold"), fg=self.TEXTO_MUTED, bg=self.CARTAO).pack(side="left")
                tk.Label(topo, text=self._data_legivel(evento["data"]), font=(self.FONTE, 7), fg=self.TEXTO_MUTED, bg=self.CARTAO).pack(side="right")
                tk.Label(card, text=evento["texto"], font=(self.FONTE, 9, "bold"), fg=self.TEXTO, bg=self.CARTAO, wraplength=920, justify="left").pack(anchor="w", pady=(7, 3))
                linha = tk.Frame(card, bg=self.CARTAO)
                linha.pack(fill="x")
                tk.Label(linha, text=evento["nota"], font=(self.FONTE, 8, "bold"), fg=evento["cor"], bg=self.CARTAO).pack(side="left")
                tk.Label(linha, text=evento["detalhe"], font=(self.FONTE, 7), fg=self.TEXTO_MUTED, bg=self.CARTAO).pack(side="left", padx=10)

    def _painel_vazio(self, pai, titulo, descricao):
        quadro = self._painel(pai, 20)
        quadro.pack(fill="x", pady=8)
        tk.Label(quadro, text=titulo, font=(self.FONTE, 10, "bold"), fg=self.TEXTO, bg=self.CARTAO).pack(anchor="w")
        tk.Label(quadro, text=descricao, font=(self.FONTE, 8), fg=self.TEXTO_SUAVE, bg=self.CARTAO, wraplength=900, justify="left").pack(anchor="w", pady=(5, 0))

    # ------------------------------------------------------------------
    # Categorias e orientação
    # ------------------------------------------------------------------
    def mostrar_categorias(self):
        self._set_nav_ativa("Explorar categorias")
        self._limpar()
        self._cabecalho("Explore por assunto", "Escolha uma área para consultar orientações e abrir diretamente as fontes oficiais.", "Base de conhecimento")
        descricoes = {
            "Currículo e entrevista": "Currículos, candidaturas e preparação para entrevistas.",
            "Direitos e proteção": "Canais de atendimento, proteção e denúncia.",
            "Direitos trabalhistas": "Salário, férias, demissão, jornada e benefícios.",
            "Jovem Aprendiz": "Requisitos, contrato, direitos e jornada.",
            "Primeiros passos": "Carteira de trabalho e entrada no mercado.",
            "Programas de inclusão": "Programas sociais, CadÚnico e inclusão produtiva.",
            "Vagas e qualificação": "Busca de vagas, SINE, cursos e formação.",
        }
        grade = tk.Frame(self.conteudo, bg=self.FUNDO)
        grade.pack(fill="x")
        for i, categoria in enumerate(self.assistente.base.categorias()):
            orientacoes = self.assistente.base.por_categoria(categoria)
            quadro = self._painel(grade, 17)
            quadro.grid(row=i // 2, column=i % 2, sticky="nsew", padx=(0 if i % 2 == 0 else 9, 0), pady=5)
            tk.Label(quadro, text="✦", font=(self.FONTE, 16, "bold"), fg=self.DESTAQUE, bg=self.CARTAO).pack(anchor="w")
            tk.Label(quadro, text=categoria, font=(self.FONTE, 11, "bold"), fg=self.TEXTO, bg=self.CARTAO).pack(anchor="w", pady=(5, 3))
            tk.Label(quadro, text=descricoes.get(categoria, "Informações e orientações oficiais."), font=(self.FONTE, 8), fg=self.TEXTO_SUAVE, bg=self.CARTAO, wraplength=420, justify="left").pack(anchor="w")
            tk.Label(quadro, text=f"{len(orientacoes)} orientações  ·  EXPLORAR →", font=(self.FONTE, 7, "bold"), fg=self.DESTAQUE_CLARO, bg=self.CARTAO).pack(anchor="w", pady=(12, 0))
            for filho in quadro.winfo_children():
                filho.configure(cursor="hand2")
                filho.bind("<Button-1>", lambda _e, cat=categoria: self.mostrar_categoria(cat))
            quadro.bind("<Button-1>", lambda _e, cat=categoria: self.mostrar_categoria(cat))
            grade.grid_columnconfigure(i % 2, weight=1, uniform="categorias")

    def mostrar_categoria(self, categoria):
        self._set_nav_ativa("Explorar categorias")
        self._limpar()
        self._cabecalho(categoria, "Selecione uma orientação para consultar o resumo e a fonte oficial.", "Categoria")
        for orientacao in self.assistente.base.por_categoria(categoria):
            linha = self._painel(self.conteudo, 14)
            linha.pack(fill="x", pady=4)
            tk.Label(linha, text=orientacao.titulo, font=(self.FONTE, 10, "bold"), fg=self.TEXTO, bg=self.CARTAO).pack(anchor="w")
            tk.Label(linha, text=(orientacao.resposta[:220] + "…") if len(orientacao.resposta) > 220 else orientacao.resposta, font=(self.FONTE, 8), fg=self.TEXTO_SUAVE, bg=self.CARTAO, wraplength=950, justify="left").pack(anchor="w", pady=(5, 7))
            tk.Label(linha, text=f"ABRIR ORIENTAÇÃO  ↗     ·     VERIFICADO EM {orientacao.verificado_em}", font=(self.FONTE, 7, "bold"), fg=self.DESTAQUE_CLARO, bg=self.CARTAO).pack(anchor="w")
            for filho in linha.winfo_children():
                filho.configure(cursor="hand2")
                filho.bind("<Button-1>", lambda _e, item=orientacao: self.mostrar_orientacao(item))
            linha.bind("<Button-1>", lambda _e, item=orientacao: self.mostrar_orientacao(item))

    def mostrar_orientacao(self, orientacao):
        self._set_nav_ativa("Explorar categorias")
        self._limpar()
        self.tempo_inicio_orientacao = time.time()
        self.orientacao_aberta = orientacao
        self._cabecalho(orientacao.titulo, orientacao.categoria, "Orientação oficial")
        caixa = self._painel(self.conteudo, 18)
        caixa.pack(fill="x", pady=(0, 13))
        tk.Label(caixa, text=orientacao.resposta, font=(self.FONTE, 10), fg=self.TEXTO, bg=self.CARTAO, wraplength=950, justify="left").pack(anchor="w")
        tk.Label(caixa, text="DOCUMENTOS OU INFORMAÇÕES ÚTEIS", font=(self.FONTE, 7, "bold"), fg=self.TEXTO_MUTED, bg=self.CARTAO).pack(anchor="w", pady=(14, 4))
        tk.Label(caixa, text="  •  " + "\n  •  ".join(orientacao.documentos), font=(self.FONTE, 8), fg=self.TEXTO_SUAVE, bg=self.CARTAO, justify="left").pack(anchor="w")
        tk.Label(caixa, text=f"ONDE: {orientacao.onde}", font=(self.FONTE, 8), fg=self.TEXTO, bg=self.CARTAO, wraplength=950, justify="left").pack(anchor="w", pady=(12, 7))
        tk.Label(caixa, text=f"Fonte conferida em: {orientacao.verificado_em}", font=(self.FONTE, 7), fg=self.TEXTO_MUTED, bg=self.CARTAO).pack(anchor="w")
        link = tk.Label(caixa, text="↗  ABRIR FONTE OFICIAL", font=(self.FONTE, 8, "bold", "underline"), fg=self.AZUL, bg=self.CARTAO, cursor="hand2")
        link.pack(anchor="w", pady=(11, 0))
        link.bind("<Button-1>", lambda _e: webbrowser.open(orientacao.fonte))

        avaliacao = self._painel(self.conteudo, 14)
        avaliacao.pack(fill="x")
        tk.Label(avaliacao, text="Essa orientação ajudou?", font=(self.FONTE, 9, "bold"), fg=self.TEXTO, bg=self.CARTAO).pack(side="left", padx=(0, 14))
        self._botao(avaliacao, "SIM, AJUDOU", lambda: self._registrar_orientacao_categoria(True)).pack(side="left", padx=4)
        self._botao(avaliacao, "NÃO", lambda: self._registrar_orientacao_categoria(False), self.CARTAO_2, self.TEXTO).pack(side="left", padx=4)

    def _registrar_orientacao_categoria(self, ajudou):
        orientacao = self.orientacao_aberta
        salvo = self.assistente.registrar(
            "categoria", orientacao.titulo, orientacao, True, ajudou, 1,
            time.time() - (self.tempo_inicio_orientacao or time.time()),
        )
        if salvo:
            messagebox.showinfo("Atendimento registrado", "Obrigado pelo retorno. Sua avaliação foi registrada sem dados pessoais.", parent=self.root)
        else:
            messagebox.showwarning("Atendimento desta sessão", "O atendimento foi contabilizado nesta sessão, mas não foi possível confirmar a gravação no histórico.", parent=self.root)
        self.mostrar_historico()

    # ------------------------------------------------------------------
    # Indicadores, exportação e fontes
    # ------------------------------------------------------------------
    def mostrar_indicadores(self):
        self._set_nav_ativa("Indicadores")
        self._limpar()
        self._cabecalho("Indicadores de atendimento", "Métricas calculadas exclusivamente a partir dos registros reais desta instalação.", "Acompanhamento")
        dados = self.assistente.indicadores()
        cards = tk.Frame(self.conteudo, bg=self.FUNDO)
        cards.pack(fill="x", pady=(0, 15))
        itens = [
            ("Atendimentos", str(dados["total"]), "Total registrado", self.AZUL),
            ("Encontradas", f"{dados['taxa_encontrada']:.1f}%" if dados["total"] else "—", "Respostas recuperadas", self.DESTAQUE),
            ("Resolvidas", f"{dados['taxa_resolucao']:.1f}%" if dados["total"] else "—", "Retorno positivo", self.DESTAQUE_CLARO),
            ("Tempo médio", f"{dados['tempo_medio']:.1f}s" if dados["total"] else "—", "Por atendimento", self.ALERTA),
        ]
        for i, item in enumerate(itens):
            card = self._cartao_metrica(cards, *item)
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 9, 0))
            cards.grid_columnconfigure(i, weight=1, uniform="indicators")

        colunas = tk.Frame(self.conteudo, bg=self.FUNDO)
        colunas.pack(fill="x")
        esquerda = self._painel(colunas, 16)
        esquerda.pack(side="left", fill="both", expand=True, padx=(0, 9))
        direita = self._painel(colunas, 16)
        direita.pack(side="left", fill="both", expand=True)
        tk.Label(esquerda, text="QUALIDADE DO ATENDIMENTO", font=(self.FONTE, 8, "bold"), fg=self.TEXTO_MUTED, bg=self.CARTAO).pack(anchor="w")
        tk.Label(esquerda, text=f"{dados['tentativas_medias']:.1f} tentativas por atendimento", font=(self.FONTE, 9), fg=self.TEXTO, bg=self.CARTAO).pack(anchor="w", pady=(11, 5))
        facilidade = f"{dados['facilidade_media']:.1f}/5  ·  {dados['total_avaliacoes']} avaliação(ões)" if dados["total_avaliacoes"] else "Ainda sem avaliações"
        tk.Label(esquerda, text=f"Facilidade de uso: {facilidade}", font=(self.FONTE, 9), fg=self.TEXTO_SUAVE, bg=self.CARTAO).pack(anchor="w", pady=4)
        tk.Label(esquerda, text="ORIENTAÇÕES MAIS CONSULTADAS", font=(self.FONTE, 7, "bold"), fg=self.TEXTO_MUTED, bg=self.CARTAO).pack(anchor="w", pady=(16, 7))
        populares = dados["orientacoes_mais_consultadas"][:6]
        if populares:
            for item in populares:
                tk.Label(esquerda, text=f"•  {item['titulo']}  ·  {item['consultas']} consulta(s)", font=(self.FONTE, 8), fg=self.TEXTO_SUAVE, bg=self.CARTAO, wraplength=410, justify="left").pack(anchor="w", pady=3)
        else:
            tk.Label(esquerda, text="Ainda não há consultas registradas.", font=(self.FONTE, 8), fg=self.TEXTO_MUTED, bg=self.CARTAO).pack(anchor="w")

        tk.Label(direita, text="DÚVIDAS QUE NÃO AJUDARAM", font=(self.FONTE, 8, "bold"), fg=self.TEXTO_MUTED, bg=self.CARTAO).pack(anchor="w")
        pendentes = dados["duvidas_sem_solucao"][-8:]
        if pendentes:
            for registro in reversed(pendentes):
                tk.Label(direita, text=f"•  {registro['pergunta']}", font=(self.FONTE, 8), fg=self.TEXTO_SUAVE, bg=self.CARTAO, wraplength=410, justify="left").pack(anchor="w", pady=5)
        else:
            tk.Label(direita, text="Nenhuma dúvida pendente registrada.", font=(self.FONTE, 8), fg=self.TEXTO_MUTED, bg=self.CARTAO).pack(anchor="w", pady=(12, 0))
        self._botao(self.conteudo, "EXPORTAR ATENDIMENTOS CSV", self.exportar).pack(anchor="w", pady=(15, 0))

    def exportar(self):
        try:
            caminho = self.assistente.exportar_csv()
        except OSError as erro:
            messagebox.showerror("Falha na exportação", f"Não foi possível exportar o arquivo:\n{erro}", parent=self.root)
            return
        messagebox.showinfo("Exportação concluída", f"Arquivo atualizado em:\n{caminho}", parent=self.root)

    def mostrar_fontes(self):
        self._set_nav_ativa("Fontes e transparência")
        self._limpar()
        self._cabecalho("Fontes e transparência", "Consulte a procedência de cada orientação e entenda os limites do assistente.", "Confiabilidade")
        aviso = self._painel(self.conteudo, 15, self.CARTAO_2)
        aviso.pack(fill="x", pady=(0, 15))
        tk.Label(aviso, text="INFORMAÇÃO IMPORTANTE", font=(self.FONTE, 8, "bold"), fg=self.ALERTA, bg=self.CARTAO_2).pack(anchor="w")
        tk.Label(aviso, text="O Trilha Cidadã organiza informações públicas e não é um canal oficial nem substitui orientação jurídica. A IA usa o catálogo local; ela não atualiza automaticamente a legislação. Não envie dados pessoais.", font=(self.FONTE, 8), fg=self.TEXTO_SUAVE, bg=self.CARTAO_2, wraplength=950, justify="left").pack(anchor="w", pady=(6, 0))
        tk.Label(self.conteudo, text=f"{len(self.assistente.base.orientacoes)} ORIENTAÇÕES CADASTRADAS", font=(self.FONTE, 8, "bold"), fg=self.TEXTO_MUTED, bg=self.FUNDO).pack(anchor="w", pady=(0, 7))
        for orientacao in self.assistente.base.orientacoes:
            linha = self._painel(self.conteudo, 12)
            linha.pack(fill="x", pady=3)
            tk.Label(linha, text=orientacao.titulo, font=(self.FONTE, 9, "bold"), fg=self.TEXTO, bg=self.CARTAO).pack(anchor="w")
            tk.Label(linha, text=f"{orientacao.categoria}  ·  conferido em {orientacao.verificado_em}", font=(self.FONTE, 7), fg=self.TEXTO_MUTED, bg=self.CARTAO).pack(anchor="w", pady=(3, 5))
            link = tk.Label(linha, text="↗  ABRIR FONTE OFICIAL", font=(self.FONTE, 7, "bold", "underline"), fg=self.AZUL, bg=self.CARTAO, cursor="hand2")
            link.pack(anchor="w")
            link.bind("<Button-1>", lambda _e, url=orientacao.fonte: webbrowser.open(url))

    def executar(self):
        self.root.mainloop()
