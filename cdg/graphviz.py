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


def dot(graph, output):
    pretty = graph.full_copy()
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
