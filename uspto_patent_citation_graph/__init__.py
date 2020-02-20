from typing import Optional

from itertools import chain, repeat
import logging

from graphscraper.base import Graph, Node, NodeList
from graphscraper.db import GraphDatabaseInterface, create_graph_database_interface
import requests

__author__ = "Peter Volf"
__copyright__ = "Copyright 2020, Peter Volf"
__email__ = "do.volfp@gmail.com"
__license__ = "MIT"
__url__ = "https://github.com/volfpeter/uspto-patent-citation-graph"
__version__ = "0.2002.0"


class USPTOPatentCitationGraph(Graph):

    def __init__(self, database: Optional[GraphDatabaseInterface], *, log_neighbor_loading: bool = False) -> None:
        """
        Initialization.

        Arguments:
            database: The database interface to use. If `None`, then a default one will be created.
            log_neighbor_loading: Whether to log when the graph loads citations from the USPTO API.
        """
        if database is None:
            database = USPTOPatentCitationGraph.create_default_database()

        super().__init__(database)

        self._logger: Optional[logging.Logger] = None
        if log_neighbor_loading:
            self._logger = logging.getLogger(self.__class__.__name__)
            self._logger.setLevel(logging.DEBUG)
            handler: logging.Handler = logging.StreamHandler()
            handler.setLevel(logging.DEBUG)
            handler.setFormatter(logging.Formatter(
                "%(levelname)s | %(asctime)s | %(name)s\n -- %(message)s"
            ))
            self._logger.addHandler(handler)

    @staticmethod
    def create_default_database(reset: bool = False) -> GraphDatabaseInterface:
        """
        Creates and returns a default SQLAlchemy database interface to use.

        Arguments:
            reset (bool): Whether to reset the database if it happens to exist already.
        """
        import sqlalchemy
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy.pool import StaticPool

        Base = declarative_base()
        engine = sqlalchemy.create_engine("sqlite:///USPTOPatentCitationGraph.db", poolclass=StaticPool)
        Session = sessionmaker(bind=engine)

        dbi: GraphDatabaseInterface = create_graph_database_interface(
            sqlalchemy, Session(), Base, sqlalchemy.orm.relationship
        )

        if reset:
            Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

        return dbi

    def get_authentic_node_name(self, node_name: str) -> Optional[str]:
        return node_name.strip()

    def log_neighbor_loading(self, patent_number: str) -> None:
        """
        Logs that the neighbors of the given patent are being loaded from the USPTO API.

        Arguments:
            patent_number: The patent number whose neighbors are being loaded.
        """
        if self._logger is not None:
            self._logger.debug(f"Loading neighbors of {patent_number}")

    def _create_node_list(self) -> NodeList:
        return USPTOPatentCitationNodeList(self)


class USPTOPatentCitationNode(Node):
    def _load_neighbors_from_external_source(self) -> None:
        graph = self._graph
        graph.log_neighbor_loading(self.name)

        query = {"patent_number": self.name}
        fields = ["cited_patent_number", "cited_patent_title", "citedby_patent_number", "citedby_patent_title"]
        response = requests.post("https://www.patentsview.org/api/patents/query", json={"q": query, "f": fields})
        if response.status_code != 200:
            raise ValueError("Request failed")

        patents = response.json()["patents"][0]
        cited_patents = patents.get("cited_patents", [])
        citedby_patents = patents.get("citedby_patents", [])


        nodes = graph.nodes

        for patent, prefix in chain(zip(cited_patents, repeat("cited")), zip(citedby_patents, repeat("citedby"))):
            patent_number = patent.get(f"{prefix}_patent_number")
            patent_title = patent.get(f"{prefix}_patent_title")
            if patent_number is None or patent_title is None:
                continue

            neighbor = nodes.get_node_by_name(
                patent_number.strip(),
                can_validate_and_load=True,
                external_id=patent_title.strip()
            )

            if neighbor is not None:
                graph.add_edge(self, neighbor)


class USPTOPatentCitationNodeList(NodeList):

    def _create_node(self, index: int, name: str, external_id: Optional[str] = None) -> Node:
        return USPTOPatentCitationNode(graph=self._graph, index=index, name=name, external_id=external_id)
