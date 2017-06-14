import networkx

def load(stream, filename):
    if filename.endswith('.json'):
        import json
        cg = json.load(stream)

    elif filename.endswith('.yaml'):
        import yaml

        try: from yaml import CLoader as Loader
        except ImportError: from yaml import Loader

        cg = yaml.load(stream, Loader = Loader)

    else:
        raise ValueError, 'Unhandled file type: %s' % filename

    graph = networkx.DiGraph(comment = 'Callgraph of %s' % filename)

    for (name, props) in cg['functions'].items():
        graph.add_node(name)

        for (k,v) in props['attributes'] if 'attributes' in props else []:
            graph.node[k] = v

        for target in props['calls'] if 'calls' in props else []:
            graph.add_edge(name, target)

    return graph
