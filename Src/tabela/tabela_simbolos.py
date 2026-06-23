from .simbolo import Simbolo


class TabelaSimbolos:
    def __init__(self):
        # chave: lexeme já em maiúsculo e truncado
        self._simbolos: dict[str, Simbolo] = {}
        self._contador: int = 0

    def inserir_ou_atualizar(
        self,
        lexeme: str,
        codigo: str,
        qtd_antes_trunc: int,
        qtd_depois_trunc: int,
        linha: int,
    ) -> int:
        """
        Se o símbolo já existe: adiciona a linha e atualiza qtd_antes_trunc
        se o novo valor for maior

        Retorna o índice do símbolo na tabela.
        """
        if lexeme in self._simbolos:
            s = self._simbolos[lexeme]
            s.adicionar_linha(linha)
            if qtd_antes_trunc > s.qtd_antes_trunc:
                s.qtd_antes_trunc = qtd_antes_trunc
            return s.indice

        self._contador += 1
        novo = Simbolo(
            indice=self._contador,
            lexeme=lexeme,
            codigo=codigo,
            qtd_antes_trunc=qtd_antes_trunc,
            qtd_depois_trunc=qtd_depois_trunc,
        )
        novo.adicionar_linha(linha)
        self._simbolos[lexeme] = novo
        return novo.indice

    def buscar(self, lexeme: str) -> Simbolo | None:
        return self._simbolos.get(lexeme)

    def obter_todos(self) -> list[Simbolo]:
        """Retorna símbolos ordenados pelo índice de inserção."""
        return sorted(self._simbolos.values(), key=lambda s: s.indice)

    def __len__(self) -> int:
        return self._contador
