import json
import html
import argparse
import os
import logging

from utils import copy_files

logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format='[%(levelname)s:attention_viz] %(message)s', level=logging.INFO)


PARSER = argparse.ArgumentParser(
    description="Generate beam search visualizations")
PARSER.add_argument(
    "-d", "--data", type=str, required=True,
    help="path to the attention data file")
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
    for line in content:
        tokens = line.split('|||')
        if first:
            first=False
            sent['id'] = tokens[0]
            sent['src'] = html.escape(tokens[1]).strip().split(' ')
            sent['score'] = tokens[2]
            sent['trg'] = html.escape(tokens[3]).strip().split(' ')
            sent['src_length'] = tokens[4]
            sent['trg_lenght'] = tokens[5]
            sent['attentions'] = []
        elif len(tokens) == 1 and tokens[0] == '\n':
            first = True
            sentences.append(sent)
            sent={}
        else:
            sent['attentions'].append(tokens[0].split(' '))


#    print("data = '" + json.dumps(sentences).replace("\\n", "").replace("'", "\\'") + "';")

html_string = "<html><head>"
html_string += """
<link rel="stylesheet" type="text/css" href="style.css">
<script src="attention.js"></script>
<script> var data = %s; </script>
<script>
document.addEventListener("DOMContentLoaded", function(event) { 
    attention_viz(data);
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
    'attention_viz/style.css'
]

copy_files(output_files, ARGS.output_dir, logger=logging)

output_path = os.path.join(ARGS.output_dir, "index.html")
if output_path is not None:
    with open(output_path, "w") as file:
        logging.info("write index file to %s" % (output_path))
        file.write(html_string)
else:
    print(html_string)
