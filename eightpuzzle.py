#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import sys
import heapq
import numpy as np
import argparse

class Nodo(object):
    """Responsável por representar um estado do tabuleiro.

    Esta classe também é capaz de gerar seus estados sucessores,
    além de saber determinar se é ou não um nodo objetivo.
    O cálculo do custo e das heurísticas também é responsabilidade do Nodo.

    O cálculo do custo é representado através da função f:

    - f: número de movimentos anteriores até se atingir o estado atual;

    Três heurísticas distintas podem ser utilizadas:

    - h1: número de peças fora do lugar;
    - h2: distância manhattan de cada peça em relação ao seu lugar original;
    - h3: média simples entre h1 e h2;

    Referência: Russel; Norvig, 2010
    """

    SOLUCAO = np.array([
        [1, 2, 3   ],
        [4, 5, 6   ],
        [7, 8, None]
    ])

    def __init__(self, estado, antecessor=None, heuristica='h2'):
        self.estado = estado
        self.antecessor = antecessor
        self.heuristica = heuristica

        if heuristica == 'h1':
            self.h = self.h1
        elif heuristica == 'h2':
            self.h = self.h2
        elif heuristica == 'h3':
            self.h = self.h3
        else:
            self.h = self.h2

        self.custo = self.f() + self.h()

    def distancia_manhattan(self, pos1, pos2):
        return np.sum(np.abs(pos1 - pos2))

    def f(self):
        '''Cálculo do custo, baseado na quantidade movimentos até se atingir o estado atual.'''
        custo = 0
        nodo = self
        while nodo.antecessor:
            custo += 1
            nodo = nodo.antecessor

        return custo

    def h1(self):
        '''Heurística baseada no número de peças fora do lugar.'''
        return np.sum(self.estado != self.SOLUCAO)

    def h2(self):
        '''Heurística baseada na distância manhattan de cada peça.'''
        custo_estimado = 0
        for i in xrange(8):
            pos_ideal = np.array(divmod(i,3))
            pos_atual = self.posicao(i+1, self.estado)
            custo_estimado += self.distancia_manhattan(pos_ideal, pos_atual)

        return custo_estimado

    def h3(self):
        '''Heurística baseada na média simples entre h1 e h2.'''
        return ( self.h1() + self.h2() ) / 2.0

    def objetivo(self):
        return (self.estado == self.SOLUCAO).all()

    def sucessor(self, x1, y1, x2, y2):
        clone_estado = self.estado.copy()
        clone_estado[x1, y1] = self.estado[x2, y2]
        clone_estado[x2, y2] = self.estado[x1, y1]
        return Nodo(clone_estado, self, heuristica=self.heuristica)

    def posicao(self, numero, estado):
        return np.array(map(lambda x: x[0], np.where(estado == numero)))

    def sucessores(self):
        x, y = map(lambda x: x[0], np.nonzero(self.estado < 1))
        sucessores = []

        if x > 0:
            sucessores.append(self.sucessor(x-1, y, x, y))
        if x < 2:
            sucessores.append(self.sucessor(x+1, y, x, y))
        if y > 0:
            sucessores.append(self.sucessor(x, y-1, x, y))
        if y < 2:
            sucessores.append(self.sucessor(x, y+1, x, y))

        return sucessores

    def __hash__(self):
        return hash(str(self.estado))

    def __eq__(self, o):
        return hash(str(self.estado)) == hash(str(o.estado))

    def __str__(self):
        return str(self.estado).replace('None', 'X')

    def __repr__(self):
        return str(self.estado).replace('None', 'X')

    def __cmp__(self, o):
        return cmp(self.custo, o.custo)


