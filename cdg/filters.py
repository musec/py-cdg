#
# Copyright (c) 2017 Brian J. Kidney
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

import query

def successors_graph_by_generations(graph, node, generations):
    succ = []
    succ.append(node)

    succ.extend(query.successors_by_generations(graph, node, generations))

    return graph.subgraph(succ)


def predecessors_graph_by_generations(graph, node, generations):
    pre = []
    pre.append(node)

    pre.extend(query.predecessors_by_generations(graph, node, generations))

    return graph.subgraph(pre)


def intersection(G, H):
    R = G.copy()
    R.remove_nodes_from(n for n in G if n not in H)
    return R


def union(G, H):
    R = G.copy()
    R.add_edges_from(H.edges())
    return R
