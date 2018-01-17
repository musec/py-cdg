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

    @classmethod
    def from_str(cls, name):
        if name == 'call':
            return EdgeKind.Call
        elif name == 'memory':
            return EdgeKind.Memory
        elif name == 'meta':
            return EdgeKind.Meta
        elif name == 'operand':
            return EdgeKind.Operand

    def to_str(self):
        if self == EdgeKind.Call:
            return 'call'
        elif self == EdgeKind.Memory:
            return 'memory'
        elif self == EdgeKind.Meta:
            return 'meta'
        elif self == EdgeKind.Operand:
            return 'operand'


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
        graph.add_node(fn_name, children=set())

        if 'attributes' in props:
            graph.node[fn_name].update(props['attributes'])

        if 'arguments' in props:
            for (name, attrs) in props['arguments'].items():
                graph.add_node(name, parent=fn_name, **attrs)
                graph.nodes[fn_name]['children'].add(name)

        if 'blocks' in props:
            for (block_name, values) in props['blocks'].items():
                graph.add_node(block_name, parent=fn_name, children=set())
                graph.nodes[fn_name]['children'].add(block_name)
                graph.nodes[block_name]['children'] = set(values)

                for (value_name, value_attrs) in values.items():
                    graph.add_node(value_name, parent=block_name, **value_attrs)

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
                    kind = EdgeKind.from_str(flow['kind'])

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


def save(graph, output):
    nodes = graph.nodes
    roots = ( (k,v) for (k,v) in graph.nodes.items() if 'parent' not in v )

    functions = {}
    for (fn_name, fn_attrs) in roots:
        if 'children' not in fn_attrs:
            continue

        fn = {
            'arguments': dict(),
            'attributes': dict(),
            'blocks': dict(),
            'calls': list(),
            'flows': list(),
        }

        # Blocks have children; anything else must be an argument.
        child_names = set(fn_attrs['children'])
        blocks = { n for n in child_names if 'children' in nodes[n] }
        args = child_names.difference(blocks)

        for block_name in blocks:
            block_attrs = nodes[block_name]
            block = fn['blocks'][block_name] = dict([
                (k,v) for (k,v) in nodes[block_name].items()
                if k not in ('parent', 'children')
            ])

            for child_name in block_attrs['children']:
                child_attrs = nodes[child_name]
                child_attrs.pop('parent')
                assert 'children' not in child_attrs

                block[child_name] = child_attrs

        for arg_name in args:
            arg_attrs = nodes[arg_name]
            arg_attrs.pop('parent')
            assert 'children' not in arg_attrs

            fn['arguments'][arg_name] = dict(arg_attrs)

        functions[fn_name] = fn

    for (src, dest, data) in graph.edges(data=True):
        (fn_name, src_name) = src.split('::', 1)
        kind = data['kind']

        data = {
            'from': src,
            'to': dest,
            'kind': EdgeKind.to_str(kind),
        }

        if kind == EdgeKind.Call:
            functions[fn_name]['calls'].append(data)
        else:
            functions[fn_name]['flows'].append(data)

    import ubjson
    ubjson.dump({'functions': functions}, output)
