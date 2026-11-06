"""Atendimento, proteção de dados, histórico, indicadores e exportação."""

from collections import Counter
from dataclasses import replace
from datetime import datetime
from pathlib import Path
import math
import re
import time

from expansor_ia import ExpansorConsultaIA
from orientacao import Orientacao


CAMPOS_HISTORICO = [
    "data",
    "origem",
    "pergunta",
    "id_orientacao",
    "encontrou",
    "ajudou",
    "tentativas",
    "tempo_segundos",
]
CAMPOS_AVALIACOES = ["data", "facilidade"]


class Assistente:
    """Coordena a interação entre usuário, base de conhecimento e arquivos."""

    def __init__(self, nome: str, base, diretorio_dados: str | Path = "data"):
        self.nome = nome
        self.base = base
        self.expansor_ia = ExpansorConsultaIA.do_projeto(Path(__file__).resolve().parent)
        self.ultima_busca_ia = False
        self.ultima_resposta_ia = False
        self.ultima_analise_ia = None
        self.ultimo_erro_ia = ""
        self.diretorio_dados = Path(diretorio_dados)
        self.diretorio_dados.mkdir(parents=True, exist_ok=True)

        self.caminho_historico = self.diretorio_dados / "historico.csv"
        self.caminho_avaliacoes = self.diretorio_dados / "avaliacoes.csv"
        self.caminho_exportacao = self.diretorio_dados / "atendimentos.csv"
        self.avisos_armazenamento: list[str] = []

        self.historico, self._persistencia_historico = self._carregar_registros(
            self.caminho_historico, CAMPOS_HISTORICO, "histórico"
        )
        self.avaliacoes, self._persistencia_avaliacoes = self._carregar_registros(
            self.caminho_avaliacoes, CAMPOS_AVALIACOES, "avaliações"
        )

    @staticmethod
    def contem_dados_pessoais(texto: str) -> bool:
        """Aplica a regra do trabalho: oito dígitos ou presença de @."""
        texto = str(texto or "")
        quantidade_digitos = len(re.findall(r"\d", texto))
        return quantidade_digitos >= 8 or "@" in texto

    @staticmethod
    def _limpar_campo(valor) -> str:
        """Garante que um campo não quebre o formato simples separado por ;."""
        texto = str(valor if valor is not None else "")
        return (
            texto.replace(";", ",")
            .replace("\n", " ")
            .replace("\r", " ")
            .strip()
        )

    def _carregar_registros(
        self, caminho: Path, campos: list[str], nome: str
    ) -> tuple[list[dict], bool]:
        """Carrega linhas válidas e preserva a aplicação diante de CSV danificado.

        O segundo valor informa se o arquivo permite novas gravações. Um cabeçalho
        desconhecido nunca é sobrescrito automaticamente, evitando perda de dados.
        """
        registros = []
        cabecalho_esperado = ";".join(campos)

        if not caminho.exists() or caminho.stat().st_size == 0:
            try:
                with caminho.open("w", encoding="utf-8") as arquivo:
                    arquivo.write(cabecalho_esperado + "\n")
                return registros, True
            except OSError as erro:
                self.avisos_armazenamento.append(
                    f"Não foi possível preparar o arquivo de {nome}: {erro}"
                )
                return registros, False

        try:
            with caminho.open("r", encoding="utf-8-sig") as arquivo:
                cabecalho = arquivo.readline().rstrip("\r\n")
                if cabecalho != cabecalho_esperado:
                    self.avisos_armazenamento.append(
                        f"O cabeçalho do arquivo de {nome} é inválido. "
                        "O arquivo foi preservado e novas gravações nele foram desativadas."
                    )
                    return registros, False

                for numero_linha, linha in enumerate(arquivo, start=2):
                    partes = linha.rstrip("\r\n").split(";")
                    if len(partes) != len(campos):
                        self.avisos_armazenamento.append(
                            f"Arquivo de {nome}, linha {numero_linha}: registro ignorado por formato inválido."
                        )
                        continue

                    registro = dict(zip(campos, partes))
                    if not self._registro_valido(registro, campos):
                        self.avisos_armazenamento.append(
                            f"Arquivo de {nome}, linha {numero_linha}: registro ignorado por conter valores inválidos."
                        )
                        continue
                    registros.append(registro)

        except OSError as erro:
            self.avisos_armazenamento.append(
                f"Não foi possível ler o arquivo de {nome}: {erro}"
            )
            return registros, False

        return registros, True

    @staticmethod
    def _registro_valido(registro: dict, campos: list[str]) -> bool:
        """Verifica os campos essenciais dos arquivos de histórico e avaliação."""
        try:
            datetime.fromisoformat(registro["data"])
            if campos == CAMPOS_AVALIACOES:
                nota = int(registro["facilidade"])
                return 1 <= nota <= 5

            if registro["origem"] not in ("pergunta", "categoria"):
                return False
            if registro["encontrou"] not in ("sim", "nao"):
                return False
            if registro["ajudou"] not in ("sim", "nao"):
                return False
            if not registro["pergunta"].strip():
                return False
            if Assistente.contem_dados_pessoais(registro["pergunta"]):
                return False
            tentativas = int(registro["tentativas"])
            tempo = float(registro["tempo_segundos"])
            return tentativas >= 1 and math.isfinite(tempo) and tempo >= 0
        except (KeyError, TypeError, ValueError):
            return False

    def _criar_orientacao_assistida(self, analise: dict, resultados_locais):
        """Cria uma apresentação com resposta IA e fontes que existem no CSV."""
        por_id = {item.id: item for item in self.base.orientacoes}
        ids_relevantes = [
            identificador for identificador in analise.get("ids_relevantes", [])
            if identificador in por_id
        ]
        ids_fontes = [
            identificador for identificador in analise.get("ids_fontes", [])
            if identificador in por_id
        ]
        if not ids_fontes:
            ids_fontes = ids_relevantes[:3]

        fontes_base = [por_id[item] for item in ids_fontes]
        if not fontes_base and ids_relevantes:
            fontes_base = [por_id[item] for item in ids_relevantes[:3]]
        if not fontes_base and resultados_locais and resultados_locais[0][0] >= 3:
            fontes_base = [resultados_locais[0][1]]
            ids_relevantes = [fontes_base[0].id]

        resposta = str(analise.get("resposta", "")).strip()
        if not resposta and fontes_base:
            resposta = "\n\n".join(
                f"{item.titulo}: {item.resposta}" for item in fontes_base
            )
        if not resposta:
            return None

        principal = fontes_base[0] if fontes_base else None
        ids_origem = [item.id for item in fontes_base] or ids_relevantes[:1]
        documentos = []
        for item in fontes_base:
            for documento in item.documentos:
                if documento not in documentos:
                    documentos.append(documento)
        fontes_adicionais = [
            {
                "titulo": item.titulo,
                "url": item.fonte,
                "verificado_em": item.verificado_em,
            }
            for item in fontes_base[1:]
        ]

        if principal:
            base_da_resposta = replace(
                principal,
                titulo=analise.get("titulo") or f"Orientação sobre {principal.titulo.casefold()}",
                resposta=resposta,
                documentos=documentos or principal.documentos,
                onde="; ".join(dict.fromkeys(item.onde for item in fontes_base if item.onde)),
                fonte=principal.fonte,
                verificado_em=(
                    principal.verificado_em if len(fontes_base) == 1
                    else "\n".join(
                        f"{item.titulo}: {item.verificado_em}" for item in fontes_base
                    )
                ),
                gerada_por_ia=True,
                ids_origem=ids_origem,
                fontes_adicionais=fontes_adicionais,
                aviso_ia=(
                    "A IA interpretou sua pergunta e organizou informações dos registros "
                    "oficiais selecionados. Confira as fontes, especialmente antes de tomar "
                    "uma decisão trabalhista."
                ),
            )
            return base_da_resposta

        # A IA pode orientar sobre empregabilidade geral sem uma FAQ específica,
        # mas a aplicação não apresenta essa resposta como direito verificado.
        return Orientacao(
            id="",
            categoria="Orientação geral de empregabilidade",
            titulo=analise.get("titulo") or "Orientação sobre sua dúvida profissional",
            palavras_chave=[],
            resposta=resposta,
            documentos=["Confirme informações legais e administrativas nos canais oficiais."],
            onde="Portal oficial do Ministério do Trabalho e Emprego; atendimento Alô Trabalho 158.",
            fonte="https://www.gov.br/trabalho-e-emprego/pt-br",
            verificado_em="Resposta geral gerada por IA; não corresponde a uma FAQ específica verificada",
            gerada_por_ia=True,
            ids_origem=[],
            fontes_adicionais=[],
            aviso_ia=(
                "Esta orientação geral não está vinculada a um registro específico da base. "
                "Ela não confirma valores, prazos ou direitos legais; consulte o MTE para esses detalhes."
            ),
        )

    def buscar_pergunta(self, pergunta: str):
        """Usa IA para interpretar cada consulta e a pontuação como recuperação/fallback."""
        pergunta = str(pergunta or "").strip()
        if not pergunta:
            return [], "pergunta_vazia"
        if self.contem_dados_pessoais(pergunta):
            return None, "dados_pessoais"
        if not self.base.orientacoes:
            return [], "base_vazia"

        self.ultima_busca_ia = False
        self.ultima_resposta_ia = False
        self.ultima_analise_ia = None
        self.ultimo_erro_ia = ""
        resultados_locais = self.base.buscar(pergunta)

        if self.expansor_ia is None:
            self.ultimo_erro_ia = (
                "IA não configurada. Copie .env.example para .env e configure "
                "OLLAMA_BASE_URL e OLLAMA_API_KEY."
            )

        # NOVO FLUXO: a IA interpreta TODA pergunta, não apenas consultas sem pontos.
        if self.expansor_ia is not None and hasattr(self.expansor_ia, "analisar"):
            analise = self.expansor_ia.analisar(pergunta, self.base.orientacoes)
            if analise:
                self.ultima_busca_ia = True
                self.ultima_analise_ia = analise
                escopo = analise.get("escopo", "ambiguo")
                if escopo == "fora":
                    # A IA pode cometer falso negativo de escopo. Se a pergunta
                    # coincide fortemente com uma orientação local, prevalece o
                    # sinal verificável da base para não rejeitar um tema do projeto.
                    if resultados_locais and resultados_locais[0][0] >= 3:
                        return resultados_locais, "encontrado"
                    return [], "fora_escopo"

                if escopo in ("dentro", "ambiguo"):
                    orientacao_ia = self._criar_orientacao_assistida(analise, resultados_locais)
                    if orientacao_ia:
                        self.ultima_resposta_ia = True
                        pontos = 0
                        if orientacao_ia.id:
                            item_base = next(
                                item for item in self.base.orientacoes if item.id == orientacao_ia.id
                            )
                            pontos = self.base.pontuar(pergunta, item_base)
                        saida = [(pontos, orientacao_ia)]
                        ids = set(orientacao_ia.ids_origem)
                        for pontuacao, item in resultados_locais:
                            if item.id not in ids and item.id != orientacao_ia.id and pontuacao >= 3:
                                saida.append((pontuacao, item))
                            if len(saida) >= 4:
                                break
                        return saida, "encontrado"

                # Se a IA não conseguiu redigir, ainda usamos a busca local válida.
            else:
                self.ultimo_erro_ia = getattr(self.expansor_ia, "ultimo_erro", "")

        # Compatibilidade com o expansor antigo (ou IA temporariamente indisponível).
        elif self.expansor_ia is not None and hasattr(self.expansor_ia, "expandir"):
            if not resultados_locais or resultados_locais[0][0] < 3:
                titulos = [orientacao.titulo for orientacao in self.base.orientacoes]
                variantes = self.expansor_ia.expandir(pergunta, titulos)
                if variantes:
                    resultados_ampliados = self.base.buscar_com_variantes([pergunta, *variantes])
                    if resultados_ampliados and resultados_ampliados[0][0] >= 3:
                        resultados_locais = resultados_ampliados
                        self.ultima_busca_ia = True

        if resultados_locais and resultados_locais[0][0] >= 3:
            return resultados_locais, "encontrado"
        if self.ultimo_erro_ia:
            return resultados_locais, "ia_indisponivel"
        return resultados_locais, "nao_encontrado"

    def explicar_busca(self, pergunta: str, orientacao):
        """Explica a participação da IA ou a pontuação do mecanismo local."""
        if getattr(orientacao, "gerada_por_ia", False):
            fontes = getattr(orientacao, "ids_origem", [])
            return {
                "palavras_chave": [],
                "palavras_titulo": [],
                "termos_corrigidos": [],
                "pontos_chaves": 0,
                "pontos_titulo": 0,
                "total": 0,
                "confianca": "RESPOSTA ASSISTIDA POR IA",
                "consulta_utilizada": pergunta,
                "busca_ampliada_ia": True,
                "ids_fontes": fontes,
            }
        consulta = self.base.consulta_usada(orientacao) or pergunta
        detalhes = self.base.explicar_pontuacao(consulta, orientacao)
        detalhes["consulta_utilizada"] = consulta
        detalhes["busca_ampliada_ia"] = self.ultima_busca_ia
        return detalhes

    def _gravar_registro(
        self,
        caminho: Path,
        registro: dict,
        campos: list[str],
        persistencia_ativa: bool,
        nome: str,
    ) -> bool:
        """Acrescenta um registro e informa se ele foi salvo em disco."""
        if not persistencia_ativa:
            return False
        try:
            with caminho.open("a", encoding="utf-8") as arquivo:
                arquivo.write(
                    ";".join(self._limpar_campo(registro.get(campo, "")) for campo in campos)
                    + "\n"
                )
            return True
        except OSError as erro:
            self.avisos_armazenamento.append(
                f"Não foi possível salvar o registro de {nome}: {erro}"
            )
            return False

    def registrar(
        self,
        origem: str,
        pergunta: str,
        orientacao,
        encontrou: bool,
        ajudou: bool,
        tentativas: int,
        tempo_segundos: float,
    ) -> bool:
        """Registra atendimento; retorna True quando a gravação em disco funciona."""
        pergunta = str(pergunta or "").strip()
        if self.contem_dados_pessoais(pergunta):
            raise ValueError("A pergunta contém dado pessoal e não pode ser registrada.")
        if not pergunta:
            raise ValueError("A pergunta ou o título da orientação não pode ficar vazio.")
        if origem not in ("pergunta", "categoria"):
            raise ValueError("A origem deve ser 'pergunta' ou 'categoria'.")

        try:
            tentativas = max(1, int(tentativas))
            tempo = float(tempo_segundos)
        except (TypeError, ValueError) as erro:
            raise ValueError("Tentativas e tempo devem ser valores numéricos válidos.") from erro

        if not math.isfinite(tempo):
            raise ValueError("O tempo do atendimento deve ser um número válido.")

        registro = {
            "data": datetime.now().astimezone().isoformat(timespec="seconds"),
            "origem": origem,
            "pergunta": self._limpar_campo(pergunta),
            "id_orientacao": orientacao.id if orientacao else "",
            "encontrou": "sim" if encontrou else "nao",
            "ajudou": "sim" if ajudou else "nao",
            "tentativas": str(tentativas),
            "tempo_segundos": str(round(max(0.0, tempo), 1)),
        }
        self.historico.append(registro)
        return self._gravar_registro(
            self.caminho_historico,
            registro,
            CAMPOS_HISTORICO,
            self._persistencia_historico,
            "histórico",
        )

    def registrar_facilidade(self, nota: int) -> bool:
        """Guarda uma avaliação de facilidade entre 1 e 5."""
        try:
            nota = int(nota)
        except (TypeError, ValueError) as erro:
            raise ValueError("A nota deve ser um número inteiro de 1 a 5.") from erro
        if not 1 <= nota <= 5:
            raise ValueError("A nota deve estar entre 1 e 5.")

        registro = {
            "data": datetime.now().astimezone().isoformat(timespec="seconds"),
            "facilidade": str(nota),
        }
        self.avaliacoes.append(registro)
        return self._gravar_registro(
            self.caminho_avaliacoes,
            registro,
            CAMPOS_AVALIACOES,
            self._persistencia_avaliacoes,
            "avaliações",
        )

    def indicadores(self) -> dict:
        """Calcula indicadores do histórico real desta instalação."""
        total = len(self.historico)
        encontrados = sum(
            1 for item in self.historico if item.get("encontrou") == "sim"
        )
        resolvidos = sum(
            1 for item in self.historico if item.get("ajudou") == "sim"
        )
        tempos = [float(item.get("tempo_segundos", 0) or 0) for item in self.historico]
        tentativas = [int(item.get("tentativas", 1) or 1) for item in self.historico]
        notas = [int(item.get("facilidade", 0) or 0) for item in self.avaliacoes]

        titulos_por_id = {
            orientacao.id: orientacao.titulo
            for orientacao in self.base.orientacoes
        }
        contagem_orientacoes = Counter(
            item.get("id_orientacao", "")
            for item in self.historico
            if item.get("id_orientacao")
        )
        orientacoes_mais_consultadas = [
            {
                "id": identificador,
                "titulo": titulos_por_id.get(identificador, "Orientação não disponível"),
                "consultas": quantidade,
            }
            for identificador, quantidade in sorted(
                contagem_orientacoes.items(),
                key=lambda item: (-item[1], titulos_por_id.get(item[0], "").casefold()),
            )
        ]

        return {
            "total": total,
            "taxa_encontrada": round((encontrados / total) * 100, 1) if total else 0.0,
            "taxa_resolucao": round((resolvidos / total) * 100, 1) if total else 0.0,
            "taxa_nao_encontrada": round(((total - encontrados) / total) * 100, 1) if total else 0.0,
            "tempo_medio": round(sum(tempos) / len(tempos), 1) if tempos else 0.0,
            "tentativas_medias": round(sum(tentativas) / len(tentativas), 1) if tentativas else 0.0,
            "facilidade_media": round(sum(notas) / len(notas), 1) if notas else 0.0,
            "total_avaliacoes": len(notas),
            "duvidas_sem_solucao": [
                item for item in self.historico if item.get("ajudou") == "nao"
            ],
            "encontrados": encontrados,
            "resolvidos": resolvidos,
            "orientacoes_mais_consultadas": orientacoes_mais_consultadas,
        }

    def exportar_csv(self) -> Path:
        """Exporta os atendimentos em CSV separado por ponto e vírgula."""
        with self.caminho_exportacao.open("w", encoding="utf-8") as arquivo:
            arquivo.write(";".join(CAMPOS_HISTORICO) + "\n")
            for registro in self.historico:
                arquivo.write(
                    ";".join(
                        self._limpar_campo(registro.get(campo, ""))
                        for campo in CAMPOS_HISTORICO
                    )
                    + "\n"
                )
        return self.caminho_exportacao

    @staticmethod
    def _perguntar_sim_nao(mensagem: str) -> bool:
        while True:
            resposta = input(mensagem).strip().casefold()
            if resposta in ("s", "sim"):
                return True
            if resposta in ("n", "não", "nao"):
                return False
            print("Entrada inválida. Digite s para sim ou n para não.")

    def perguntar(self):
        """Executa um atendimento por pergunta no terminal."""
        inicio = time.time()
        pergunta = input("\nDigite sua dúvida (0 para voltar): ").strip()
        if pergunta == "0":
            return
        if not pergunta:
            print("Digite uma pergunta antes de continuar.")
            return
        if self.contem_dados_pessoais(pergunta):
            print(
                "\nAtenção: não digite CPF, telefone, e-mail ou outros dados pessoais.\n"
                "Sua pergunta não foi registrada. Reescreva sem essas informações."
            )
            return

        if self.expansor_ia is not None:
            print("\nIA Cloud analisando sua pergunta e consultando as orientações verificadas...")
        else:
            print("\nIA Cloud não configurada. Consultando a base local...")

        resultados, status = self.buscar_pergunta(pergunta)
        if status == "base_vazia":
            print("A base de conhecimento está vazia. Confira o arquivo CSV.")
            return

        orientacao = None
        encontrou = status == "encontrado"
        if encontrou:
            pontos, orientacao = resultados[0]
            explicacao = self.explicar_busca(pergunta, orientacao)
            print(
                f"\nCompatibilidade da busca: {explicacao['confianca']} "
                f"({pontos} pontos)"
            )
            if explicacao["busca_ampliada_ia"]:
                print("Interpretação assistida por IA: o modelo analisou a pergunta e organizou a orientação com base nos registros selecionados.")
            elif self.ultimo_erro_ia:
                print(f"Aviso: a IA não participou desta resposta. Motivo: {self.ultimo_erro_ia}")
            else:
                print("Orientação recuperada pela busca pontuada da base verificada.")
            print("\n" + orientacao.exibir())
            alternativas = [item for item in resultados[1:3] if item[0] >= 3]
            if alternativas:
                print("\nOutras orientações que podem ajudar:")
                for pontos_alt, alternativa in alternativas:
                    print(f"  • {alternativa.titulo} ({pontos_alt} pontos)")
            ajudou = self._perguntar_sim_nao(
                "\nEssa orientação resolveu sua dúvida? (s/n): "
            )
        else:
            if status == "fora_escopo":
                print("\nEsse assunto foi identificado como fora do escopo do Trilha Cidadã.")
                print("O assistente é focado em emprego, empregabilidade, Jovem Aprendiz e direitos do trabalhador.")
            elif status == "ia_indisponivel":
                print("\nA IA está indisponível e a busca local não encontrou uma orientação segura.")
                if self.ultimo_erro_ia:
                    print(f"Diagnóstico: {self.ultimo_erro_ia}")
            else:
                print("\nNão encontrei uma orientação com pontuação suficiente.")
            sugestoes = [item for item in resultados[:2] if item[0] > 0]
            if sugestoes:
                print("Assuntos próximos (ainda sem confiança suficiente):")
                for pontos_sugestao, sugestao in sugestoes:
                    print(f"  • {sugestao.titulo} ({pontos_sugestao} ponto(s))")
            print("Tente outras palavras ou navegue pelas categorias disponíveis:")
            for categoria in self.base.categorias():
                print(f"  • {categoria}")
            ajudou = self._perguntar_sim_nao(
                "\nConseguiu resolver sua dúvida por outro caminho? (s/n): "
            )

        tempo = round(time.time() - inicio, 1)
        salvo = self.registrar("pergunta", pergunta, orientacao, encontrou, ajudou, 1, tempo)
        if salvo:
            print(f"\nAtendimento registrado. Tempo: {tempo:.1f} segundos.")
        else:
            print(
                "\nAtendimento contabilizado nesta sessão, mas não foi possível "
                "confirmar a gravação em disco."
            )

    def navegar(self):
        """Permite consultar orientações organizadas por categoria."""
        while True:
            categorias = self.base.categorias()
            print("\n--- CATEGORIAS ---")
            for indice, categoria in enumerate(categorias, start=1):
                print(f"{indice}. {categoria}")
            print("0. Voltar ao menu principal")
            escolha = input("Escolha uma categoria: ").strip()
            if escolha == "0":
                return
            if not escolha.isdigit() or not (1 <= int(escolha) <= len(categorias)):
                print("Opção inválida. Escolha um número da lista.")
                continue

            categoria = categorias[int(escolha) - 1]
            orientacoes = self.base.por_categoria(categoria)
            while True:
                print(f"\n--- {categoria.upper()} ---")
                for indice, orientacao in enumerate(orientacoes, start=1):
                    print(f"{indice}. {orientacao.titulo}")
                print("0. Voltar às categorias")
                escolha_orientacao = input("Escolha uma orientação: ").strip()
                if escolha_orientacao == "0":
                    break
                if (
                    not escolha_orientacao.isdigit()
                    or not (1 <= int(escolha_orientacao) <= len(orientacoes))
                ):
                    print("Opção inválida. Escolha um número da lista.")
                    continue

                inicio = time.time()
                orientacao = orientacoes[int(escolha_orientacao) - 1]
                print("\n" + orientacao.exibir())
                ajudou = self._perguntar_sim_nao(
                    "\nEssa orientação ajudou? (s/n): "
                )
                salvo = self.registrar(
                    "categoria",
                    orientacao.titulo,
                    orientacao,
                    True,
                    ajudou,
                    1,
                    time.time() - inicio,
                )
                if salvo:
                    print("Atendimento registrado.")
                else:
                    print("Atendimento contabilizado apenas nesta sessão.")

    def exibir_indicadores(self):
        """Mostra os indicadores calculados a partir do histórico."""
        dados = self.indicadores()
        print("\n--- INDICADORES DO TRILHA CIDADÃ ---")
        print(f"Atendimentos: {dados['total']}")
        print(f"Respostas encontradas: {dados['taxa_encontrada']:.1f}%")
        print(f"Taxa de resolução: {dados['taxa_resolucao']:.1f}%")
        print(f"Tempo médio: {dados['tempo_medio']:.1f} segundos")
        print(f"Tentativas por atendimento: {dados['tentativas_medias']:.1f}")
        facilidade = (
            f"{dados['facilidade_media']:.1f}/5"
            if dados["total_avaliacoes"]
            else "Ainda sem avaliações"
        )
        print(f"Facilidade de uso: {facilidade}")

        print("\nOrientações mais consultadas:")
        if dados["orientacoes_mais_consultadas"]:
            for item in dados["orientacoes_mais_consultadas"][:5]:
                print(f"  • {item['titulo']}: {item['consultas']} consulta(s)")
        else:
            print("  Ainda não há consultas por categoria registradas.")

        print("\nDúvidas sem solução:")
        if dados["duvidas_sem_solucao"]:
            for item in dados["duvidas_sem_solucao"][-10:]:
                print(f"  • {item['pergunta']}")
        else:
            print("  Nenhuma registrada.")

    def executar_terminal(self):
        """Inicia o menu interativo de terminal."""
        print("=" * 58)
        print("TRILHA CIDADÃ | Emprego, oportunidades e direitos do trabalhador")
        print("Informação pública para dar o próximo passo com segurança.")
        if self.expansor_ia is not None:
            print("IA Cloud: CONFIGURADA — perguntas serão interpretadas pelo modelo.")
        else:
            print("IA Cloud: NÃO CONFIGURADA — o sistema usará a busca local.")
        print("=" * 58)

        if self.avisos_armazenamento:
            print("\nAvisos sobre os arquivos de histórico:")
            for aviso in self.avisos_armazenamento:
                print(f"- {aviso}")

        while True:
            print("\n1. Fazer uma pergunta (conversar com a IA)")
            print("2. Explorar orientações por categoria")
            print("3. Ver indicadores dos atendimentos")
            print("4. Exportar atendimentos para CSV")
            print("0. Encerrar e avaliar a experiência")
            escolha = input("Escolha uma opção: ").strip()

            if escolha == "1":
                self.perguntar()
            elif escolha == "2":
                self.navegar()
            elif escolha == "3":
                self.exibir_indicadores()
            elif escolha == "4":
                try:
                    print(f"Arquivo exportado: {self.exportar_csv()}")
                except OSError as erro:
                    print(f"Não foi possível exportar os atendimentos: {erro}")
            elif escolha == "0":
                while True:
                    nota = input(
                        "Antes de sair, avalie a facilidade de uso (1 a 5): "
                    ).strip()
                    if nota.isdigit() and 1 <= int(nota) <= 5:
                        salvo = self.registrar_facilidade(int(nota))
                        if not salvo:
                            print("A avaliação foi considerada nesta sessão, mas não foi salva em disco.")
                        break
                    print("Nota inválida. Digite um número de 1 a 5.")
                try:
                    self.exportar_csv()
                except OSError as erro:
                    print(f"Não foi possível exportar os atendimentos: {erro}")
                print("Obrigado por utilizar o Trilha Cidadã. Até a próxima!")
                return
            else:
                print("Opção inválida. O programa continua aberto.")
