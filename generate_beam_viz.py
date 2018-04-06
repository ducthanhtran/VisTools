#! /usr/bin/env python
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# Modified by Alexander Rush, 2007
# Modified by Gabriel Bretschner, 2018

""" Generate beam search visualization.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import os
import json
import shutil
import logging
from string import Template
import html

import networkx as nx
from networkx.readwrite import json_graph

logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format='[%(levelname)s:generate_beam_viz] %(message)s', level=logging.INFO)

PARSER = argparse.ArgumentParser(
    description="Generate beam search visualizations")
PARSER.add_argument(
    "-d", "--data", type=str, required=True,
    help="path to the beam search data file")
PARSER.add_argument(
    "-o", "--output_dir", type=str, required=True,
    help="path to the output directory")
ARGS = PARSER.parse_args()


HTML_TEMPLATE = Template("""
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Beam Search</title>
    <link rel="stylesheet" type="text/css" href="tree.css">
    <!--<script src="http://d3js.org/d3.v3.min.js"></script>-->
    <script src="d3.v3.min.js"></script>
  </head>
  <body style="position:absolute; width: 100%; height:100%">
  <p style="position:relative;">$SENTENCE</p>
    <script>
      var treeData = $DATA
    </script>
    <script src="tree.js"></script>
  </body>
</html>""")


def _add_graph_level(graph, level, parent_ids, names, scores, model_scores=None, alignment=None):
    """Adds a levelto the passed graph"""
    scores_list = scores if isinstance(scores, list) else [scores]
    sentence_end_indices = [i for i, x in enumerate(names) if x == "</s>"]
    min_score = min([scores_list[x] for x in sentence_end_indices]) if len(sentence_end_indices) > 0 else None
    min_node = None
    for i, parent_id in enumerate(parent_ids):
        new_node = (level, i)
        parent_node = (level - 1, parent_id)
        if min_score == scores_list[i]:
            min_node = new_node
        score_str = '%.3f' % float(scores_list[i]) if scores_list[i] is not None else '-inf'
        model_scores_str = "[" + ', '.join(map(lambda x: '%.3f' % float(x), model_scores[i])) + "]" \
            if model_scores is not None else ''
        graph.add_node(new_node)
        graph.node[new_node]["name"] = names[i]
        graph.node[new_node]["score"] = score_str
        graph.node[new_node]["model_scores"] = model_scores_str
        graph.node[new_node]["size"] = 100
        graph.node[new_node]["alignment"] = alignment[i] if alignment is not None else ""
        graph.node[new_node]["best_path"] = False
        # Add an edge to the parent
        graph.add_edge(parent_node, new_node)

    return min_node



def create_graph(predicted_ids, parent_ids, scores, predicted_tokens, model_scores=None, alignment=None):

    seq_length = len(predicted_ids)  # .shape[0]
    graph = nx.DiGraph()
    graph.add_node((0, 0))
    min_node = (0,0)

    for level in range(seq_length):
        names = [pred for pred in predicted_tokens[level]]
        mod_scores = model_scores[level] if model_scores is not None else None
        alignments = alignment[level] if alignment is not None else None
        min_node = _add_graph_level(graph, level + 1, parent_ids[level], names, scores[level], model_scores=mod_scores,
                         alignment=alignments)

    graph.node[(0, 0)]["name"] = "START"
    return graph, min_node


def main():
    if not os.path.exists(ARGS.output_dir):
        os.makedirs(ARGS.output_dir)

    path_base = os.path.dirname(os.path.realpath(__file__))

    # Copy required files
    shutil.copy2(path_base + "/beam_search_viz/tree.css", ARGS.output_dir)
    shutil.copy2(path_base + "/beam_search_viz/tree.js", ARGS.output_dir)
    shutil.copy2(path_base + "/beam_search_viz/d3.v3.min.js", ARGS.output_dir)

    with open(ARGS.data, 'r') as file:
        idx = 0

        for line in file:
            logging.info("Process sentence %d" % idx)
            beam_data = json.loads(line)

            predicted_ids = beam_data["predicted_ids"]
            parent_ids = beam_data["parent_ids"]
            predicted_tokens = beam_data["predicted_tokens"]
            scores = beam_data["scores"]
            model_scores = beam_data["model_scores"] if "model_scores" in beam_data else None
            alignment = beam_data["alignment"] if "alignment" in beam_data else None

            graph, min_node = create_graph(
                predicted_ids=predicted_ids,
                parent_ids=parent_ids,
                scores=scores,
                predicted_tokens=predicted_tokens,
                model_scores=model_scores,
                alignment=alignment)

            translation = []
            while min_node is not None:
                graph.node[min_node]["best_path"] = True
                translation.insert(0, html.escape(graph.node[min_node]["name"]))
                if min_node == (0, 0):
                    min_node = None
                else:
                    min_node = list(graph.in_edges(min_node))[0][0]

            json_str = json.dumps(
                json_graph.tree_data(graph, (0, 0)),
                ensure_ascii=True)

            html_str = HTML_TEMPLATE.substitute(SENTENCE=" ".join(translation).replace("@@ ", ""), DATA=json_str)
            output_path = os.path.join(ARGS.output_dir, "{:06d}.html".format(idx))
            with open(output_path, "w") as file:
                file.write(html_str)

            logging.info("write output to \t%s" % output_path)
            idx += 1


if __name__ == "__main__":
    main()
