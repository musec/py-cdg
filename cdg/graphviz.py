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
import networkx

class Colour:
    CallRoot = '#ffcc6699'
    CallTarget = '#99663399'

    FlowSource = '#99ccff99'
    FlowSink = '#cc666699'


def dot(graph, output):
    pretty = graph.full_copy()

    for (node, attrs) in pretty.nodes(data = True):
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
            attrs['fillcolor'] = '#cccccc66'

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


    for (src,dest,attrs) in pretty.edges(data = True):
        kind = attrs['kind']

        if kind == cdg.EdgeKind.Call:
            attrs['color'] = '#66666699'

        elif kind == cdg.EdgeKind.Flow:
            attrs['color'] = '#ff666699'

        else:
            assert False    # invalid EdgeKind

    agraph = networkx.drawing.nx_agraph.to_agraph(pretty)
    agraph.node_attr['shape'] = 'rectangle'
    agraph.node_attr['style'] = 'filled'
    agraph.write(output)
