from dataclasses import dataclass, field


@dataclass
class Token:
    lexeme: str           # texto encontrado ex: "VAR1", ":=", "REAL"
    codigo: str           # código do átomo  ex: "C01", "B04", "A20"
    linha: int            # linha onde apareceu no texto fonte
    coluna: int           # coluna onde apareceu
    indice_tab: int       # índice na tabela de símbolos (-1 se não for identificador)
    qtd_antes_trunc: int = 0   # total de chars válidos lidos (pode ser > 30)
    qtd_depois_trunc: int = 0  # chars no lexeme guardado (≤ 30)

    def __str__(self):
        idx = self.indice_tab if self.indice_tab != -1 else "-"
        return (
            f"Lexeme: {self.lexeme}, "
            f"Código: {self.codigo}, "
            f"indiceTabSimb: {idx}, "
            f"Linha: {self.linha}."
        )
