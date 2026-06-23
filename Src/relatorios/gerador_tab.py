from tabela.tabela_simbolos import TabelaSimbolos


class GeradorRelatorioTAB:
    def __init__(self, codigo_equipe: str, componentes: list[dict]):
        """
        componentes: lista de dicts com chaves 'nome', 'email', 'telefone'
        """
        self.codigo_equipe = codigo_equipe
        self.componentes = componentes

    def gerar(self, caminho_saida: str, nome_fonte: str, tabela: TabelaSimbolos):
        """
        Gera o arquivo .TAB na mesma pasta do texto fonte
        """
        linhas = []

        # --- Cabeçalho obrigatório ---
        linhas.append(f"Código da Equipe: {self.codigo_equipe}")
        linhas.append("Componentes:")
        for c in self.componentes:
            linhas.append(f"  {c['nome']}; {c['email']}; {c['telefone']}")
        linhas.append("")
        linhas.append("RELATÓRIO DA TABELA DE SÍMBOLOS.")
        linhas.append(f"Texto fonte analisado: {nome_fonte}")
        linhas.append("")

        # --- Um bloco por símbolo ---
        for s in tabela.obter_todos():
            linhas_fmt = "(" + ", ".join(str(l) for l in s.linhas) + ")"
            linhas.append(
                f"Entrada: {s.indice}, Código: {s.codigo}, Lexeme: {s.lexeme},"
            )
            linhas.append(
                f"QtdCharsAntesTrunc: {s.qtd_antes_trunc}, "
                f"QtdCharDepoisTrunc: {s.qtd_depois_trunc},"
            )
            linhas.append(f"TipoSimb: {s.tipo}, Linhas: {linhas_fmt}.")
            linhas.append("-" * 64)

        with open(caminho_saida, "w", encoding="utf-8", errors="replace") as f:
            f.write("\n".join(linhas) + "\n")

        print(f"  → TAB gerado: {caminho_saida}")
