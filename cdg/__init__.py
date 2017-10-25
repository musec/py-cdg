# Copyright 2017 Jonathan Anderson
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import cdg.graphviz
import networkx


class EdgeKind:
    Call, Flow = range(2)


def create(name):
    graph = networkx.DiGraph(comment='Callgraph of %s' % name)
    hot_patch(graph)
    return graph


def load(stream, filename):
    if filename.endswith('.cdg'):
        import ubjson
        cg = ubjson.load(stream)

    elif filename.endswith('.json'):
        import json
        cg = json.load(stream)

    elif filename.endswith('.yaml'):
        import yaml

        try:
            from yaml import CLoader as Loader
        except ImportError:
            from yaml import Loader

        cg = yaml.load(stream, Loader=Loader)

    else:
        raise ValueError('Unhandled file type: %s' % filename)

    graph = create(filename)

    for (name, props) in cg['functions'].items():
        graph.add_node(name)

        for (k, v) in props['attributes'] if 'attributes' in props else []:
            graph.node[k] = v

        if 'calls' in props:
            calls = props['calls']
            if calls:
                for target in calls:
                    graph.add_edge(name, target, kind = EdgeKind.Call)

        if 'flows' in props:
            flows = props['flows']
            if flows:
                for source in flows:
                    graph.add_edge(source, name, kind = EdgeKind.Flow)

    return graph


def hot_patch(graph):
    '''
    Bind new instance methods for converting, saving, etc.
    '''

    import cdg.simplify

    setattr(graph, 'save', save.__get__(graph, graph.__class__))
    setattr(graph, 'simplified',
            simplify.simplified.__get__(graph, graph.__class__))
    setattr(graph, 'to_dot', cdg.graphviz.dot.__get__(graph, graph.__class__))

    def full_copy(g):
        c = g.copy()
        hot_patch(c)
        return c

    setattr(graph, 'full_copy', full_copy.__get__(graph, graph.__class__))

    return graph


def is_call(attrs):
    return attrs['kind'] == EdgeKind.Call


def is_flow(attrs):
    return attrs['kind'] == EdgeKind.Flow


def save(graph, output):
    import ubjson

    calls = {}

    for fn in graph.nodes():
        calls[fn] = set()

    for (source, dest) in graph.edges():
        calls[source].add(dest)

    values = {
        'functions': dict([
            (source, {'calls': list(dests)})
            for (source, dests) in calls.items()
        ])
    }

    ubjson.dump(values, output)
