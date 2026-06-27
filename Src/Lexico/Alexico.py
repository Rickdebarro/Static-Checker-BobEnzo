from .token import Token
from .tabela_reservados import TabelaPalavrasReservadas

LIMITE = 30  # spec: máximo de 30 caracteres válidos por átomo


def _eh_valido(c: str) -> bool:
    """Caracteres válidos da linguagem fora de strings/comentários."""
    return c.isalnum() or c in " \t\n\r_.,;:=?()[]{}+-*/%<>!#\"'"


def _eh_valido_miolo_cadeia(c: str) -> bool:
    """
    Apêndice C — <miolo-cadeia>:
    Aceita APENAS: letra | branco | dígito | $ | _ | .
    Tudo o mais (parênteses, vírgula, operadores, etc.) termina a string.
    """
    return c.isalpha() or c.isdigit() or c in ' \t$_.'


def _eh_valido_identificador(c: str) -> bool:
    """
    Apêndice C — <variable>:
    letra | dígito | _
    """
    return c.isalnum() or c == '_'


def _eh_valido_nome(c: str) -> bool:
    """
    Apêndice C — <programName> e <functionName>:
    letra | dígito  (SEM underscore — diferente de variable)
    """
    return c.isalnum()


class Alexico:
    def __init__(self, conteudo: str, tabela_reservada: TabelaPalavrasReservadas):
        self.fonte = conteudo.upper()  # spec: case-insensitive → tudo maiúsculo
        self.tabela_reservada = tabela_reservada
        self.pos = 0
        self.linha = 1
        self.coluna = 1

    # ------------------------------------------------------------------
    # Interface pública — o sintático chama UMA VEZ por token
    # ------------------------------------------------------------------
    def obter_proximo_token(self) -> Token | None:
        while self.pos < len(self.fonte):
            c = self.fonte[self.pos]

            # Quebras de linha
            if c == '\n':
                self.linha += 1
                self.coluna = 1
                self.pos += 1
                continue
            if c == '\r':
                self.pos += 1
                continue

            # Espaços e tabs — delimitadores
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
        """
        Apêndice C:
          <variable>     ::= <letra> | _ | <variable><letra> | <variable><digito> | <variable>_
          <programName>  ::= <letra> | <programName><letra> | <programName><digito>
          <functionName> ::= <letra> | <functionName><letra> | <functionName><digito>
        
        """
        lexeme = ""
        qtd_total = 0
        col_inicio = self.coluna
        linha_inicio = self.linha

        while self.pos < len(self.fonte):
            c = self.fonte[self.pos]

            if _eh_valido_identificador(c):
                # letra, dígito ou _ — válido para variable
                qtd_total += 1
                if len(lexeme) < LIMITE:
                    lexeme += c
                self.pos += 1
                self.coluna += 1

            elif not _eh_valido(c):
                # Filtro de 1º nível dentro do átomo
                self.pos += 1
                self.coluna += 1

            else:
                break  # delimitador legítimo

        qtd_depois_trunc = len(lexeme)

        if self.tabela_reservada.contem(lexeme):
            return Token(
                lexeme,
                self.tabela_reservada.get_codigo(lexeme),
                linha_inicio, col_inicio, -1,
                qtd_total, qtd_depois_trunc,
            )

        return Token(
            lexeme, "C01",
            linha_inicio, col_inicio, -1,
            qtd_total, qtd_depois_trunc,
        )

    def _ler_numero(self) -> Token:
        """
        Apêndice C:
          <intConst>  ::= <digitos-decimal>
          <realConst> ::= <digitos-decimal> . <digitos-decimal>
                        | <digitos-decimal> . <digitos-decimal> <parte-exponencial>
          <parte-exponencial> ::= e<digitos> | e-<digitos> | e+<digitos>
        """
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
                    break  # ponto sozinho = delimitador

            elif c == 'E' and tem_ponto:
                # Parte exponencial APENAS em realConst
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
                    # dígitos obrigatórios após e/e+/e-
                    if not (self.pos < len(self.fonte) and self.fonte[self.pos].isdigit()):
                        # sem dígitos após e → volta atrás, encerra antes do e
                        lexeme = lexeme.rstrip('E').rstrip('+-')
                        break
                else:
                    break
            else:
                break

        # Garante que número truncado não termina em '.', 'E' ou sinal
        lexeme = lexeme.rstrip('.').rstrip('E').rstrip('+-')

        codigo = "C07" if tem_ponto else "C06"
        qtd_depois_trunc = len(lexeme)
        return Token(lexeme, codigo, linha_inicio, col_inicio, -1,
                     qtd_total, qtd_depois_trunc)

    def _ler_string(self) -> Token:
        """
        Apêndice C:
          <stringConst> ::= '"' <miolo-cadeia> '"'
          <miolo-cadeia> aceita APENAS: letra | branco | dígito | $ | _ | .
        """
        col_inicio = self.coluna
        linha_inicio = self.linha
        lexeme = '"'
        qtd_total = 1       # aspa de abertura conta
        truncado = False
        self.pos += 1
        self.coluna += 1

        while self.pos < len(self.fonte):
            c = self.fonte[self.pos]

            # Fechamento normal com aspa dupla
            if c == '"':
                qtd_total += 1
                if not truncado:
                    if len(lexeme) < LIMITE:
                        lexeme += c
                    else:
                        lexeme = lexeme[:LIMITE - 1] + '"'
                self.pos += 1
                self.coluna += 1
                break

            # Quebra de linha — encerra string sem fechar
            if c in ('\n', '\r'):
                break

            # Caractere INVÁLIDO para o miolo
            if not _eh_valido_miolo_cadeia(c):
                break

            # Caractere válido do miolo
            qtd_total += 1
            if not truncado:
                if len(lexeme) < LIMITE - 1:
                    lexeme += c
                else:
                    lexeme = lexeme[:LIMITE - 1] + '"'
                    truncado = True

            self.pos += 1
            self.coluna += 1

        qtd_depois_trunc = len(lexeme)
        return Token(lexeme, "C04", linha_inicio, col_inicio, -1,
                     qtd_total, qtd_depois_trunc)

    def _ler_char(self) -> Token:
        """
        Apêndice C:
          <charConst> ::= "'" <letra> "'"
        """
        col_inicio = self.coluna
        linha_inicio = self.linha
        lexeme = "'"
        qtd_total = 1
        self.pos += 1
        self.coluna += 1

        # Consome exatamente uma letra
        if self.pos < len(self.fonte) and self.fonte[self.pos].isalpha():
            lexeme += self.fonte[self.pos]
            qtd_total += 1
            self.pos += 1
            self.coluna += 1

        # Consome a aspa de fechamento
        if self.pos < len(self.fonte) and self.fonte[self.pos] == "'":
            lexeme += "'"
            qtd_total += 1
            self.pos += 1
            self.coluna += 1

        qtd_depois_trunc = len(lexeme)
        return Token(lexeme, "C05", linha_inicio, col_inicio, -1,
                     qtd_total, qtd_depois_trunc)

    # ------------------------------------------------------------------
    # Helpers de comentário
    # ------------------------------------------------------------------

    def _pular_comentario_bloco(self):
        """/* ... */ — sem fechar, consome até EOF."""
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
