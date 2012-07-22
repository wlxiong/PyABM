import pygraphviz as pgv


class GNetwork(object):
    def __init__(self, net):
        self.G = pgv.AGraph()
        for edge in net.edges:
            self.G.add_edge(edge.head, edge.tail)
    
    def draw(self, filename):
        self.G.layout()
        self.G.draw(filename)
    
    