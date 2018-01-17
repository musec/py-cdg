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
    Call, Operand, Memory, Meta = range(4)


def create(name):
    graph = networkx.DiGraph(comment='Callgraph of %s' % name)
    hot_patch(graph)
    return graph


def dimensions(graph):
    return (len(graph.nodes()), len(graph.edges()))


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

    fns = cg['functions']
    for (fn_name, props) in fns.items():
        graph.add_node(fn_name)

        if 'attributes' in props:
            graph.node[fn_name].update(props['attributes'])

        if 'arguments' in props:
            for (name, attrs) in props['arguments'].items():
                graph.add_node(name, **attrs)

        if 'blocks' in props:
            for (block_name, values) in props['blocks'].items():
                graph.add_node(block_name)
                graph.nodes[block_name].update({'parent':fn_name})

                for (value_name, value_attrs) in values.items():
                    graph.add_node(value_name, **value_attrs)
                    graph.nodes[value_name].update({'parent':block_name})

        if 'calls' in props:
            calls = props['calls']
            if calls:
                for call in calls:
                    source = call['from']
                    dest = call['to']

                    target = fns[dest] if dest in fns else None
                    if target and 'arguments' in target:
                        for arg in target['arguments']:
                            graph.add_edge(source, arg, kind = EdgeKind.Call)

                    else:
                        graph.add_edge(source, dest, kind = EdgeKind.Call)

        if 'flows' in props:
            flows = props['flows']
            if flows:
                for flow in flows:
                    source = flow['from']
                    dest = flow['to']
                    k = flow['kind']

                    if k == 'memory':
                        kind = EdgeKind.Memory
                    elif k == 'meta':
                        kind = EdgeKind.Meta
                    elif k == 'operand':
                        kind = EdgeKind.Operand

                    graph.add_edge(source, dest, kind=kind)

    return graph


def hot_patch(graph):
    '''
    Bind new instance methods for converting, saving, etc.
    '''

    import cdg.simplify

    setattr(graph, 'dimensions', dimensions.__get__(graph, graph.__class__))
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

    functions = {}

    # Initialize functions to empty calls/flows tuple
    for (fn, attrs) in graph.nodes(data = True):
        functions[fn] = (set(), set(), attrs)

    for (source,dest,attrs) in graph.edges(data = True):
        (calls, flows, _) = functions[source]

        if is_call(attrs):
            functions[source][0].add(dest)

        elif is_flow(attrs):
            functions[dest][1].add(source)

        else:
            assert False   # invalid EdgeKind

    values = {
        'functions': dict([
            (name, {
                'attributes': attrs,
                'calls': list(calls),
                'flows': list(flows),
            })
            for (name, (calls, flows, attrs)) in functions.items()
        ])
    }

    ubjson.dump(values, output)
