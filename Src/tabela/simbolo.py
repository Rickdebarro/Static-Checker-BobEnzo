from dataclasses import dataclass, field

MAX_LINHAS = 5  # spec: guarda apenas as 5 primeiras ocorrências


@dataclass
class Simbolo:
    indice: int                                   # posição na tabela (começa em 1)
    lexeme: str                                   # os 30 primeiros chars válidos
    codigo: str                                   # ex: "C01", "C06"
    qtd_antes_trunc: int                          # total de chars válidos lidos
    qtd_depois_trunc: int                         # len(lexeme) — máximo 30
    tipo: str = "-"                               # FP, IN, ST, CH, BL, VD... ou "-"
    linhas: list[int] = field(default_factory=list)  # até 5 linhas de ocorrência

    def adicionar_linha(self, linha: int):
        """Registra a linha de ocorrência — apenas as 5 primeiras"""
        if len(self.linhas) < MAX_LINHAS:
            self.linhas.append(linha)

    def set_tipo(self, tipo: str):
        self.tipo = tipo

    def __str__(self):
        linhas_fmt = "(" + ", ".join(str(l) for l in self.linhas) + ")"
        return (
            f"Entrada: {self.indice}, Código: {self.codigo}, Lexeme: {self.lexeme},\n"
            f"QtdCharsAntesTrunc: {self.qtd_antes_trunc}, "
            f"QtdCharDepoisTrunc: {self.qtd_depois_trunc},\n"
            f"TipoSimb: {self.tipo}, Linhas: {linhas_fmt}."
        )
