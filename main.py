#TRABALHO DE INTRODUÇÃO À TEORIA DA COMPUTAÇÃO - 8110/8111

class AFN:
    def __init__(self, estados, alfabeto, transicoes, estado_inicial, estados_aceitacao):
        self.estados = estados
        self.alfabeto = alfabeto
        self.transicoes = transicoes
        self.estado_inicial = estado_inicial
        self.estados_aceitacao = estados_aceitacao

class AFD:
    def __init__(self, estados, alfabeto, transicoes, estado_inicial, estados_aceitacao):
        self.estados = estados
        self.alfabeto = alfabeto
        self.transicoes = transicoes
        self.estado_inicial = estado_inicial
        self.estados_aceitacao = estados_aceitacao


# Conversor AFD ----> AFN

def afn_para_afd(afn):
    estado_inicial = frozenset([afn.estado_inicial])  # Estado inicial como frozenset para garantir imutabilidade
    estados = {estado_inicial}  # Conjunto de estados do AFD, iniciado com o estado inicial
    transicoes = {}  # Dicionário para armazenar as transições do AFD
    estados_aceitacao = set()  # Conjunto de estados de aceitação do AFD
    fila = [estado_inicial]  # Fila para processar estados

    while fila:
        atual = fila.pop(0)  # Estado atual a ser processado
        transicoes[atual] = {}  # Inicializa as transições para o estado atual

        for simbolo in afn.alfabeto:
            # Calcula o próximo estado para cada símbolo do alfabeto
            proximo_estado = frozenset(
                estado for subestado in atual 
                for estado in afn.transicoes.get(subestado, {}).get(simbolo, set())
            )

            if not proximo_estado:
                continue

            # Adiciona a transição para o estado atual
            transicoes[atual][simbolo] = proximo_estado
            if proximo_estado not in estados:
                estados.add(proximo_estado)  # Adiciona novo estado à lista de estados
                fila.append(proximo_estado)  # Adiciona estado à fila para processamento futuro
            if proximo_estado & afn.estados_aceitacao:
                estados_aceitacao.add(proximo_estado)  # Adiciona estado à aceitação se for um estado de aceitação

    return AFD(estados, afn.alfabeto, transicoes, estado_inicial, estados_aceitacao)
        

# Simulador 

def simular_afd(afd, palavra):
    estado_atual = afd.estado_inicial  # Estado inicial do AFD
    for simbolo in palavra:
        if simbolo in afd.transicoes[estado_atual]:
            estado_atual = afd.transicoes[estado_atual][simbolo]  # Transição para o próximo estado
        else:
            return False  # Retorna falso se o símbolo não é encontrado na transição
    return estado_atual in afd.estados_aceitacao  # Verifica se o estado final é de aceitação

def simular_afn(afn, palavra):
    estados_atuais = {afn.estado_inicial}  # Conjunto de estados atuais, iniciado com o estado inicial
    for simbolo in palavra:
        proximos_estados = set()  # Conjunto de próximos estados
        for estado in estados_atuais:
            proximos_estados.update(afn.transicoes.get(estado, {}).get(simbolo, set()))  # Atualiza próximos estados
        estados_atuais = proximos_estados
    return bool(estados_atuais & afn.estados_aceitacao)  # Verifica se algum dos estados atuais é de aceitação


# Equivalência

def testar_equivalencia(afn, afd):
    """
    Testa a equivalência entre um AFN e um AFD minimizado comparando as palavras aceitas por ambos.
    """
    # Definindo um conjunto de palavras representativas para teste
    palavras_teste = ['a', 'b', 'ab', 'ba', 'aa', 'bb', 'aab', 'bba', 'aaa', 'bbb']

    def testar_palavras():
        """
        Testa um conjunto de palavras e compara a aceitação entre AFN e AFD minimizado.
        """
        erros = []
        for palavra in palavras_teste:
            afn_aceita = simular_afn(afn, palavra)
            afd_aceita = simular_afd(afd, palavra)
            if afn_aceita != afd_aceita:
                erros.append((palavra, afn_aceita, afd_aceita))  # Adiciona erro se a aceitação não coincidir
        return erros

    erros = testar_palavras()
    if not erros:
        print("AFN e AFD minimizado aceitam as mesmas palavras.")
    else:
        print("Diferenças encontradas:")
        for palavra, afn_aceita, afd_aceita in erros:
            print(f"Palavra: {palavra} - AFN: {'Aceita' if afn_aceita else 'Não aceita'}, AFD: {'Aceita' if afd_aceita else 'Não aceita'}")


# Minimização

