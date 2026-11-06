"""Avaliação reproduzível da busca do Trilha Cidadã.

O conjunto de perguntas é um benchmark de regressão escrito pela equipe.
Ele ajuda a detectar mudanças no comportamento da busca, mas não representa
uma medição estatística de todos os cidadãos ou de todas as formas de pergunta.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
import json
from pathlib import Path


CABECALHO_AVALIACAO = ["id", "tipo", "pergunta", "orientacao_esperada"]
TIPOS_VALIDOS = {"dentro_escopo", "fora_escopo"}
LIMITE_RESPOSTA = 3


class AvaliadorBusca:
    """Executa perguntas de referência e calcula métricas da busca."""

    def __init__(self, base, caminho_perguntas: str | Path):
        self.base = base
        self.caminho_perguntas = Path(caminho_perguntas)
        self.perguntas: list[dict] = []
        self.erros: list[str] = []

    def carregar_perguntas(self) -> bool:
        """Carrega e valida o conjunto de perguntas separado por ponto e vírgula."""
        self.perguntas = []
        self.erros = []

        if not self.caminho_perguntas.exists():
            self.erros.append(f"Arquivo não encontrado: {self.caminho_perguntas}")
            return False

        ids_encontrados: set[str] = set()
        ids_base = {orientacao.id for orientacao in self.base.orientacoes}

        try:
            with self.caminho_perguntas.open("r", encoding="utf-8-sig") as arquivo:
                primeira_linha = arquivo.readline().rstrip("\r\n")
                if primeira_linha.split(";") != CABECALHO_AVALIACAO:
                    self.erros.append(
                        "Cabeçalho inválido no arquivo de avaliação."
                    )
                    return False

                for numero_linha, linha in enumerate(arquivo, start=2):
                    linha = linha.rstrip("\r\n")
                    if not linha.strip():
                        continue

                    campos = [campo.strip() for campo in linha.split(";")]
                    if len(campos) != len(CABECALHO_AVALIACAO):
                        self.erros.append(
                            f"Linha {numero_linha}: quantidade de campos inválida."
                        )
                        continue

                    identificador, tipo, pergunta, esperado = campos
                    if not identificador or identificador in ids_encontrados:
                        self.erros.append(
                            f"Linha {numero_linha}: identificador vazio ou duplicado."
                        )
                        continue
                    if tipo not in TIPOS_VALIDOS:
                        self.erros.append(
                            f"Linha {numero_linha}: tipo deve ser dentro_escopo ou fora_escopo."
                        )
                        continue
                    if not pergunta:
                        self.erros.append(
                            f"Linha {numero_linha}: pergunta vazia."
                        )
                        continue

                    if tipo == "dentro_escopo":
                        if not esperado or esperado not in ids_base:
                            self.erros.append(
                                f"Linha {numero_linha}: orientação esperada inexistente."
                            )
                            continue
                    elif esperado:
                        self.erros.append(
                            f"Linha {numero_linha}: pergunta fora do escopo não deve ter orientação esperada."
                        )
                        continue

                    self.perguntas.append(
                        {
                            "id": identificador,
                            "tipo": tipo,
                            "pergunta": pergunta,
                            "orientacao_esperada": esperado,
                        }
                    )
                    ids_encontrados.add(identificador)

        except OSError as erro:
            self.erros.append(f"Não foi possível ler o arquivo de avaliação: {erro}")
            return False

        dentro = sum(1 for item in self.perguntas if item["tipo"] == "dentro_escopo")
        fora = sum(1 for item in self.perguntas if item["tipo"] == "fora_escopo")
        if dentro == 0:
            self.erros.append("O conjunto precisa ter perguntas dentro do escopo.")
        if fora == 0:
            self.erros.append("O conjunto precisa ter perguntas fora do escopo.")

        return bool(self.perguntas) and not self.erros

    def executar(self) -> dict:
        """Executa o benchmark e devolve resultados e métricas agregadas."""
        if not self.perguntas:
            raise ValueError("Carregue perguntas válidas antes de executar a avaliação.")

        resultados = []
        totais_categoria = defaultdict(lambda: {"total": 0, "corretas": 0})

        dentro_total = 0
        dentro_corretas = 0
        dentro_top3 = 0
        dentro_com_resposta = 0
        dentro_corretas_com_resposta = 0
        fora_total = 0
        fora_abstencoes_corretas = 0
        fora_falsos_positivos = 0
        total_corretos = 0

        for item in self.perguntas:
            ranking = self.base.buscar(item["pergunta"])
            melhor_pontuacao, melhor_orientacao = ranking[0] if ranking else (0, None)
            respondeu = melhor_orientacao is not None and melhor_pontuacao >= LIMITE_RESPOSTA
            top3_ids = [orientacao.id for pontos, orientacao in ranking[:3] if pontos >= LIMITE_RESPOSTA]

            if item["tipo"] == "dentro_escopo":
                dentro_total += 1
                esperado = item["orientacao_esperada"]
                acerto_top1 = respondeu and melhor_orientacao.id == esperado
                acerto_top3 = esperado in top3_ids
                if respondeu:
                    dentro_com_resposta += 1
                    if acerto_top1:
                        dentro_corretas_com_resposta += 1
                if acerto_top1:
                    dentro_corretas += 1
                    total_corretos += 1
                if acerto_top3:
                    dentro_top3 += 1

                orientacao_esperada = next(
                    (orientacao for orientacao in self.base.orientacoes if orientacao.id == esperado),
                    None,
                )
                categoria = orientacao_esperada.categoria if orientacao_esperada else "Sem categoria"
                totais_categoria[categoria]["total"] += 1
                if acerto_top1:
                    totais_categoria[categoria]["corretas"] += 1
                status = "correta" if acerto_top1 else ("incorreta" if respondeu else "sem_resposta")
            else:
                fora_total += 1
                esperado = ""
                acerto_top1 = not respondeu
                acerto_top3 = not respondeu
                if acerto_top1:
                    fora_abstencoes_corretas += 1
                    total_corretos += 1
                    status = "abstencao_correta"
                else:
                    fora_falsos_positivos += 1
                    status = "falso_positivo"
                categoria = "Fora do escopo"

            resultados.append(
                {
                    "id": item["id"],
                    "tipo": item["tipo"],
                    "pergunta": item["pergunta"],
                    "orientacao_esperada": esperado,
                    "orientacao_prevista": melhor_orientacao.id if respondeu else "",
                    "titulo_previsto": melhor_orientacao.titulo if respondeu else "",
                    "pontuacao": melhor_pontuacao,
                    "confianca": self._confianca(melhor_pontuacao),
                    "respondeu": respondeu,
                    "acerto_top1": bool(acerto_top1),
                    "acerto_top3": bool(acerto_top3),
                    "status": status,
                    "categoria": categoria,
                }
            )

        total = len(resultados)
        total_fora_corretos = fora_abstencoes_corretas
        categorias = {
            nome: {
                "total": dados["total"],
                "corretas": dados["corretas"],
                "acuracia_top1_percentual": self._percentual(
                    dados["corretas"], dados["total"]
                ),
            }
            for nome, dados in sorted(totais_categoria.items())
        }

        return {
            "executado_em": datetime.now().astimezone().isoformat(timespec="seconds"),
            "arquivo_perguntas": self.caminho_perguntas.name,
            "orientacoes_na_base": len(self.base.orientacoes),
            "total_casos": total,
            "dentro_escopo": {
                "total": dentro_total,
                "acertos_top1": dentro_corretas,
                "acuracia_top1_percentual": self._percentual(dentro_corretas, dentro_total),
                "acertos_top3": dentro_top3,
                "acuracia_top3_percentual": self._percentual(dentro_top3, dentro_total),
                "cobertura_percentual": self._percentual(dentro_com_resposta, dentro_total),
                "respostas_corretas_entre_as_emitidas_percentual": self._percentual(
                    dentro_corretas_com_resposta, dentro_com_resposta
                ),
                "respostas_emitidas": dentro_com_resposta,
                "abstencoes": dentro_total - dentro_com_resposta,
                "classificacoes_incorretas_com_resposta": dentro_com_resposta - dentro_corretas_com_resposta,
            },
            "fora_escopo": {
                "total": fora_total,
                "abstencoes_corretas": fora_abstencoes_corretas,
                "falsos_positivos": fora_falsos_positivos,
                "taxa_falso_positivo_percentual": self._percentual(
                    fora_falsos_positivos, fora_total
                ),
            },
            "acuracia_geral_percentual": self._percentual(total_corretos, total),
            "por_categoria": categorias,
            "casos": resultados,
            "observacao_metodologica": (
                "Benchmark interno e determinístico, criado pela equipe para regressão. "
                "Não representa uma estimativa estatística de desempenho em toda a população."
            ),
        }

    @staticmethod
    def _percentual(parte: int, total: int) -> float:
        return round((parte / total) * 100, 1) if total else 0.0

    @staticmethod
    def _confianca(pontos: int) -> str:
        if pontos >= 6:
            return "ALTA"
        if pontos >= 3:
            return "MÉDIA"
        return "INSUFICIENTE"

    @staticmethod
    def salvar_relatorio(relatorio: dict, caminho: str | Path) -> Path:
        """Salva o resultado completo em JSON para comparação entre versões."""
        destino = Path(caminho)
        destino.parent.mkdir(parents=True, exist_ok=True)
        with destino.open("w", encoding="utf-8") as arquivo:
            json.dump(relatorio, arquivo, ensure_ascii=False, indent=2)
            arquivo.write("\n")
        return destino

    @staticmethod
    def exibir_resumo(relatorio: dict) -> None:
        """Exibe um resumo legível no terminal."""
        dentro = relatorio["dentro_escopo"]
        fora = relatorio["fora_escopo"]
        print("\nTRILHA CIDADÃ — AVALIAÇÃO DA BUSCA")
        print("=" * 43)
        print(f"Casos avaliados: {relatorio['total_casos']}")
        print("\nPERGUNTAS DENTRO DO ESCOPO")
        print(
            f"Acurácia da primeira resposta: {dentro['acuracia_top1_percentual']:.1f}% "
            f"({dentro['acertos_top1']}/{dentro['total']})"
        )
        print(
            f"Encontrada entre as três primeiras: {dentro['acuracia_top3_percentual']:.1f}%"
        )
        print(f"Cobertura: {dentro['cobertura_percentual']:.1f}%")
        print(
            "Respostas corretas entre as emitidas: "
            f"{dentro['respostas_corretas_entre_as_emitidas_percentual']:.1f}%"
        )
        print(f"Abstenções: {dentro['abstencoes']}")
        print(
            "Classificações incorretas com resposta: "
            f"{dentro['classificacoes_incorretas_com_resposta']}"
        )

        print("\nPERGUNTAS FORA DO ESCOPO")
        print(f"Abstenções corretas: {fora['abstencoes_corretas']}/{fora['total']}")
        print(f"Falsos positivos: {fora['falsos_positivos']}")
        print(
            f"Taxa de falso positivo: {fora['taxa_falso_positivo_percentual']:.1f}%"
        )
        print(
            f"\nAcurácia geral do benchmark: "
            f"{relatorio['acuracia_geral_percentual']:.1f}%"
        )

        print("\nRESULTADOS POR CATEGORIA")
        for categoria, dados in relatorio["por_categoria"].items():
            print(
                f"- {categoria}: {dados['acuracia_top1_percentual']:.1f}% "
                f"({dados['corretas']}/{dados['total']})"
            )

        falhas = [caso for caso in relatorio["casos"] if not caso["acerto_top1"]]
        if falhas:
            print("\nCASOS QUE PRECISAM DE REVISÃO")
            for caso in falhas:
                previsto = caso["orientacao_prevista"] or "nenhuma"
                esperado = caso["orientacao_esperada"] or "abster-se"
                print(
                    f"- {caso['id']}: esperado {esperado}, previsto {previsto} "
                    f"(pontuação {caso['pontuacao']})"
                )
        else:
            print("\nNenhuma falha no conjunto atual de perguntas.")

        print("\nObservação: resultado de benchmark interno, não teste com usuários reais.")
