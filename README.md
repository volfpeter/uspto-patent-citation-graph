# USPTO-patent-citation-graph

Graph that downloads patent citation data from USPTO's [PatentsView](https://www.patentsview.org) API on-demand and stores it locally in an SQL database (and in memory) for fast access later.

The project is based on the [graphscraper](https://pypi.org/project/graphscraper/) project, please see that project for the details of the graph API.

## Installation

Install the latest version of the project from the Python Package Index using `pip install uspto-patent-citation-graph`.

## Getting started

Creating a graph instance that will use a default, on-disk SQLite database:

```Python
from uspto_patent_citation_graph import USPTOPatentCitationGraph

graph = USPTOPatentCitationGraph(None)
```

Loading a node that is not in the local database yet:

```Python
# `can_validate_and_load=True` tells the graph's node list that it is allowed to
# load data from the PatentsView API. Its default value is `False`, and the
# argument can be omitted if the given patent is already in the local database.
patent_number = "4733665"  # Stent patent
stent_patent = g.nodes.get_node_by_name(patent_number, can_validate_and_load=True)
```

Accessing a node's neighbors (cited and cited-by patents):

```Python
print(f"Neighbors of {stent_patent.name}:")
for neighbor in stent_patent.neighbors:
    print(f" - {neighbor.name}: {neighbor.external_id}")
```

## Community guidelines

Any form of constructive contribution is welcome:

- Questions, feedback, bug reports: please open an issue in the issue tracker of the project or contact the repository owner by email, whichever you feel appropriate.
- Contribution to the software: please open an issue in the issue tracker of the project that describes the changes you would like to make to the software and open a pull request with the changes. The description of the pull request must references the corresponding issue.

The following types of contribution are especially appreciated:

## License - MIT

The library is open-sourced under the conditions of the [MIT license](https://choosealicense.com/licenses/mit/).
