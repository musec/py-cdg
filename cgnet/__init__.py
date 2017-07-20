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

import networkx


def load(stream, filename):
    if filename.endswith('.json'):
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
        raise ValueError, 'Unhandled file type: %s' % filename

    graph = networkx.DiGraph(comment='Callgraph of %s' % filename)

    for (name, props) in cg['functions'].items():
        graph.add_node(name)

        for (k, v) in props['attributes'] if 'attributes' in props else []:
            graph.node[k] = v

        for target in props['calls'] if 'calls' in props else []:
            graph.add_edge(name, target)

    # Bind the `to_dot` function to this graph as an instance method
    setattr(graph, 'to_dot', to_dot.__get__(graph, graph.__class__))

    return graph


def to_dot(graph, output):
    agraph = networkx.to_agraph(graph)
    agraph.node_attr['shape'] = 'rectangle'
    agraph.node_attr['style'] = 'filled'
    agraph.write(output)
