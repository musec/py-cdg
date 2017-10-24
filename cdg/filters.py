#
# Copyright (c) 2017 Brian J. Kidney
# Copyright (c) 2017 Jonathan Anderson
# All rights reserved.
#
# This software was developed by BAE Systems, the University of Cambridge
# Computer Laboratory, and Memorial University under DARPA/AFRL contract
# FA8650-15-C-7558 ("CADETS"), as part of the DARPA Transparent Computing
# (TC) research program.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import cdg.query


def apply(filter_spec, graph):
    '''
    Apply a filter like pred:read,write or succ:main to a graph.
    '''

    (name, arg) = filter_spec.split(':')

    if name == 'pred':
        to_keep = arg.split(',')
        return predecessors(graph, to_keep)

    elif name == 'succ':
        to_keep = arg.split(',')
        return successors(graph, to_keep)


def predecessors(graph, to_keep):
    leaves = cdg.query.get_leaves(graph)
    keep = set(to_keep).intersection(leaves)

    result = cdg.create('Filtered graph')

    for leaf in keep:
        g = predecessors_graph_by_generations(graph, leaf, 100)
        print('Keeping %d predecessors of %s' % (len(g.nodes()), leaf))

        # Calculate non-disjoint union:
        for n in g.nodes():
            result.add_node(n)
        for e in g.edges():
            result.add_edge(*e)

    return result


def successors(graph, to_keep):
    roots = cdg.query.get_roots(graph)
    keep = set(to_keep).intersection(roots)

    result = cdg.create('Filtered graph')

    for root in keep:
        g = successors_graph_by_generations(graph, root, 100)
        print('Keeping %d successors of %s' % (len(g.nodes()), root))

        # Calculate non-disjoint union:
        for n in g.nodes():
            result.add_node(n)
        for e in g.edges():
            result.add_edge(*e)

    return result


def successors_graph_by_generations(graph, node, generations):
    succ = []
    succ.append(node)

    succ.extend(cdg.query.successors_by_generations(graph, node, generations))

    return graph.subgraph(succ)


def predecessors_graph_by_generations(graph, node, generations):
    pre = []
    pre.append(node)

    pre.extend(cdg.query.predecessors_by_generations(graph, node, generations))

    return graph.subgraph(pre)


def intersection(G, H):
    R = G.full_copy()
    R.remove_nodes_from(n for n in G if n not in H)
    return R


def union(G, H):
    R = G.full_copy()
    R.add_edges_from(H.edges())
    return R
