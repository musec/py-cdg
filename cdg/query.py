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


def pred(graph, node, attribute_predicate):
    nodes = set(graph.predecessors(node))

    return (
        src for (src,dest,attrs) in graph.edges(nodes, data = True)
        if dest == node and attribute_predicate(attrs)
    )


def succ(graph, node, attribute_predicate):
    return (
        dest for (src,dest,attrs) in graph.edges(node, data = True)
        if src == node and attribute_predicate(attrs)
    )


def transitive_neighbours(graph, starting_nodes, select_fn, annotations=None,
                          depth_limit=None):
    result = set()
    seen = set()
    working_set = set(starting_nodes).intersection(graph.nodes)

    if annotations:
        for node in working_set:
            graph.nodes[node].update(annotations)

    depth = 0
    while True:
        next_gen = set()

        for node in working_set:
            if node not in graph.nodes:
                continue

            result.add(node)
            seen.add(node)

            selected = set(select_fn(node))

            # Don't recurse down paths that we've previously explored
            if seen.intersection(selected) == selected:
                continue

            seen = seen.union(selected)
            result = result.union(selected)
            next_gen = next_gen.union(selected)

        working_set = next_gen
        if len(working_set) == 0:
            break

        if depth_limit:
            depth += 1
            if depth >= depth_limit:
                break

    return result
