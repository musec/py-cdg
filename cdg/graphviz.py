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

import cdg
import collections
import networkx
import pygraphviz

class Colour:
    CallRoot = '#ffcc6699'
    CallTarget = '#99663399'

    FlowSource = '#99ccff99'
    FlowSink = '#cc666699'


def dot(graph, output):
    """
    Write GraphViz .dot representation of a graph.
    """

    nodes = graph.nodes

    def graph_name(name):
        """
        The final name of a graph node may be prefixed with 'cluster_' if the
        node is, in fact, a subgraph. This is a requirement for GraphViz layout
        algorithms that know how to draw subgraphs.
        """
        return 'cluster_' + name if 'children' in nodes[name] else name

    parents = dict([
        (name, { graph_name(c) for c in attrs['children'] })
            for (name,attrs) in nodes.items()
            if 'children' in attrs
    ])

    leaves = { n for n in nodes if n not in parents }

    #
    # We need to generate a pygraphviz object ourselves because NetworkX's
    # built-in pygraphviz support doesn't let us build hierarchies of subgraphs
    # within subgraphs.
    #
    pgv = pygraphviz.AGraph(directed=True)
    pgv.node_attr['shape'] = 'rectangle'
    pgv.node_attr['style'] = 'filled'

    # In order to display recursive clusters of nodes, we need to add all leaf
    # nodes (but no subgraph nodes) to the top-level graph.
    for name in leaves:
        pgv.add_node(name, **node_attrs(graph.nodes[name]))

    # Add subgraphs, starting from the root, using our hierarchical naming
    # system to ensure that we always generate a subgraph before its
    # sub-sub-graphs. 
    clusters = {}

    for name in sorted(parents, key=lambda name: len(name)):
        attrs = nodes[name]
        children = all_children(attrs, nodes)

        g = clusters[attrs['parent']] if 'parent' in attrs else pgv
        sub = g.add_subgraph(children, fillcolor='#66666611', label=name,
            name='cluster_'+name, style='filled')
        clusters[name] = sub

    for (src,dest,attrs) in graph.edges(data = True):
        pgv.add_edge(src, dest, **edge_attrs(attrs))

    pgv.write(output)


def all_children(node, nodes):
    """
    Recursively find all children of a graph node.
    """
    children = node['children']

    for c in children:
        child = nodes[c]
        if 'children' in child:
            children = children.union(all_children(child, nodes))

    return children


def edge_attrs(attrs):
    """
    Decorate a graph edge.
    """

    kind = attrs['kind']

    if kind == cdg.EdgeKind.Call:
        attrs['color'] = '#ff66ffff'

    elif kind == cdg.EdgeKind.Memory:
        attrs['color'] = '#ff666699'

    elif kind == cdg.EdgeKind.Meta:
        attrs['color'] = '#ff6666ff'

    elif kind == cdg.EdgeKind.Operand:
        attrs['color'] = '#66666633'

    else:
        assert False    # invalid EdgeKind

    return attrs


def node_attrs(attrs):
    """
    Decorate a graph node.
    """

    callend = attrs['call'] if 'call' in attrs else None
    flowend = attrs['flow'] if 'flow' in attrs else None

    target = (callend == 'target')
    root = (callend == 'root')
    source = (flowend == 'source')
    sink = (flowend == 'sink')

    # Colour:
    colours = []
    if root:
        colours.append(Colour.CallRoot)

    if target:
        colours.append(Colour.CallTarget)

    if source:
        colours.append(Colour.FlowSource)

    if sink:
        colours.append(Colour.FlowSink)

    if len(colours) == 0:
        attrs['fillcolor'] = '#66666633'

    elif len(colours) == 1:
        attrs['fillcolor'] = colours[0]

    else:
        weight = 1.0 / len(colours)
        attrs['fillcolor'] = ':'.join(
            [ '%s;%f' % (c, weight) for c in colours ])

    # Font:
    if root or target or sink or source:
        attrs['fontsize'] = 24

    # Shape:
    if sink or target:
        attrs['shape'] = 'doubleoctagon'

    elif source or root:
        attrs['shape'] = 'doublecircle'

    return attrs
