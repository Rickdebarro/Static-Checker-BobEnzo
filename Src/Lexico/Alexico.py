from .token import Token
from .tabela_reservados import TabelaPalavrasReservadas

LIMITE = 30  # spec: máximo de 30 caracteres válidos por átomo


def _eh_valido(c: str) -> bool:
    """Caracteres válidos da linguagem fora de strings/comentários."""
    return c.isalnum() or c in " \t\n\r_.,;:=?()[]{}+-*/%<>!#\"'"


class Alexico:
    def __init__(self, conteudo: str, tabela_reservada: TabelaPalavrasReservadas):
        self.fonte = conteudo.upper() 
        self.tabela_reservada = tabela_reservada
        self.pos = 0
        self.linha = 1
        self.coluna = 1

    # ------------------------------------------------------------------
    # O sintático chama isso UMA VEZ por token
    # ------------------------------------------------------------------
    def obter_proximo_token(self) -> Token | None:
        while self.pos < len(self.fonte):
            c = self.fonte[self.pos]

            # Quebras de linha — atualiza contadores, não gera token
            if c == '\n':
                self.linha += 1
                self.coluna = 1
                self.pos += 1
                continue
            if c == '\r':
                self.pos += 1
                continue

            # Espaços e tabs — delimitadores puros
            if c in (' ', '\t'):
                self.coluna += 1
                self.pos += 1
                continue

            # Comentário de bloco /* ... */
            if c == '/' and self._peek(1) == '*':
                self._pular_comentario_bloco()
                continue

            # Comentário de linha // ...
            if c == '/' and self._peek(1) == '/':
                self._pular_comentario_linha()
                continue

            # Identificador ou palavra reservada
            if c.isalpha() or c == '_':
                return self._ler_identificador_ou_reservada()

            # Número inteiro ou real
            if c.isdigit():
                return self._ler_numero()

            # String com aspas duplas
            if c == '"':
                return self._ler_string()

            # Char com aspas simples
            if c == "'":
                return self._ler_char()

            # Símbolo de 2 caracteres — testa ANTES do de 1
            dois = c + (self._peek(1) or "")
            if self.tabela_reservada.contem(dois):
                col = self.coluna
                self.pos += 2
                self.coluna += 2
                return Token(dois, self.tabela_reservada.get_codigo(dois),
                             self.linha, col, -1, 2, 2)

            # Símbolo de 1 caractere
            if self.tabela_reservada.contem(c):
                col = self.coluna
                self.pos += 1
                self.coluna += 1
                return Token(c, self.tabela_reservada.get_codigo(c),
                             self.linha, col, -1, 1, 1)

            # Filtro de 1º nível: caractere inválido — descarta silenciosamente
            self.pos += 1
            self.coluna += 1

        return None  # EOF

    # ------------------------------------------------------------------
    # Leitores específicos por tipo de átomo
    # ------------------------------------------------------------------

    def _ler_identificador_ou_reservada(self) -> Token:
        lexeme = ""
        qtd_total = 0       # todos os chars válidos lidos (antes de truncar)
        col_inicio = self.coluna
        linha_inicio = self.linha

        while self.pos < len(self.fonte):
            c = self.fonte[self.pos]

            if c.isalnum() or c == '_':
                qtd_total += 1          # conta SEMPRE (mesmo depois do limite)
                if len(lexeme) < LIMITE:
                    lexeme += c         # guarda só os 30 primeiros
                self.pos += 1
                self.coluna += 1

            elif not _eh_valido(c):
                # Filtro de 1º nível DENTRO do átomo:
                # caractere inválido não conta e não quebra o átomo
                self.pos += 1
                self.coluna += 1

            else:
                break  # delimitador legítimo — encerra o átomo

        qtd_depois_trunc = len(lexeme)  # ≤ 30

        # Palavra reservada tem prioridade
        if self.tabela_reservada.contem(lexeme):
            return Token(
                lexeme,
                self.tabela_reservada.get_codigo(lexeme),
                linha_inicio, col_inicio, -1,
                qtd_total, qtd_depois_trunc,
            )

        # Identificador comum — índice será preenchido pelo main
        return Token(
            lexeme, "C01",
            linha_inicio, col_inicio, -1,
            qtd_total, qtd_depois_trunc,
        )

    def _ler_numero(self) -> Token:
        lexeme = ""
        qtd_total = 0
        col_inicio = self.coluna
        linha_inicio = self.linha
        tem_ponto = False

        while self.pos < len(self.fonte):
            c = self.fonte[self.pos]

            if c.isdigit():
                qtd_total += 1
                if len(lexeme) < LIMITE:
                    lexeme += c
                self.pos += 1
                self.coluna += 1

            elif c == '.' and not tem_ponto:
                # Ponto só válido se seguido de dígito
                prox = self._peek(1)
                if prox and prox.isdigit():
                    tem_ponto = True
                    qtd_total += 1
                    if len(lexeme) < LIMITE:
                        lexeme += c
                    self.pos += 1
                    self.coluna += 1
                else:
                    break

            elif c == 'E' and tem_ponto:
                # Parte exponencial: e<digits> | e+<digits> | e-<digits>
                prox = self._peek(1)
                if prox and (prox.isdigit() or prox in ('+', '-')):
                    qtd_total += 1
                    if len(lexeme) < LIMITE:
                        lexeme += c
                    self.pos += 1
                    self.coluna += 1
                    # sinal opcional
                    if self.pos < len(self.fonte) and self.fonte[self.pos] in ('+', '-'):
                        qtd_total += 1
                        if len(lexeme) < LIMITE:
                            lexeme += self.fonte[self.pos]
                        self.pos += 1
                        self.coluna += 1
                else:
                    break
            else:
                break

        # Garante que número truncado não termina em '.' ou 'E' ou sinal
        # (spec: "garantir que os números após truncar formarão construções válidas")
        lexeme = lexeme.rstrip('.').rstrip('E').rstrip('+-')

        codigo = "C07" if tem_ponto else "C06"
        qtd_depois_trunc = len(lexeme)
        return Token(lexeme, codigo, linha_inicio, col_inicio, -1,
                     qtd_total, qtd_depois_trunc)

    def _ler_string(self) -> Token:
        """stringConst: inicia e termina com aspas duplas."""
        col_inicio = self.coluna
        linha_inicio = self.linha
        lexeme = '"'
        qtd_total = 1       
        self.pos += 1
        self.coluna += 1

        while self.pos < len(self.fonte):
            c = self.fonte[self.pos]

            if c == '"':
                qtd_total += 1
                if len(lexeme) < LIMITE:
                    lexeme += c
                else:
                    # Forçar fechamento na posição 30 (spec)
                    lexeme = lexeme[:LIMITE - 1] + '"'
                self.pos += 1
                self.coluna += 1
                break

            if c in ('\n', '\r'):
                # String não fechada na linha — encerra
                break

            qtd_total += 1
            if len(lexeme) < LIMITE:
                lexeme += c
            self.pos += 1
            self.coluna += 1

        qtd_depois_trunc = len(lexeme)
        return Token(lexeme, "C04", linha_inicio, col_inicio, -1,
                     qtd_total, qtd_depois_trunc)

    def _ler_char(self) -> Token:
        """charConst: ' <letra> '  (exatamente uma letra entre aspas simples)."""
        col_inicio = self.coluna
        linha_inicio = self.linha
        lexeme = "'"
        qtd_total = 1       # aspas de abertura conta
        self.pos += 1
        self.coluna += 1

        if self.pos < len(self.fonte) and self.fonte[self.pos].isalpha():
            lexeme += self.fonte[self.pos]
            qtd_total += 1
            self.pos += 1
            self.coluna += 1

        if self.pos < len(self.fonte) and self.fonte[self.pos] == "'":
            lexeme += "'"
            qtd_total += 1
            self.pos += 1
            self.coluna += 1

        qtd_depois_trunc = len(lexeme)
        return Token(lexeme, "C05", linha_inicio, col_inicio, -1,
                     qtd_total, qtd_depois_trunc)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _pular_comentario_bloco(self):
        """/* ... */ — sem fechar, consome até EOF (spec permite)."""
        self.pos += 2
        self.coluna += 2
        while self.pos < len(self.fonte):
            c = self.fonte[self.pos]
            if c == '\n':
                self.linha += 1
                self.coluna = 1
            elif c == '*' and self._peek(1) == '/':
                self.pos += 2
                self.coluna += 2
                return
            self.pos += 1
            self.coluna += 1

    def _pular_comentario_linha(self):
        """// ... até \\n ou EOF."""
        self.pos += 2
        self.coluna += 2
        while self.pos < len(self.fonte) and self.fonte[self.pos] != '\n':
            self.pos += 1

    def _peek(self, offset: int) -> str | None:
        idx = self.pos + offset
        return self.fonte[idx] if idx < len(self.fonte) else None
