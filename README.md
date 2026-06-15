import networkx as nx
import pytest

from search import SearchAlgorithm, search


@pytest.fixture
def grid() -> nx.Graph:
    return nx.grid_2d_graph(4, 4)


@pytest.mark.parametrize("algorithm", list(SearchAlgorithm))
def test_every_algorithm_finds_route(grid: nx.Graph, algorithm: SearchAlgorithm) -> None:
    result = search(grid, (0, 0), (3, 3), algorithm)
    assert result.found
    assert result.path[0] == (0, 0)
    assert result.path[-1] == (3, 3)
    assert result.nodes_expanded > 0


def test_astar_finds_shortest_grid_path(grid: nx.Graph) -> None:
    result = search(grid, (0, 0), (3, 3), SearchAlgorithm.ASTAR)
    assert result.path_length == 6


def test_blocked_goal_returns_explanation(grid: nx.Graph) -> None:
    result = search(grid, (0, 0), (9, 9), SearchAlgorithm.BFS)
    assert not result.found
    assert "blocked" in result.explanation.lower()

