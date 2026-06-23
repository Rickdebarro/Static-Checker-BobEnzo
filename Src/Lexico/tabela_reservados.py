class TabelaPalavrasReservadas:
    def __init__(self):
        self._palavras: dict[str, str] = {}
        self.carregar_tabela_fixa()

    def carregar_tabela_fixa(self):
        self._palavras = {
            # --- Palavras Reservadas (A) — Apêndice A ---
            "BOOLEAN":        "A01",
            "BREAK":          "A02",
            "CHARACTER":      "A03",
            "DECLARATIONS":   "A04",
            "ELSE":           "A05",
            "ENDDECLARATIONS":"A06",
            "ENDFUNCTION":    "A07",
            "ENDFUNCTIONS":   "A08",
            "ENDIF":          "A09",
            "ENDPROGRAM":     "A10",
            "ENDWHILE":       "A11",
            "FALSE":          "A12",
            "FUNCTIONS":      "A13",
            "FUNCTYPE":       "A14",
            "IF":             "A15",
            "INTEGER":        "A16",
            "PARAMTYPE":      "A17",
            "PRINT":          "A18",
            "PROGRAM":        "A19",
            "REAL":           "A20",
            "RETURN":         "A21",
            "STRING":         "A22",
            "TRUE":           "A23",
            "VARTYPE":        "A24",
            "VOID":           "A25",
            "WHILE":          "A26",
            # --- Símbolos de 2 caracteres (B) — verificar ANTES dos de 1 ---
            ":=":  "B04",
            "==":  "B17",
            "!=":  "B18",
            "<=":  "B20",
            ">=":  "B22",
            # --- Símbolos de 1 caractere (B) ---
            ";":   "B01",
            ",":   "B02",
            ":":   "B03",
            "?":   "B05",
            "(":   "B06",
            ")":   "B07",
            "[":   "B08",
            "]":   "B09",
            "{":   "B10",
            "}":   "B11",
            "+":   "B12",
            "-":   "B13",
            "*":   "B14",
            "/":   "B15",
            "%":   "B16",
            "#":   "B18",   # alias para != (spec pág. 14)
            "<":   "B19",
            ">":   "B21",
        }

    def contem(self, lexeme: str) -> bool:
        return lexeme.upper() in self._palavras

    def get_codigo(self, lexeme: str) -> str | None:
        return self._palavras.get(lexeme.upper())
