
# Relatório - Busca Heurística (8-puzzle)

Alunos:
- Caio Cargnin Cardoso
- Diego Marzarotto

---

## Implementação


```python
import numpy as np
from eightpuzzle import Nodo, BuscaHeuristica8Puzzle, Interface
```

O programa consiste de um script python, que utiliza 3 classes ao  
realizar a busca A* para encontrar a solução do jogo 8-puzzle.

Além das bibliotecas nativas do python, o script usa também o *numpy*,  
portanto, antes de rodar o script é necessário instalar a biblioteca.  
Caso esteja usado o *pip* para gerenciar as dependências, basta rodar:

`sudo pip install -r requirements.txt`

Caso contrário, instale o pip antes. No Ubuntu basta executar:

`sudo apt-get install python-pip`

Para instruções em outros sistemas operacionais, consulte o google. :)  
Para utilizar o script, ele deve ser executado em um terminal. 

`./eightpuzzle.py`

Ao ser executado, o script apresenta a seguinte saída para o usuário,  
que deve então entrar com um estado válido do tabuleiro.  
Em seguida é mostrado o caminho até a solução:

```python
Interface().iniciar('h2', loop=False) # internamente o script executa isso, com loop=True
```

    
    ### 8-puzzle ###
    
    Entre com um estado do tabuleiro,
    com os números separados por espaços,
    representando o espaço vazio com um X:
    
    Ex: 1 2 3 4 5 6 7 8 X = equivalente a |1 2 3|
                                          |4 5 6|
                                          |7 8 X|
    
    
    > 1 2 3 4 5 6 7 X 8
    
    
    |1 2 3|
    |4 5 6|
    |7 X 8|
       |
       v
    |1 2 3|
    |4 5 6|
    |7 8 X|
    
    ## Número de nodos visitados: 2
    ## Maior quantidade de nodos na fronteira: 3
    ## Número de passos: 1
    ## Heurística utilizada: h2


---

Podem ser passadas as diferentes heurísticas implementadas como  parâmetros para o script.

`./eighpuzzle.py h1`  
`./eighpuzzle.py h2`  
`./eighpuzzle.py h3`  

---

A seguir, uma breve descrição das classes existentes,  
e o código de seus principais métodos:  

### Classe Nodo
---

Responsável por representar um estado do tabuleiro.

Esta classe também é capaz de gerar seus estados sucessores,  
além de saber determinar se é ou não um nodo objetivo.  
O cálculo do custo e das heurísticas também é responsabilidade do Nodo.

O cálculo do custo é representado através da função f:

- **f**: número de movimentos anteriores até se atingir o estado atual;

Três heurísticas distintas podem ser utilizadas:

- **h1**: número de peças fora do lugar;
- **h2**: distância manhattan de cada peça em relação ao seu lugar original;
- **h3**: média simples entre h1 e h2;

*Referência: Russel; Norvig, 2010*

---


```python
def f(self):
    '''Cálculo do custo, baseado na quantidade movimentos até se atingir o estado atual.'''
    custo = 0
    nodo = self
    while nodo.antecessor:
        custo += 1
        nodo = nodo.antecessor

    return custo
```


```python
def h1(self):
    '''Heurística baseada no número de peças fora do lugar.'''
    return np.sum(self.estado != self.SOLUCAO)
```


```python
def h2(self):
    '''Heurística baseada na distância manhattan de cada peça'''
    custo_estimado = 0
    for i in xrange(8):
        pos_ideal = np.array(divmod(i,3))
        pos_atual = self.posicao(i+1, self.estado)
        custo_estimado += self.distancia_manhattan(pos_ideal, pos_atual)

    return custo_estimado

def distancia_manhattan(self, pos1, pos2):
        return np.sum(np.abs(pos1 - pos2))
```


```python
def h3(self):
    '''Heurística baseada na média simples entre h1 e h2.'''
    return ( self.h1() + self.h2() ) / 2.0
```

### Classe BuscaHeuristica8Puzzle
---

Responsável por realizar a busca A* da solução para o jogo 8-puzzle.

Implementa a lógica de busca da solução para o jogo 8-puzzle,  
utilizando para isso o algoritmo A*, no qual utiliza-se uma  
heurística para estimar o custo de cada estado do tabuleiro  
em relação ao estado final do jogo.

*Referência: Russel; Norvig, 2010*

---


```python
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
```

### Classe Interface
---

Responsável por interagir com o usuário e apresentar o resultado da busca.

Além de mostrar o caminho percorrido até a solução,  
apresenta também o número de passos,  
o tamanho máximo da fronteira durante a busca  
e o número de nodos visitados até a solução.  

Os detalhes de implementação serão omitidos neste relatório,  
mas basta dizer que é possível apresentar o resultado completo  
da busca, com o caminho completo, ou apenas o resumo.

---

## Exemplos

**Um exemplo mínimo, utilizando a heurística h2, com dois passos de distância em relação ao objetivo:**

---


