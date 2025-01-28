import networkx as nx
import matplotlib.pyplot as plt

class Node:
    graph = nx.DiGraph()  # Grafo compartilhado entre todas as instâncias

    def __init__(self, name):
        self.name = name
        Node.graph.add_node(self.name)  # Adiciona o nó ao grafo

    def connect(self, other):
        """Conecta este nó a outro nó."""
        if isinstance(other, Node):
            Node.graph.add_edge(self.name, other.name)  # Cria a aresta no grafo
        else:
            raise TypeError("A conexão deve ser feita com outro objeto Node.")

    @classmethod
    def plot_graph(cls):
        """Plota o grafo atual."""
        plt.figure(figsize=(10, 7))
        nx.draw(cls.graph, with_labels=True, node_color="lightblue", font_size=10, font_weight="bold", node_size=2000)
        plt.show()

# Criação dos nós
node_a = Node("A")
node_b = Node("B")
node_c = Node("C")

# Criação das conexões
node_a.connect(node_b)
node_b.connect(node_c)
node_c.connect(node_a)

# Plotando o grafo
Node.plot_graph()
