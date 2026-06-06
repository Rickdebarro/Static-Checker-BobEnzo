from dataclasses import dataclass

class Token:
    lexeme: str        # o texto encontrado, ("VAR1", ":=", "REAL")
    codigo: str        # código do átomo("C01", "B04", "A20")
    linha: int         # linha onde apareceu no texto fonte
    columna: int       # coluna onde apareceu no texto fonte
    indice_tab: int    # índice na tabela de símbolos (-1 se não for identificador)

    # formato de impressão do token
    def __str__(self):
        idx = self.indice_tab if self.indice_tab != -1 else "-"
        return (f"Lexeme: {self.lexeme}, "
                f"Código: {self.codigo}, "
                f"indiceTabSimb: {idx}, "
                f"Linha: {self.linha}.")