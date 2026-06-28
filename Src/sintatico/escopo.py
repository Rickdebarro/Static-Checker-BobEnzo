from enum import Enum, auto


class NivelEscopo(Enum):
    FORA         = auto()  # antes de "program"
    PROGRAMA     = auto()  # dentro de program … endProgram
    DECLARACOES  = auto()  # dentro de declarations … endDeclarations
    FUNCOES      = auto()  # dentro de functions … endFunctions
    CORPO_FUNCAO = auto()  # dentro de funcType … endFunction


class ControladorEscopo:
    """
    Rastreia em qual bloco da linguagem o sintático está no momento.
    Isso permite ao main.py atribuir o código C correto a cada identificador
    
    """

    def __init__(self):
        self._pilha: list[NivelEscopo] = [NivelEscopo.FORA]
        self._aguardando_nome_funcao: bool = False

    @property
    def atual(self) -> NivelEscopo:
        return self._pilha[-1]

    def abrir(self, nivel: NivelEscopo):
        self._pilha.append(nivel)

    def fechar(self):
        if len(self._pilha) > 1:
            self._pilha.pop()

    def esta_em(self, nivel: NivelEscopo) -> bool:
        return self.atual == nivel

    def codigo_para_identificador(self, codigo_token_anterior: str | None) -> str:
        """
        Decide o código C do identificador com base no escopo e no token anterior, um pouco de base no apêndice b, para decidir entre ProgramName, FunctionName e VariableName.
        """
        # Logo após "program" viria o nome do programa
        if codigo_token_anterior == "A19":
            return "C03"

        # Primeiro identificador após "funcType <tipo> :" → nome da função
        if self._aguardando_nome_funcao:
            self._aguardando_nome_funcao = False
            return "C02"

        return "C01"  # variable — caso geral

    def sinalizar_functype(self):
        """Chamado pelo main quando encontra o token funcType (A14)."""
        self._aguardando_nome_funcao = True

    def __str__(self):
        return " > ".join(e.name for e in self._pilha)
