"""Núcleo conversacional por IA + recuperação em base oficial do Trilha Cidadã.

A IA interpreta todas as perguntas quando configurada, seleciona orientações da
base local e sintetiza uma resposta a partir desses registros. Ela não deve
inventar regras trabalhistas nem substituir as fontes oficiais.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.request


class ExpansorConsultaIA:
    """Integra o Trilha Cidadã à API do Ollama Cloud ou a um servidor local."""

    def __init__(
        self,
        base_url: str,
        modelo: str,
        chave_api: str = "",
        timeout: float = 45.0,
    ):
        self.base_url = (base_url or "").rstrip("/")
        self.modelo = modelo or "gemma4:31b"
        self.chave_api = chave_api or ""
        self.timeout = max(5.0, float(timeout))
        self.cache_analises: dict[str, dict] = {}
        self.cache_expansoes: dict[str, list[str]] = {}
        self.ultimo_erro = ""

    @classmethod
    def do_projeto(cls, pasta_projeto: str | Path):
        """Lê .env sem bibliotecas externas e ativa IA somente com config válida."""
        pasta = Path(pasta_projeto)
        configuracoes = {}
        caminho_env = pasta / ".env"
        if caminho_env.exists():
            try:
                for linha in caminho_env.read_text(encoding="utf-8-sig").splitlines():
                    linha = linha.strip()
                    if not linha or linha.startswith("#") or "=" not in linha:
                        continue
                    chave, valor = linha.split("=", 1)
                    configuracoes[chave.strip()] = valor.strip().strip('"').strip("'")
            except OSError:
                pass

        def obter(nome, alternativo=None, padrao=""):
            return (
                os.getenv(nome)
                or (os.getenv(alternativo) if alternativo else "")
                or configuracoes.get(nome)
                or (configuracoes.get(alternativo) if alternativo else "")
                or padrao
            )

        api_key = obter("OLLAMA_API_KEY")
        base_url = obter("OLLAMA_BASE_URL", "OLLAMA_HOST", "http://localhost:11434")
        modelo = obter("OLLAMA_MODEL", padrao="gemma4:31b")
        timeout_texto = obter("OLLAMA_TIMEOUT", padrao="45")
        try:
            timeout = float(timeout_texto)
        except ValueError:
            timeout = 45.0

        explicitamente_configurado = bool(
            api_key
            or os.getenv("OLLAMA_BASE_URL")
            or os.getenv("OLLAMA_HOST")
            or configuracoes.get("OLLAMA_BASE_URL")
            or configuracoes.get("OLLAMA_HOST")
        )
        if not explicitamente_configurado:
            return None
        if base_url.startswith("https://") and not api_key:
            return None
        if api_key.strip().upper() in {
            "COLOQUE_SUA_CHAVE_AQUI", "SUA_CHAVE", "API_KEY", "SUA_CHAVE_OLLAMA"
        }:
            return None
        return cls(base_url, modelo, api_key, timeout)

    @property
    def configurado(self) -> bool:
        return bool(self.base_url and (not self.base_url.startswith("https://") or self.chave_api))

    def _chat_json(self, sistema: str, usuario: str, num_predict: int = 1400) -> dict | None:
        """Executa uma chamada JSON e devolve o objeto já validado sintaticamente."""
        if not self.configurado:
            self.ultimo_erro = "Integração não configurada. Confira o arquivo .env."
            return None

        payload = {
            "model": self.modelo,
            "messages": [
                {"role": "system", "content": sistema},
                {"role": "user", "content": usuario},
            ],
            "stream": False,
            "format": "json",
            "options": {"temperature": 0, "num_predict": num_predict},
        }
        dados = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        cabecalhos = {"Content-Type": "application/json"}
        if self.chave_api:
            cabecalhos["Authorization"] = f"Bearer {self.chave_api}"
        url = f"{self.base_url}/api/chat"
        requisicao = urllib.request.Request(url, data=dados, headers=cabecalhos, method="POST")

        try:
            with urllib.request.urlopen(requisicao, timeout=self.timeout) as resposta:
                conteudo = json.loads(resposta.read().decode("utf-8"))
            texto = conteudo.get("message", {}).get("content", "")
            if isinstance(texto, dict):
                self.ultimo_erro = ""
                return texto
            if not isinstance(texto, str) or not texto.strip():
                self.ultimo_erro = "A API respondeu sem conteúdo."
                return None
            texto = texto.strip()
            texto = re.sub(r"^```(?:json)?\s*|\s*```$", "", texto, flags=re.IGNORECASE)
            resultado = json.loads(texto)
            if not isinstance(resultado, dict):
                self.ultimo_erro = "A resposta da IA não veio como objeto JSON."
                return None
            self.ultimo_erro = ""
            return resultado
        except urllib.error.HTTPError as erro:
            detalhe = ""
            try:
                detalhe = erro.read().decode("utf-8", errors="replace")[:300]
            except Exception:
                pass
            self.ultimo_erro = f"Ollama HTTP {erro.code}: {detalhe or erro.reason}"
            return None
        except urllib.error.URLError as erro:
            self.ultimo_erro = f"Falha de conexão com Ollama: {getattr(erro, 'reason', erro)}"
            return None
        except TimeoutError:
            self.ultimo_erro = f"A IA excedeu o limite de {self.timeout:.0f} segundos."
            return None
        except (OSError, ValueError, TypeError, KeyError) as erro:
            self.ultimo_erro = f"Não foi possível interpretar a resposta da IA: {erro}"
            return None

    @staticmethod
    def _catalogo(orientacoes) -> list[dict]:
        """Prepara todas as orientações para recuperação semântica pela IA."""
        catalogo = []
        for item in orientacoes:
            catalogo.append({
                "id": str(item.id),
                "categoria": item.categoria,
                "titulo": item.titulo,
                "palavras_chave": item.palavras_chave,
                "resposta_verificada": item.resposta,
                "documentos": item.documentos,
                "onde": item.onde,
                "fonte_oficial": item.fonte,
                "verificado_em": item.verificado_em,
            })
        return catalogo

    def analisar(self, pergunta: str, orientacoes) -> dict | None:
        """Entende toda pergunta, recupera registros e redige resposta fundamentada."""
        pergunta = " ".join(str(pergunta or "").split())
        if not pergunta:
            return None
        if sum(caractere.isdigit() for caractere in pergunta) >= 8 or "@" in pergunta:
            self.ultimo_erro = "Consulta bloqueada por proteção de dados pessoais."
            return None

        chave_cache = pergunta.casefold()
        if chave_cache in self.cache_analises:
            return dict(self.cache_analises[chave_cache])

        catalogo = self._catalogo(orientacoes)
        ids_validos = {item["id"] for item in catalogo}
        sistema = (
            "Você é o núcleo de IA do Trilha Cidadã, um assistente brasileiro de orientação "
            "sobre primeiro emprego, busca de vagas, currículo, entrevistas, qualificação, "
            "Jovem Aprendiz, carteira de trabalho, contratos, salários, benefícios, jornada, "
            "segurança, direitos trabalhistas, demissão, FGTS, seguro-desemprego e serviços "
            "públicos ligados ao trabalho. Responda em português brasileiro, com linguagem simples.\n\n"
            "SUA TAREFA: interpretar a pergunta do usuário e responder de forma útil. Você deve "
            "ser usado em TODA pergunta, inclusive quando ela contém uma única palavra ou quando "
            "a busca exata teria pontuação baixa. Não dependa de correspondência literal.\n\n"
            "ESCOPO: assuntos de trabalho, empregabilidade, entrada e permanência no mercado, "
            "formação profissional e direitos do trabalhador. Fora disso (receitas, jogos, clima, "
            "relacionamentos sem relação com trabalho etc.), classifique como fora do escopo.\n\n"
            "BASE: abaixo você receberá TODOS os registros oficiais locais. Use-os como fonte "
            "prioritária. Pode combinar mais de um registro. Não invente direitos, prazos, valores, "
            "percentuais, artigos de lei, documentos ou canais. Nunca atribua a uma fonte um fato "
            "que não aparece no registro. Diferencie trabalhador comum de Jovem Aprendiz e não "
            "generalize regras específicas de uma modalidade para outra.\n\n"
            "COMPORTAMENTO: termos curtos dentro do tema devem ser interpretados. Exemplos: "
            "'emprego' deve levar a orientações de primeiro emprego/vagas; 'seguro', neste contexto, "
            "provavelmente significa seguro-desemprego e você deve declarar essa interpretação; "
            "'transporte' deve levar ao vale-transporte. Se houver ambiguidade real, escolha a "
            "interpretação mais provável dentro do tema e informe a suposição na resposta, sem "
            "recusar automaticamente.\n\n"
            "RESPOSTA: quando houver informação nos registros, responda diretamente, organize em "
            "passos quando útil e indique o que a pessoa pode fazer. Em pergunta ampla como 'emprego', "
            "dê um ponto de partida prático usando os registros relevantes. Se a pergunta for de "
            "empregabilidade geral (currículo, procura, entrevista), você pode complementar com "
            "orientação geral não jurídica. Para uma dúvida jurídica específica sem informação "
            "suficiente nos registros, não chute: explique o limite e indique o canal oficial.\n\n"
            "CLASSIFICAÇÃO: 'dentro' para qualquer pergunta relacionada ao escopo; 'fora' somente "
            "para temas claramente alheios; 'ambiguo' quando não der para decidir. Não classifique "
            "pergunta curta como fora apenas por ser curta.\n\n"
            "RETORNE SOMENTE JSON válido com este formato: "
            '{"escopo":"dentro|fora|ambiguo","titulo":"...",'
            '"ids_relevantes":["id"],"ids_fontes":["id"],"resposta":"...",'
            '"consultas":["..."],"precisa_esclarecer":false,"pergunta_esclarecimento":""}.\n'
            "IDs são somente os IDs existentes no catálogo. Use até 4 IDs relevantes e até 3 IDs "
            "de fontes. Se usar fatos dos registros, inclua seus IDs em ids_fontes. Não invente IDs. "
            "A resposta deve ter até 1800 caracteres. Para fora do escopo, deixe resposta e listas vazias."
        )
        usuario = (
            f"PERGUNTA DO CIDADÃO:\n{pergunta[:700]}\n\n"
            "CATÁLOGO COMPLETO DA BASE VERIFICADA (JSON):\n"
            + json.dumps(catalogo, ensure_ascii=False, separators=(",", ":"))
        )
        bruto = self._chat_json(sistema, usuario, num_predict=1800)
        if bruto is None:
            return None

        escopo = str(bruto.get("escopo", "ambiguo")).casefold().strip()
        mapa_escopo = {
            "dentro_escopo": "dentro", "in_scope": "dentro", "inside": "dentro",
            "out_of_scope": "fora", "fora_escopo": "fora", "outside": "fora",
        }
        escopo = mapa_escopo.get(escopo, escopo)
        if escopo not in {"dentro", "fora", "ambiguo"}:
            escopo = "ambiguo"

        def limpar_ids(valor, limite):
            if not isinstance(valor, list):
                return []
            saida = []
            for identificador in valor:
                texto = str(identificador).strip()
                if texto in ids_validos and texto not in saida:
                    saida.append(texto)
                if len(saida) >= limite:
                    break
            return saida

        ids_relevantes = limpar_ids(bruto.get("ids_relevantes", []), 4)
        ids_fontes = limpar_ids(bruto.get("ids_fontes", []), 3)
        ids_fontes = [item for item in ids_fontes if item in ids_relevantes] or ids_relevantes[:3]
        resposta = bruto.get("resposta", "")
        if not isinstance(resposta, str):
            resposta = ""
        resposta = "\n".join(linha.rstrip() for linha in resposta.strip().splitlines())[:1800]
        consultas = bruto.get("consultas", [])
        if not isinstance(consultas, list):
            consultas = []
        consultas_ok = []
        for consulta in consultas:
            if not isinstance(consulta, str):
                continue
            consulta = " ".join(consulta.split())[:120]
            if consulta and consulta.casefold() != pergunta.casefold() and consulta not in consultas_ok:
                if sum(c.isdigit() for c in consulta) < 8 and "@" not in consulta:
                    consultas_ok.append(consulta)
            if len(consultas_ok) >= 4:
                break

        resultado = {
            "escopo": escopo,
            "titulo": str(bruto.get("titulo", "")).strip()[:120],
            "ids_relevantes": ids_relevantes,
            "ids_fontes": ids_fontes,
            "resposta": resposta,
            "consultas": consultas_ok,
            "precisa_esclarecer": bool(bruto.get("precisa_esclarecer", False)),
            "pergunta_esclarecimento": str(bruto.get("pergunta_esclarecimento", "")).strip()[:240],
        }
        self.cache_analises[chave_cache] = resultado
        return dict(resultado)

    def expandir(self, pergunta: str, titulos: list[str] | None = None) -> list[str]:
        """Compatibilidade com versão anterior: cria consultas equivalentes."""
        pergunta = str(pergunta or "").strip()
        if not pergunta:
            return []
        if sum(caractere.isdigit() for caractere in pergunta) >= 8 or "@" in pergunta:
            return []
        chave_cache = pergunta.casefold()
        if chave_cache in self.cache_expansoes:
            return list(self.cache_expansoes[chave_cache])
        if sum(caractere.isdigit() for caractere in pergunta) >= 8 or "@" in pergunta:
            return []

        titulos_texto = "\n".join(f"- {titulo}" for titulo in (titulos or [])[:100])
        sistema = (
            "Você expande consultas de um assistente brasileiro de orientação ao trabalho. "
            "Não responda à dúvida. Retorne somente JSON {\"consultas\":[...]}, com até quatro "
            "paráfrases curtas em português brasileiro."
        )
        usuario = f"Pergunta: {pergunta[:300]}\nAssuntos disponíveis:\n{titulos_texto}"
        bruto = self._chat_json(sistema, usuario, num_predict=220)
        consultas = bruto.get("consultas", []) if bruto else []
        if not isinstance(consultas, list):
            consultas = []
        saida = []
        for item in consultas:
            if isinstance(item, str):
                item = " ".join(item.split())[:120]
                if item and item.casefold() != pergunta.casefold() and item not in saida:
                    if sum(c.isdigit() for c in item) < 8 and "@" not in item:
                        saida.append(item)
            if len(saida) == 4:
                break
        self.cache_expansoes[chave_cache] = saida
        return list(saida)

    def testar_conexao(self) -> tuple[bool, str]:
        """Faz uma chamada real mínima e devolve diagnóstico sem expor a chave."""
        if not self.configurado:
            return False, "IA não configurada. Confira OLLAMA_BASE_URL e OLLAMA_API_KEY no .env."
        bruto = self._chat_json(
            "Responda somente JSON válido: {\"ok\":true,\"mensagem\":\"conexao ativa\"}.",
            "Verifique a conexão respondendo ok.",
            num_predict=80,
        )
        if bruto and bruto.get("ok") is True:
            return True, f"Conexão confirmada com {self.modelo} em {self.base_url}."
        return False, self.ultimo_erro or "A API respondeu, mas não confirmou o teste."
