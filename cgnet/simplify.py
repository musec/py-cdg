import networkx as nx

def is_simple_node( graph, node ):
    """A node is "Simple" if none of the following is true
    - it has multiple inputs (it joins chains together)
    - it has no inputs (it's a root node)
    - it has multiple outputs (it splits chains apart)
    - it has no outputs (it's a leaf node)

    Keyword arguments:
    node -- A networkx DiGraph Node
    """
    return graph.in_degree(node) == 1 \
            and graph.out_degree(node)  == 1

def simplify_graph( graph ):
    """Simplify a CallGraph by collapsing call chains and dropping
    any unreferenced calls.

    Keyword arguments:
    graph -- A networkx DiGraph
    """

    g = graph.copy()

    for n in graph:
        if is_simple_node(graph, n):
            pre = graph.predecessors(n)[0]
            suc = graph.successors(n)[0]
            g.add_edge(pre, suc)
            g.remove_node(n)

    return g
