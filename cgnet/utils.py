
def get_roots( graph ):
    return [n for n,d in graph.in_degree().items() if d==0]

def get_leaves( graph ):
    return [n for n,d in graph.out_degree().items() if d==0]

