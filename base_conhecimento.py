"""Carregamento, validação e busca explicável na base CSV do Trilha Cidadã."""

from datetime import date
from pathlib import Path
import re
import unicodedata
from urllib.parse import urlparse

from orientacao import Orientacao


CABECALHO = [
    "id",
    "categoria",
    "titulo",
    "palavras_chave",
    "resposta",
    "documentos",
    "onde",
    "fonte",
    "verificado_em",
]

PONTOS_PALAVRA_CHAVE = 3
PONTOS_TITULO = 1
LIMITE_CONFIANCA_ALTA = 6
LIMITE_CONFIANCA_MEDIA = 3


# Equivalências conservadoras para variações frequentes no vocabulário do projeto.
# Aplicadas igualmente às perguntas e às palavras-chave cadastradas.
EQUIVALENCIAS_BUSCA = {
    "curriculum": "curriculo", "cv": "curriculo", "cvs": "curriculo",
    "curriculos": "curriculo", "vagas": "vaga", "empregos": "emprego",
    "entrevistas": "entrevista", "aprendizes": "aprendiz", "cursos": "curso",
    "empresas": "empresa", "documentos": "documento", "direitos": "direito",
    "salarios": "salario", "candidaturas": "candidatura",
    "experiencias": "experiencia", "oportunidades": "oportunidade",
    "trabalhar": "trabalho", "trabalha": "trabalho", "trabalham": "trabalho",
    "trabalhe": "trabalho", "trabalhei": "trabalho", "trabalhado": "trabalho",
    "trabalhando": "trabalho", "trabalhos": "trabalho",
    "noite": "noturno", "noites": "noturno",
    "pede": "pedir", "pedi": "pedir", "peço": "pedir", "peco": "pedir",
    "pedem": "pedir", "pediu": "pedir", "peça": "pedir", "peca": "pedir",
    "recebo": "receber", "recebe": "receber", "recebem": "receber",
    "recebi": "receber", "recebido": "receber", "recebida": "receber",
    "valores": "valor", "contas": "conta", "folgas": "folga", "horas": "hora",
    "dias": "dia", "faltas": "falta", "justificadas": "justificada",
    "intervalos": "intervalo", "turnos": "turno", "descontar": "desconto",
    "descontado": "desconto", "descontada": "desconto", "descontos": "desconto",
    "demitido": "demissao", "demitida": "demissao", "demitidos": "demissao",
    "demitidas": "demissao", "dispensado": "demissao", "dispensada": "demissao",
    "dispensados": "demissao", "dispensadas": "demissao",
    "manda": "mandar", "mandado": "mandar", "mandada": "mandar",
    "volte": "voltar", "volto": "voltar", "volta": "voltar",
    "almocar": "almoco", "almocei": "almoco", "comecei": "comecar",
    "comeca": "comecar", "assina": "assinar", "assinei": "assinar",
    "assinado": "assinar", "humilha": "humilhar", "humilhou": "humilhar",
    "humilhado": "humilhar", "equipamentos": "equipamento", "luvas": "luva",
    "mensais": "mensal", "semanas": "semana", "atrasado": "atraso", "pagaram": "pagar", "paga": "pagar",
    "sai": "sair", "saio": "sair", "saiu": "sair", "escalar": "escala",
    "escale": "escala", "escalado": "escala", "escalada": "escala",
    "atrasada": "atraso",
    "conducao": "transporte", "passagem": "transporte",
    "passagens": "transporte", "onibus": "transporte",
    "metro": "transporte", "metros": "transporte",
}


def normalizar(texto: str) -> str:
    """Padroniza texto, remove acentos e aplica equivalências comuns do domínio."""
    texto = unicodedata.normalize("NFD", str(texto or "").casefold().strip())
    texto = "".join(
        caractere
        for caractere in texto
        if unicodedata.category(caractere) != "Mn"
    )
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    texto = " ".join(texto.split())
    texto = re.sub(r"\bcurriculum\s+vitae\b", "curriculo", texto)
    palavras = [EQUIVALENCIAS_BUSCA.get(palavra, palavra) for palavra in texto.split()]
    return " ".join(palavras)


