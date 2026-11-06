"""Modelo de dados de uma orientação cidadã."""

from dataclasses import dataclass, field


@dataclass
class Orientacao:
    """Representa uma orientação verificada ou uma resposta sintetizada com IA."""

    id: str
    categoria: str
    titulo: str
    palavras_chave: list[str]
    resposta: str
    documentos: list[str]
    onde: str
    fonte: str
    verificado_em: str
    gerada_por_ia: bool = False
    ids_origem: list[str] = field(default_factory=list)
    fontes_adicionais: list[dict] = field(default_factory=list)
    aviso_ia: str = ""

    def exibir(self) -> str:
        """Monta uma apresentação legível para o terminal."""
        documentos = "\n".join(
            f"  • {item}" for item in self.documentos
        ) or "  • Consulte a fonte oficial."
        fontes = [self.fonte] if self.fonte else []
        fontes.extend(
            item.get("url", "") for item in self.fontes_adicionais
            if item.get("url") and item.get("url") not in fontes
        )
        fontes_texto = "\n".join(f"  • {url}" for url in fontes) or "  • Consulte o portal oficial do MTE."
        aviso_ia = f"\nNota sobre IA: {self.aviso_ia}" if self.aviso_ia else ""

        return (
            f"{self.titulo} [{self.categoria}]\n\n"
            f"{self.resposta}\n\n"
            f"Documentos ou informações úteis:\n{documentos}\n\n"
            f"Onde: {self.onde}\n"
            f"Fontes oficiais:\n{fontes_texto}\n"
            f"Verificado em: {self.verificado_em}{aviso_ia}\n"
            "Aviso: este assistente não é um canal oficial. "
            "Confirme os detalhes na fonte indicada."
        )