class BuscaHeuristica8Puzzle(object):
    '''Responsável por realizar a busca A* da solução para o jogo 8-puzzle.

    Implementa a lógica de busca da solução para o jogo 8-puzzle,
    utilizando para isso o algoritmo A*, no qual utiliza-se uma
    heurística para estimar o custo de cada estado do tabuleiro
    em relação ao estado final do jogo.

    Referência: Russel; Norvig, 2010
    '''

    def __init__(self, heuristica='h2'):
        self.heuristica = heuristica

    def num_visitados(self):
        return len(self.visitados)

    def buscar(self, estado_atual):
        '''Método responsável pela busca propriamente dita.

        Para armazenar os nodos presentes na fronteira, durante a busca,
        foi utilizada uma lista de prioridade, que apesar de ser uma lista simples do python,
        é manipulada utilizando a biblioteca 'heapq', nativa da linguagem,
        que permite que operações de inserção e remoção ('pop') mantenham
        as propriedades de ordenação da lista de prioridade.

        Dessa forma, garante-se que o próximo elemento a ser retirado
        através da operação "pop" seja o Nodo com menor custo estimado;

        Para auxiliar na verificação de Nodos já presentes na fronteira,
        é também utilizada uma tabela de hash ('dict' do python),
        na qual a chave é uma função hash baseada apenas no estado de cada Nodo.

        '''
        assert type(estado_atual) == np.ndarray, 'O estado deve ser representado por uma matriz numpy'
        assert estado_atual.shape == (3,3), 'A matriz de estados deve ser uma matriz 3x3'

        self.fronteira = list()
        self.dict_fronteira = dict()
        self.visitados = set()
        self.max_fronteira = 1

        nodo_atual = Nodo(estado_atual, antecessor=None, heuristica=self.heuristica)
        self.visitados.add(nodo_atual)

        while not nodo_atual.objetivo():

            for nodo in nodo_atual.sucessores():
                nodo_na_fronteira = self.dict_fronteira.get(hash(nodo))
                if not nodo_na_fronteira and (not nodo in self.visitados):
                    heapq.heappush(self.fronteira, nodo)
                    self.dict_fronteira[hash(nodo)] = nodo
                elif nodo_na_fronteira and nodo_na_fronteira.custo > nodo.custo:
                    self.fronteira.remove(nodo_na_fronteira)
                    heapq.heappush(self.fronteira, nodo)
                    self.dict_fronteira[hash(nodo)] = nodo

            if len(self.fronteira) > self.max_fronteira:
                self.max_fronteira = len(self.fronteira)

            if len(self.fronteira) > 0:
                nodo_atual = heapq.heappop(self.fronteira)
                del self.dict_fronteira[hash(nodo_atual)]
                self.visitados.add(nodo_atual)
            else:
                return null

        return nodo_atual


class Interface(object):
    '''Responsável por interagir com o usuário e apresentar o resultado da busca.

    Além de mostrar o caminho percorrido até a solução,
    apresenta também o número de passos,
    o tamanho máximo da fronteira durante a busca
    e o número de nodos visitados até a solução.
    '''


    def mostrar_solucao(self, busca, nodo_final, resumido=False):
        caminho = [nodo_final]
        nodo = nodo_final
        while nodo.antecessor:
            caminho.append(nodo.antecessor)
            nodo = nodo.antecessor

        print '\n'
        if not resumido:
            for i, n in enumerate(reversed(caminho)):
                print str(n).replace('[[', '|').replace(']]', '|').replace(' [', '|').replace(']', '|')
                if i != len(caminho) - 1:
                    print '   |\n   v'

        print '\n## Número de nodos visitados: %d' % busca.num_visitados()
        print '## Maior quantidade de nodos na fronteira: %d' % busca.max_fronteira
        print "## Número de passos: %d" % (len(caminho) - 1)
        print '## Heurística utilizada: %s' % busca.heuristica

    def iniciar(self, heuristica, loop=True):
        while True:
            print '\n### 8-puzzle ###\n'
            print 'Entre com um estado do tabuleiro,'
            print 'com os números separados por espaços,'
            print 'representando o espaço vazio com um X:\n'

            print 'Ex: 1 2 3 4 5 6 7 8 X = equivalente a |1 2 3|'
            print '                                      |4 5 6|'
            print '                                      |7 8 X|\n\n'

            self.entrada = raw_input('> ')

            try:

                entrada = str(self.entrada).split(' ')

                if len(entrada) < 9:
                    raise Exception("Número insuficente de posições")

                entrada = map(lambda e: int(e) if bool(re.search('[0-9]', e)) else None, entrada)
                entrada = np.array(entrada).reshape(3, 3)

                busca = BuscaHeuristica8Puzzle(heuristica=heuristica)
                nodo_final = busca.buscar(entrada)
                self.mostrar_solucao(busca, nodo_final)

                if not loop:
                    break

                raw_input("\nPressione enter para continuar...")
            except Exception as e:
                print '\nEstado inválido, tente novamente'
                raw_input("\nPressione enter para continuar...")
                continue


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('heuristica', nargs='?', default='h2', type=str)
        args = parser.parse_args()
        Interface().iniciar(args.heuristica)
    except KeyboardInterrupt:
        print "\nSaindo..."
        sys.exit(0)