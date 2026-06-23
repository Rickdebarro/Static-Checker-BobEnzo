from lexico.token import Token


class GeradorRelatorioLEX:
    def __init__(self, codigo_equipe: str, componentes: list[dict]):
        """
        componentes: lista de dicts com chaves 'nome', 'email', 'telefone'
        """
        self.codigo_equipe = codigo_equipe
        self.componentes = componentes

    def gerar(self, caminho_saida: str, nome_fonte: str, tokens: list[Token]):
        """
        Gera o arquivo .LEX na mesma pasta do texto fonte
        """
        linhas = []

        # --- Cabeçalho obrigatório ---
        linhas.append(f"Código da Equipe: {self.codigo_equipe}")
        linhas.append("Componentes:")
        for c in self.componentes:
            linhas.append(f"  {c['nome']}; {c['email']}; {c['telefone']}")
        linhas.append("")
        linhas.append("RELATÓRIO DA ANÁLISE LÉXICA.")
        linhas.append(f"Texto fonte analisado: {nome_fonte}")
        linhas.append("")

        # --- Uma linha por token, na ordem em que apareceram ---
        for tok in tokens:
            idx = tok.indice_tab if tok.indice_tab != -1 else "-"
            linhas.append(
                f"Lexeme: {tok.lexeme}, "
                f"Código: {tok.codigo}, "
                f"indiceTabSimb: {idx}, "
                f"Linha: {tok.linha}."
            )

        with open(caminho_saida, "w", encoding="utf-8", errors="replace") as f:
            f.write("\n".join(linhas) + "\n")

        print(f"  → LEX gerado: {caminho_saida}")
