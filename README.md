# VisTools
Toolkit independent tools for visualizing NMT systems

## Installation

```
pip install -r requirements.txt
```

## Beam Search Visualization

In sockeye use option `--output-type beam_store` to save the beam history in a json file.

```
python generate_beam_viz.py -d path/to/json/file
                            -o path/to/output/directory
```
