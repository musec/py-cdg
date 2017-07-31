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

import networkx as nx


def is_simple_node(graph, node):
    """A node is "Simple" if none of the following is true
    - it has multiple inputs (it joins chains together)
    - it has no inputs (it's a root node)
    - it has multiple outputs (it splits chains apart)
    - it has no outputs (it's a leaf node)

    Keyword arguments:
    node -- A networkx DiGraph Node
    """
    return graph.in_degree(node) == 1 and graph.out_degree(node) == 1


def simplified(graph):
    """Simplify a CallGraph by coalescing call chains and dropping
    any unreferenced calls.

    Keyword arguments:
    graph -- A networkx DiGraph
    """

    g = graph.copy()

    for n in graph:
        if is_simple_node(graph, n):
            pre = g.predecessors(n)[0]
            suc = g.successors(n)[0]
            g.add_edge(pre, suc)
            g.remove_node(n)

    return g