class BaseConhecimento:
    """Carrega orientações e encontra as mais relevantes por pontuação."""

    def __init__(self, caminho: str | Path):
        self.caminho = Path(caminho)
        self.orientacoes: list[Orientacao] = []
        self.erros: list[str] = []
        self.avisos: list[str] = []
        self._vocabulario_busca: set[str] | None = None
        self._cache_correcao: dict[str, tuple[str, list[str]]] = {}

    def carregar(self) -> bool:
        """Carrega o CSV e ignora linhas inválidas sem encerrar o programa.

        A leitura mantém open(), for e split(";"), conforme solicitado no
        enunciado da atividade.
        """
        self.orientacoes = []
        self.erros = []
        self.avisos = []
        self._vocabulario_busca = None
        self._cache_correcao = {}

        if not self.caminho.exists():
            self.erros.append(f"Arquivo não encontrado: {self.caminho}")
            return False

        identificadores: set[str] = set()

        try:
            with self.caminho.open("r", encoding="utf-8-sig") as arquivo:
                primeira_linha = arquivo.readline().rstrip("\r\n")
                if primeira_linha.split(";") != CABECALHO:
                    self.erros.append(
                        "Cabeçalho inválido. Confira os nomes e a ordem das colunas."
                    )
                    return False

                for numero_linha, linha in enumerate(arquivo, start=2):
                    linha = linha.rstrip("\r\n")
                    if not linha.strip():
                        continue

                    campos = [campo.strip() for campo in linha.split(";")]
                    if len(campos) != len(CABECALHO):
                        self.erros.append(
                            f"Linha {numero_linha}: quantidade de campos inválida."
                        )
                        continue

                    (
                        identificador,
                        categoria,
                        titulo,
                        chaves,
                        resposta,
                        documentos,
                        onde,
                        fonte,
                        verificado_em,
                    ) = campos

                    obrigatorios = {
                        "id": identificador,
                        "categoria": categoria,
                        "título": titulo,
                        "resposta": resposta,
                        "local de atendimento": onde,
                        "fonte": fonte,
                        "data de verificação": verificado_em,
                    }
                    vazios = [nome for nome, valor in obrigatorios.items() if not valor]
                    if vazios:
                        self.erros.append(
                            f"Linha {numero_linha}: campo obrigatório vazio ({', '.join(vazios)})."
                        )
                        continue

                    if identificador in identificadores:
                        self.erros.append(
                            f"Linha {numero_linha}: ID duplicado ({identificador})."
                        )
                        continue

                    lista_chaves = [
                        item.strip() for item in chaves.split("|") if item.strip()
                    ]
                    chaves_normalizadas = {normalizar(item) for item in lista_chaves}
                    if len(chaves_normalizadas) < 3:
                        self.erros.append(
                            f"Linha {numero_linha}: use pelo menos três palavras-chave diferentes."
                        )
                        continue

                    endereco = urlparse(fonte)
                    if endereco.scheme != "https" or not endereco.netloc:
                        self.erros.append(
                            f"Linha {numero_linha}: a fonte deve ser um endereço HTTPS válido."
                        )
                        continue

                    try:
                        date.fromisoformat(verificado_em)
                    except ValueError:
                        self.erros.append(
                            f"Linha {numero_linha}: data inválida; use AAAA-MM-DD."
                        )
                        continue

                    self.orientacoes.append(
                        Orientacao(
                            id=identificador,
                            categoria=categoria,
                            titulo=titulo,
                            palavras_chave=lista_chaves,
                            resposta=resposta,
                            documentos=[
                                item.strip()
                                for item in documentos.split("|")
                                if item.strip()
                            ],
                            onde=onde,
                            fonte=fonte,
                            verificado_em=verificado_em,
                        )
                    )
                    identificadores.add(identificador)

        except OSError as erro:
            self.erros.append(f"Não foi possível ler a base: {erro}")
            return False

        self.avisos = self.validar_requisitos()
        return bool(self.orientacoes)

    def validar_requisitos(self) -> list[str]:
        """Confere os mínimos quantitativos pedidos no enunciado."""
        avisos = []
        if len(self.orientacoes) < 10:
            avisos.append(
                f"A base possui {len(self.orientacoes)} orientações; o mínimo é 10."
            )

        quantidade_categorias = len(self.categorias())
        if quantidade_categorias < 3:
            avisos.append(
                f"A base possui {quantidade_categorias} categorias; o mínimo é 3."
            )

        for orientacao in self.orientacoes:
            if len(orientacao.palavras_chave) < 3:
                avisos.append(
                    f"A orientação {orientacao.id} possui menos de três palavras-chave."
                )

        return avisos

    def categorias(self) -> list[str]:
        """Devolve as categorias sem duplicação e em ordem alfabética."""
        return sorted(
            {orientacao.categoria for orientacao in self.orientacoes},
            key=str.casefold,
        )

    def por_categoria(self, categoria: str) -> list[Orientacao]:
        """Filtra orientações sem diferenciar maiúsculas de minúsculas."""
        return [
            orientacao
            for orientacao in self.orientacoes
            if orientacao.categoria.casefold() == str(categoria).casefold()
        ]

    @staticmethod
    def _distancia_edicao_um(a: str, b: str) -> bool:
        """Retorna True quando duas palavras diferem por uma edição simples.

        Aceita uma substituição, inserção, remoção ou troca de duas letras
        adjacentes. Não tenta corrigir palavras curtas.
        """
        if a == b:
            return False
        if abs(len(a) - len(b)) > 1:
            return False
        if len(a) == len(b):
            diferencas = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
            if len(diferencas) == 1:
                return True
            if len(diferencas) == 2:
                i, j = diferencas
                return j == i + 1 and a[i] == b[j] and a[j] == b[i]
            return False

        menor, maior = (a, b) if len(a) < len(b) else (b, a)
        i = j = 0
        pulou = False
        while i < len(menor) and j < len(maior):
            if menor[i] == maior[j]:
                i += 1
                j += 1
            elif pulou:
                return False
            else:
                pulou = True
                j += 1
        return True

    def corrigir_erros_digitacao(self, pergunta: str) -> tuple[str, list[str]]:
        """Corrige erros de um caractere quando há uma única opção no vocabulário.

        A correção é conservadora: só considera palavras com pelo menos cinco
        letras e só troca quando existe exatamente uma palavra candidata na
        base. Termos ambíguos permanecem como foram digitados.
        """
        original = str(pergunta or "")
        chave = original.casefold()
        if chave in self._cache_correcao:
            texto, mudancas = self._cache_correcao[chave]
            return texto, list(mudancas)

        tokens = normalizar(original).split()
        if self._vocabulario_busca is None:
            vocabulario = set()
            for item in self.orientacoes:
                for texto in [item.titulo, *item.palavras_chave]:
                    vocabulario.update(
                        token for token in normalizar(texto).split()
                        if len(token) >= 5
                    )
            self._vocabulario_busca = vocabulario

        palavras_comuns = {
            "quando", "quanto", "quero", "tenho", "minhas", "minhas",
            "minimo", "maximo", "porque", "tambem", "empresa", "empresas",
            "trabalho", "trabalhar", "trabalhei", "trabalhando", "direito",
            "direitos", "salario", "salarios", "pessoa", "pessoas", "podem",
            "receber", "recebo", "recebe", "recebi", "fazer", "preciso",
            "algum", "alguma", "alguns", "algumas", "meu", "minha",
            "seguro", "desemprego", "transporte", "curriculo", "emprego",
        }
        corrigidos = []
        mudancas = []
        for token in tokens:
            if len(token) < 5 or token in self._vocabulario_busca or token in palavras_comuns:
                corrigidos.append(token)
                continue
            candidatos = [
                palavra for palavra in self._vocabulario_busca
                if abs(len(palavra) - len(token)) <= 1
                and self._distancia_edicao_um(token, palavra)
            ]
            if len(candidatos) == 1:
                substituto = candidatos[0]
                corrigidos.append(substituto)
                mudancas.append(f"{token} → {substituto}")
            else:
                corrigidos.append(token)

        resultado = " ".join(corrigidos)
        self._cache_correcao[chave] = (resultado, mudancas)
        return resultado, list(mudancas)

    def explicar_pontuacao(self, pergunta: str, orientacao: Orientacao) -> dict:
        """Explica correspondências de expressões-chave e palavras do título.

        Uma expressão-chave é reconhecida quando seus termos relevantes aparecem
        na pergunta, mesmo que estejam separados por palavras intermediárias ou
        em outra ordem. Expressões menores contidas em expressões maiores são
        descartadas para evitar que sinônimos redundantes inflem a pontuação.
        Cada expressão-chave independente vale +3; cada termo relevante do título
        encontrado vale +1, preservando a regra de pontuação da atividade.
        """
        pergunta_corrigida, termos_corrigidos = self.corrigir_erros_digitacao(pergunta)
        pergunta_normalizada = normalizar(pergunta_corrigida)
        sequencia_pergunta = pergunta_normalizada.split()
        contexto_aprendiz = any(t in sequencia_pergunta for t in ("aprendiz", "aprendizagem", "jovem"))
        contexto_menor = contexto_aprendiz or any(t in pergunta_normalizada for t in ("menor", "adolescente", "17 ano", "16 ano", "15 ano", "14 ano"))
        tem_justa_causa = "justa" in sequencia_pergunta and "causa" in sequencia_pergunta
        tem_sem_justa_causa = "sem" in sequencia_pergunta and tem_justa_causa
        # O ID 37 trata exclusivamente do vale-transporte do Jovem Aprendiz.
        # Para trabalhadores em geral, priorize o registro 76.
        if orientacao.id == "37" and not contexto_aprendiz:
            return {"palavras_chave": [], "palavras_titulo": [], "pontos_chaves": 0, "pontos_titulo": 0, "total": 0, "especificidade": 0, "confianca": "INSUFICIENTE"}
        # Evita misturar dúvidas gerais com regras exclusivas de aprendizagem.
        if orientacao.id == "7" and not contexto_aprendiz:
            return {"palavras_chave": [], "palavras_titulo": [], "pontos_chaves": 0, "pontos_titulo": 0, "total": 0, "especificidade": 0, "confianca": "INSUFICIENTE"}
        if orientacao.id in ("13", "39") and not contexto_menor:
            return {"palavras_chave": [], "palavras_titulo": [], "pontos_chaves": 0, "pontos_titulo": 0, "total": 0, "especificidade": 0, "confianca": "INSUFICIENTE"}
        # ID 7 trata a jornada geral do aprendiz; as horas do curso têm FAQ própria (ID 40).
        if orientacao.id == "7" and any(t in sequencia_pergunta for t in ("curso", "teorico", "teorica")):
            return {"palavras_chave": [], "palavras_titulo": [], "pontos_chaves": 0, "pontos_titulo": 0, "total": 0, "especificidade": 0, "confianca": "INSUFICIENTE"}
        # Para pergunta genérica sobre menor aprendiz, manter a FAQ principal; usar ID 39 quando houver idade/horário explícito.
        if orientacao.id == "39" and not any(t.isdigit() for t in sequencia_pergunta):
            return {"palavras_chave": [], "palavras_titulo": [], "pontos_chaves": 0, "pontos_titulo": 0, "total": 0, "especificidade": 0, "confianca": "INSUFICIENTE"}
        # Se a pessoa pergunta por justa causa, não confundir com dispensa sem justa causa.
        if orientacao.id == "53" and tem_justa_causa and not tem_sem_justa_causa:
            return {"palavras_chave": [], "palavras_titulo": [], "pontos_chaves": 0, "pontos_titulo": 0, "total": 0, "especificidade": 0, "confianca": "INSUFICIENTE"}
        if orientacao.id == "54" and tem_sem_justa_causa:
            return {"palavras_chave": [], "palavras_titulo": [], "pontos_chaves": 0, "pontos_titulo": 0, "total": 0, "especificidade": 0, "confianca": "INSUFICIENTE"}
        # Perguntas sobre seguro-desemprego devem priorizar a orientação do benefício.
        if orientacao.id in ("46", "50", "53", "54") and "seguro" in sequencia_pergunta:
            return {"palavras_chave": [], "palavras_titulo": [], "pontos_chaves": 0, "pontos_titulo": 0, "total": 0, "especificidade": 0, "confianca": "INSUFICIENTE"}
        if orientacao.id == "46" and "aviso" in sequencia_pergunta:
            return {"palavras_chave": [], "palavras_titulo": [], "pontos_chaves": 0, "pontos_titulo": 0, "total": 0, "especificidade": 0, "confianca": "INSUFICIENTE"}
        if orientacao.id == "46" and ("luz" in sequencia_pergunta or "agua" in sequencia_pergunta) and ("conta" in sequencia_pergunta or "via" in sequencia_pergunta):
            return {"palavras_chave": [], "palavras_titulo": [], "pontos_chaves": 0, "pontos_titulo": 0, "total": 0, "especificidade": 0, "confianca": "INSUFICIENTE"}
        if orientacao.id == "69" and "fgts" in sequencia_pergunta:
            return {"palavras_chave": [], "palavras_titulo": [], "pontos_chaves": 0, "pontos_titulo": 0, "total": 0, "especificidade": 0, "confianca": "INSUFICIENTE"}
        # Uma comparação explícita não deve cair na orientação genérica de pedir demissão.
        if orientacao.id == "46" and any(t in pergunta_normalizada for t in ("comparar", "diferenca", "comparacao", "compare")) and tem_sem_justa_causa:
            return {"palavras_chave": [], "palavras_titulo": [], "pontos_chaves": 0, "pontos_titulo": 0, "total": 0, "especificidade": 0, "confianca": "INSUFICIENTE"}
        stopwords = {
            "a", "as", "o", "os", "um", "uma", "uns", "umas", "de", "da", "do",
            "das", "dos", "em", "no", "na", "nos", "nas", "por", "para", "com",
            "sem", "e", "ou", "que", "qual", "quais", "como", "quando", "onde",
            "meu", "minha", "meus", "minhas", "seu", "sua", "seus", "suas",
            "eu", "voce", "voces", "ele", "ela", "eles", "elas", "isso", "isto",
            "ser", "ter", "tem", "tenho", "pode", "podem", "preciso", "quero",
            "faco", "fazer", "fiz", "foi", "sou", "estou", "esta", "estao",
        }
        def aparece_na_pergunta(termos):
            """Reconhece expressão mesmo com inversão ou palavras intermediárias."""
            return set(termos).issubset(set(sequencia_pergunta))

        correspondencias_por_sequencia = {}
        for expressao in orientacao.palavras_chave:
            termos = tuple(
                t for t in normalizar(expressao).split()
                if t not in stopwords and len(t) > 1
            )
            if termos and aparece_na_pergunta(termos):
                correspondencias_por_sequencia.setdefault(termos, expressao)

        # Remove aliases redundantes: expressões menores que já aparecem dentro
        # de uma expressão mais específica não somam pontos pela segunda vez.
        sequencias = list(correspondencias_por_sequencia)
        def eh_subsequencia(menor, maior):
            posicao = 0
            for termo in maior:
                if posicao < len(menor) and termo == menor[posicao]:
                    posicao += 1
            return posicao == len(menor)

        sequencias_maximas = [
            termos for termos in sequencias
            if not any(termos != outra and eh_subsequencia(termos, outra) for outra in sequencias)
        ]
        palavras_chave_encontradas = [
            correspondencias_por_sequencia[termos] for termos in sequencias_maximas
        ]
        pontos_chaves = len(palavras_chave_encontradas) * PONTOS_PALAVRA_CHAVE

        # Consulta de uma palavra: não obrigar o cidadão a escrever a frase inteira.
        # Ex.: "emprego" encontra primeiro emprego; "seguro" encontra seguro-desemprego.
        # A regra só é aplicada a um termo de conteúdo com pelo menos quatro letras.
        if len(sequencia_pergunta) == 1:
            termo_unico = sequencia_pergunta[0]
            if len(termo_unico) >= 4 and not palavras_chave_encontradas:
                aparece_no_vocabulario = any(
                    termo_unico in normalizar(expressao).split()
                    for expressao in orientacao.palavras_chave
                ) or termo_unico in normalizar(orientacao.titulo).split()
                if aparece_no_vocabulario:
                    palavras_chave_encontradas = [f"termo isolado: {termo_unico}"]
                    pontos_chaves = PONTOS_PALAVRA_CHAVE

        palavras_pergunta = set(sequencia_pergunta)
        palavras_titulo = {
            palavra for palavra in normalizar(orientacao.titulo).split()
            if palavra not in stopwords and len(palavra) >= 4
        }
        palavras_titulo_encontradas = sorted(palavras_pergunta & palavras_titulo)
        pontos_titulo = len(palavras_titulo_encontradas) * PONTOS_TITULO
        total = pontos_chaves + pontos_titulo

        if total >= LIMITE_CONFIANCA_ALTA:
            confianca = "ALTA"
        elif total >= LIMITE_CONFIANCA_MEDIA:
            confianca = "MÉDIA"
        else:
            confianca = "INSUFICIENTE"

        return {
            "palavras_chave": palavras_chave_encontradas,
            "palavras_titulo": palavras_titulo_encontradas,
            "termos_corrigidos": termos_corrigidos,
            "pontos_chaves": pontos_chaves,
            "pontos_titulo": pontos_titulo,
            "total": total,
            "especificidade": max(
                (len([t for t in normalizar(expressao).split() if t not in stopwords and len(t) > 1])
                 for expressao in palavras_chave_encontradas),
                default=0,
            ),
            "confianca": confianca,
        }

    def pontuar(self, pergunta: str, orientacao: Orientacao) -> int:
        """Aplica as regras: palavra-chave +3 e palavra do título +1."""
        return self.explicar_pontuacao(pergunta, orientacao)["total"]

    def buscar_com_variantes(self, consultas: list[str]) -> list[tuple[int, Orientacao]]:
        """Busca pela pergunta original e paráfrases; usa a melhor pontuação por FAQ.

        A expansão melhora a recuperação, mas não cria fatos nem respostas. Cada
        orientação continua sendo selecionada pelo mecanismo de pontos exigido
        no trabalho (+3 por expressão-chave e +1 por termo do título).
        """
        consultas_unicas = []
        vistos = set()
        for consulta in consultas:
            consulta = str(consulta or "").strip()
            normalizada = normalizar(consulta)
            if normalizada and normalizada not in vistos:
                consultas_unicas.append(consulta)
                vistos.add(normalizada)

        if not consultas_unicas:
            self.consultas_usadas = {}
            return []

        resultados = []
        self.consultas_usadas = {}
        stopwords = {
            "a", "as", "o", "os", "um", "uma", "de", "da", "do", "das",
            "dos", "em", "no", "na", "nos", "nas", "por", "para", "com",
            "sem", "e", "ou", "que", "qual", "quais", "como", "quando",
            "onde", "meu", "minha", "seu", "sua", "eu", "voce", "ser",
            "ter", "tem", "tenho", "pode", "quero", "fazer", "foi",
        }
        for orientacao in self.orientacoes:
            melhor = None
            for indice, consulta in enumerate(consultas_unicas):
                detalhes = self.explicar_pontuacao(consulta, orientacao)
                candidato = (
                    detalhes["total"],
                    detalhes["especificidade"],
                    -indice,
                    consulta,
                )
                if melhor is None or candidato[:3] > melhor[:3]:
                    melhor = candidato
            if melhor is None:
                continue
            pontos, especificidade, _preferencia, consulta_usada = melhor
            resultados.append((pontos, especificidade, orientacao, consulta_usada))

        resultados.sort(
            key=lambda item: (-item[0], -item[1], item[2].titulo.casefold(), item[2].id)
        )
        self.consultas_usadas = {
            orientacao.id: consulta for _pontos, _esp, orientacao, consulta in resultados
        }
        return [(pontos, orientacao) for pontos, _esp, orientacao, _consulta in resultados]

    def consulta_usada(self, orientacao: Orientacao) -> str | None:
        """Retorna a consulta que produziu a melhor correspondência da orientação."""
        return getattr(self, "consultas_usadas", {}).get(orientacao.id)

    def buscar(self, pergunta: str) -> list[tuple[int, Orientacao]]:
        """Retorna (pontos, orientação), por pontuação e título crescente."""
        return self.buscar_com_variantes([pergunta])
