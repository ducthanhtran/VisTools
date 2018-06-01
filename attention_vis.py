import json
import html
import argparse
import os
import logging
import numpy as np

from utils import copy_files

logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format='[%(levelname)s:attention_viz] %(message)s', level=logging.INFO)


PARSER = argparse.ArgumentParser(
    description="Generate beam search visualizations")
PARSER.add_argument(
    "-d", "--data", type=str, required=True,
    help="path to the attention data file")
PARSER.add_argument(
    "-s", "--scale-max", action="store_true",
    help="scale attentions by the max of the sentence"
)
PARSER.add_argument(
    "-o", "--output-dir", type=str, required=True,
    help="path to the output directory.")
ARGS = PARSER.parse_args()

filepath = ARGS.data

with open(filepath) as fp:
    content = fp.readlines()
    sent = {}
    sentences = []
    first = True
    attentions = []
    for line in content:
        tokens = line.split('|||')
        if first:
            first=False
            sent['id'] = tokens[0]
            sent['src'] = html.escape(tokens[3]).strip().split(' ')
            sent['score'] = tokens[2]
            sent['trg'] = html.escape(tokens[1]).strip().split(' ')
            sent['src_length'] = tokens[4]
            sent['trg_lenght'] = tokens[5]
            sent['attentions'] = []
        elif len(tokens) == 1 and tokens[0] == '\n':
            #print(np.array(attentions).shape, np.array(attentions).transpose().shape)
            max_attention = max(max(attentions)) if ARGS.scale_max else 1
            sent['attentions'] = (np.array(attentions)/max_attention).transpose().tolist()
            first = True
            sentences.append(sent)
            sent = {}
            attentions = []
        else:
            attentions.append([float(x) for x in tokens[0].replace('\n', '').split(' ')])

#    print("data = '" + json.dumps(sentences).replace("\\n", "").replace("'", "\\'") + "';")

html_string_overlay = "<html><head>"
html_string_overlay += """
<link rel="stylesheet" type="text/css" href="style.css">
<script src="attention.js"></script>
<script> var data = %s; </script>
<script>
document.addEventListener("DOMContentLoaded", function(event) { 
    attention_viz_overlay(data);
});
 </script>
 </head>
 <body>
 <div id="sentences"></div>
 </body>
 </html>
 """ % json.dumps(sentences, ensure_ascii=True).replace("\\n", "")


html_string_matrix = "<html><head>"
html_string_matrix += """
<link rel="stylesheet" type="text/css" href="style.css">
<script src="d3.v3.min.js"></script>
<script src="https://cdn.rawgit.com/eligrey/FileSaver.js/5ed507ef8aa53d8ecfea96d96bc7214cd2476fd2/FileSaver.min.js"></script>
<script src="https://cdn.rawgit.com/eligrey/Blob.js/0cef2746414269b16834878a8abc52eb9d53e6bd/Blob.js"></script>
<script src="attention.js"></script>
<script> var data = %s; </script>
<script>
document.addEventListener("DOMContentLoaded", function(event) { 
    attention_viz_matrix(data);
});
 </script>
 </head>
 <body>
 <div id="sentences"></div>
 </body>
 </html>
 """ % json.dumps(sentences, ensure_ascii=True).replace("\\n", "")

output_files = [
    'attention_viz/attention.js',
    'attention_viz/style.css',
    'attention_viz/d3.v3.min.js',
]

copy_files(output_files, ARGS.output_dir, logger=logging)

output_path_overlay = os.path.join(ARGS.output_dir, "index.html")
if output_path_overlay is not None:
    with open(output_path_overlay, "w") as file:
        logging.info("write index file to %s" % output_path_overlay)
        file.write(html_string_overlay)

output_path_matrix = os.path.join(ARGS.output_dir, "index_matrix.html")
if output_path_matrix is not None:
    with open(output_path_matrix, "w") as file:
        logging.info("write index file to %s" % output_path_matrix)
        file.write(html_string_matrix)
