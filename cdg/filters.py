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


class FilterError(Exception):
    """Raised when an error is encountered filtering a graph.

    Attributes:
        filter_spec       User-provided filter specification
        message           Explanation
    """

    def __init__(self, filter_spec, message):
        self.filter_spec = filter_spec
        self.message = message


def apply(filter_spec, graph):
    '''
    Apply a filter like calls-to:read,write or flows-from:main to a graph.
    '''

    tokens = filter_spec.split(':')
    name = tokens[0]
    args = tokens[1].split(',')
    depth_limit = int(tokens[2]) if len(tokens) > 2 else None

    def get_neighbours(select_fn, **annotations):
        return cdg.query.transitive_neighbours(graph, args, select_fn,
                                               annotations, depth_limit)

    if name == 'identity':
        return graph

    elif name == 'exclude':
        return exclude(graph, args)

    elif name == 'calls-from':
        select_fn = lambda node: cdg.query.succ(graph, node, cdg.is_call)
        nodes = get_neighbours(select_fn, call='root')

        print('Keeping %d successors of %d nodes' % (len(nodes), len(args)))

    elif name == 'calls-to':
        select_fn = lambda node: cdg.query.pred(graph, node, cdg.is_call)
        nodes = get_neighbours(select_fn, call='target')

        print('Keeping %d predecessors of %d nodes' % (len(nodes), len(args)))

    elif name == 'flows-from':
        select_fn = lambda node: cdg.query.succ(graph, node, lambda _: True)
        nodes = get_neighbours(select_fn, flow='source')

        print('Keeping %d successors of %d nodes' % (len(nodes), len(args)))

    elif name == 'flows-to':
        select_fn = lambda node: cdg.query.pred(graph, node, lambda _: True)
        nodes = get_neighbours(select_fn, flow='sink')

        print('Keeping %d predecessors of %d nodes' % (len(nodes), len(args)))

    else:
        raise FilterError(filter_spec, 'Invalid filter')

    return cdg.hot_patch(graph.subgraph(nodes))


def exclude(graph, to_exclude):
    result = graph.full_copy()

    for n in to_exclude:
        result.remove_node(n)

    print('Removed %d nodes, %d edges' % (
        len(graph.nodes) - len(result.nodes),
        len(graph.edges) - len(result.edges),
    ))

    return result


def intersection(G, H):
    R = G.full_copy()
    R.remove_nodes_from(n for n in G if n not in H)
    return R


def union(G, H):
    R = G.full_copy()
    R.add_edges_from(H.edges())
    return R