def minimizar_afd(afd):
    # Inicia a partição com estados de aceitação e não aceitação
    particao = [afd.estados_aceitacao, afd.estados - afd.estados_aceitacao]
    nova_particao = []

    def encontrar_bloco(estado, particao):
        """
        Encontra o bloco da partição ao qual um estado pertence.
        """
        for bloco in particao:
            if estado in bloco:
                return bloco
        return None

    while True:
        nova_particao = []
        for bloco in particao:
            blocos_divididos = {}
            for estado in bloco:
                # Cria uma chave para o estado baseada nos blocos de transição
                chave = tuple(
                    frozenset(encontrar_bloco(afd.transicoes[estado][simbolo], particao)) 
                    for simbolo in afd.alfabeto if simbolo in afd.transicoes[estado]
                )
                if chave not in blocos_divididos:
                    blocos_divididos[chave] = set()
                blocos_divididos[chave].add(estado)  # Adiciona estado ao bloco correspondente
            nova_particao.extend(blocos_divididos.values())  # Atualiza a nova partição
        
        # Se a partição não muda, o processo de minimização está completo
        if nova_particao == particao:
            break
        particao = nova_particao

    # Cria novos estados a partir dos blocos de partição
    novos_estados = {frozenset(bloco): f'S{indice}' for indice, bloco in enumerate(particao)}
    novo_estado_inicial = next(estado for bloco, estado in novos_estados.items() if afd.estado_inicial in bloco)
    novos_estados_aceitacao = {estado for bloco, estado in novos_estados.items() if bloco & afd.estados_aceitacao}
    novas_transicoes = {
        estado: {
            simbolo: novos_estados[frozenset(encontrar_bloco(afd.transicoes[next(iter(bloco))][simbolo], particao))]
            for simbolo in afd.alfabeto if simbolo in afd.transicoes[next(iter(bloco))]
        }
        for bloco, estado in novos_estados.items()
    }

    return AFD(set(novos_estados.values()), afd.alfabeto, novas_transicoes, novo_estado_inicial, novos_estados_aceitacao)


# FrontEnd

def main():
    # Entrada de dados do AFN
    estados = set(input("Estados do AFN (separados por vírgula): ").split(','))
    alfabeto = set(input("Alfabeto (separado por vírgula): ").split(','))
    transicoes = {}
    for estado in estados:
        transicoes[estado] = {}
        for simbolo in alfabeto:
            transicoes[estado][simbolo] = set(input(f"\t {simbolo}\n{estado}\t----->\t").split(','))
            if '' in transicoes[estado][simbolo]:
                transicoes[estado][simbolo].remove('')
    estado_inicial = input("Estado inicial: ")
    estados_aceitacao = set(input("Estados de aceitação (separados por vírgula): ").split(','))

    # Criação do AFN e conversão para AFD
    afn = AFN(estados, alfabeto, transicoes, estado_inicial, estados_aceitacao)
    afd = afn_para_afd(afn)
    afd_minimizado = minimizar_afd(afd)

    # Exibição do AFD convertido
    print("convertido para AFD:")
    print(f"Estados: {afd.estados}")
    print(f"Alfabeto: {afd.alfabeto}")
    print(f"Transições: {afd.transicoes}")
    print(f"Estado inicial: {afd.estado_inicial}")
    print(f"Estados de aceitação: {afd.estados_aceitacao}")

    # Exibição do AFD minimizado
    print("\nAFD minimizado:")
    print(f"Estados: {afd_minimizado.estados}")
    print(f"Alfabeto: {afd_minimizado.alfabeto}")
    print(f"Transições: {afd_minimizado.transicoes}")
    print(f"Estado inicial: {afd_minimizado.estado_inicial}")
    print(f"Estados de aceitação: {afd_minimizado.estados_aceitacao}")

    # Verificação de aceitação de palavras para AFN e AFD
    while True:
        palavra = input("Digite uma palavra para verificar (ou 'sair' para sair): ")
        if palavra == 'sair':
            break
        afn_aceita = simular_afn(afn, palavra)
        afd_aceita = simular_afd(afd_minimizado, palavra)
        print(f"A palavra '{palavra}' é aceita pelo AFN? {'Sim' if afn_aceita else 'Não'}")
        print(f"A palavra '{palavra}' é aceita pelo AFD minimizado? {'Sim' if afd_aceita else 'Não'}")
        
    # Teste de equivalência
    print("\nTeste de equivalência entre AFN e AFD minimizado:")
    testar_equivalencia(afn, afd_minimizado)

if __name__ == '__main__':
    main()