```python
busca = BuscaHeuristica8Puzzle(heuristica='h2')
nodo_final = busca.buscar(np.array([
    [1    , 2    , 3    ],
    [4    , 5    , 6    ],
    [None , 7    , 8    ]
]))
Interface().mostrar_solucao(busca, nodo_final)
```

    
    
    |1 2 3|
    |4 5 6|
    |X 7 8|
       |
       v
    |1 2 3|
    |4 5 6|
    |7 X 8|
       |
       v
    |1 2 3|
    |4 5 6|
    |7 8 X|
    
    ## Número de nodos visitados: 3
    ## Maior quantidade de nodos na fronteira: 3
    ## Número de passos: 2
    ## Heurística utilizada: h2


---

**Um exemplo maior, exemplificando a diferença entre as heurísticas:**

---


```python
busca = BuscaHeuristica8Puzzle(heuristica='h1')
nodo_final = busca.buscar(np.array([
    [1    , 2    , 3    ],
    [4    , 5    , None ],
    [6    , 7    , 8    ]
]))
Interface().mostrar_solucao(busca, nodo_final, resumido=True)
```

    
    
    
    ## Número de nodos visitados: 165
    ## Maior quantidade de nodos na fronteira: 105
    ## Número de passos: 13
    ## Heurística utilizada: h1



```python
busca = BuscaHeuristica8Puzzle(heuristica='h2')
nodo_final = busca.buscar(np.array([
    [1    , 2    , 3    ],
    [4    , 5    , None ],
    [6    , 7    , 8    ]
]))
Interface().mostrar_solucao(busca, nodo_final, resumido=True)
```

    
    
    
    ## Número de nodos visitados: 81
    ## Maior quantidade de nodos na fronteira: 56
    ## Número de passos: 13
    ## Heurística utilizada: h2



```python
busca = BuscaHeuristica8Puzzle(heuristica='h3')
nodo_final = busca.buscar(np.array([
    [1    , 2    , 3    ],
    [4    , 5    , None ],
    [6    , 7    , 8    ]
]))
Interface().mostrar_solucao(busca, nodo_final, resumido=True)
```

    
    
    
    ## Número de nodos visitados: 102
    ## Maior quantidade de nodos na fronteira: 64
    ## Número de passos: 13
    ## Heurística utilizada: h3


## Limitações

O exemplo com maior número de passos que conseguimos resolver foi  
com um estado distante 27 passos da solução, utilizando a heurística h2.  
Para estados mais distantes, o algoritmo não concluiu a busca em um tempo hábil.

As outras heurísticas não conseguiram executar uma busca com tantos passos.

---


```python
busca = BuscaHeuristica8Puzzle(heuristica='h2')
nodo_final = busca.buscar(np.array([
    [7    , 5    , 8    ],
    [2    , 3    , 4    ],
    [1    , None , 6    ]
]))
Interface().mostrar_solucao(busca, nodo_final)
```

    
    
    |7 5 8|
    |2 3 4|
    |1 X 6|
       |
       v
    |7 5 8|
    |2 3 4|
    |1 6 X|
       |
       v
    |7 5 8|
    |2 3 X|
    |1 6 4|
       |
       v
    |7 5 X|
    |2 3 8|
    |1 6 4|
       |
       v
    |7 X 5|
    |2 3 8|
    |1 6 4|
       |
       v
    |7 3 5|
    |2 X 8|
    |1 6 4|
       |
       v
    |7 3 5|
    |2 8 X|
    |1 6 4|
       |
       v
    |7 3 5|
    |2 8 4|
    |1 6 X|
       |
       v
    |7 3 5|
    |2 8 4|
    |1 X 6|
       |
       v
    |7 3 5|
    |2 X 4|
    |1 8 6|
       |
       v
    |7 3 5|
    |2 4 X|
    |1 8 6|
       |
       v
    |7 3 X|
    |2 4 5|
    |1 8 6|
       |
       v
    |7 X 3|
    |2 4 5|
    |1 8 6|
       |
       v
    |X 7 3|
    |2 4 5|
    |1 8 6|
       |
       v
    |2 7 3|
    |X 4 5|
    |1 8 6|
       |
       v
    |2 7 3|
    |1 4 5|
    |X 8 6|
       |
       v
    |2 7 3|
    |1 4 5|
    |8 X 6|
       |
       v
    |2 7 3|
    |1 X 5|
    |8 4 6|
       |
       v
    |2 X 3|
    |1 7 5|
    |8 4 6|
       |
       v
    |X 2 3|
    |1 7 5|
    |8 4 6|
       |
       v
    |1 2 3|
    |X 7 5|
    |8 4 6|
       |
       v
    |1 2 3|
    |7 X 5|
    |8 4 6|
       |
       v
    |1 2 3|
    |7 4 5|
    |8 X 6|
       |
       v
    |1 2 3|
    |7 4 5|
    |X 8 6|
       |
       v
    |1 2 3|
    |X 4 5|
    |7 8 6|
       |
       v
    |1 2 3|
    |4 X 5|
    |7 8 6|
       |
       v
    |1 2 3|
    |4 5 X|
    |7 8 6|
       |
       v
    |1 2 3|
    |4 5 6|
    |7 8 X|
    
    ## Número de nodos visitados: 4792
    ## Maior quantidade de nodos na fronteira: 2595
    ## Número de passos: 27
    ## Heurística utilizada: h2

