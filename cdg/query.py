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


class _Direction:
    Successors, Predecessors = range(2)


def get_roots(graph):
    return [n for n, d in graph.in_degree().items() if d == 0]


def get_leaves(graph):
    return [n for n, d in graph.out_degree().items() if d == 0]


def successors_by_generations(graph, node, generations):
    return _neighbours_by_generations(graph, node, generations,
                                      _Direction.Successors)


def predecessors_by_generations(graph, node, generations):
    return _neighbours_by_generations(graph, node, generations,
                                      _Direction.Predecessors)


def _neighbours_by_generations(graph, node, generations, direction):
    neighbours = []
    current_gen = []
    current_gen.append(node)

    for x in range(0, generations):
        next_gen = []
        for y in current_gen:
            s = []
            if direction == _Direction.Successors:
                s = graph.successors(y)
            elif direction == _Direction.Predecessors:
                s = graph.predecessors(y)
            neighbours.extend(s)
            next_gen.extend(s)
        current_gen = next_gen

    return neighbours
