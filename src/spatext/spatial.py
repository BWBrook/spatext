from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int64]


@dataclass(frozen=True, slots=True)
class CellGraphDomain:
    """Generic cell-graph domain for grid and non-grid tessellations."""

    rows: int
    cols: int
    neighborhood: str
    coordinates: IntArray
    adjacency: tuple[tuple[int, ...], ...]
    transition_matrix: FloatArray

    @property
    def cell_count(self) -> int:
        return self.rows * self.cols

    def reshape_vector(self, values: FloatArray) -> FloatArray:
        return values.reshape((self.rows, self.cols))

    def to_metadata(self) -> dict[str, int | str]:
        return {
            "rows": self.rows,
            "cols": self.cols,
            "cell_count": self.cell_count,
            "neighborhood": self.neighborhood,
        }


def build_square_lattice_domain(
    rows: int, cols: int, *, neighborhood: str = "rook"
) -> CellGraphDomain:
    """Build a square-lattice cell graph with symmetric rook adjacency."""

    if rows <= 0 or cols <= 0:
        raise ValueError("rows and cols must be positive")
    if neighborhood != "rook":
        raise ValueError(f"unsupported neighborhood: {neighborhood}")

    coordinates = np.array(
        [(row, col) for row in range(rows) for col in range(cols)],
        dtype=np.int64,
    )
    adjacency_rows: list[tuple[int, ...]] = []
    transition_matrix = np.zeros((rows * cols, rows * cols), dtype=np.float64)

    for row in range(rows):
        for col in range(cols):
            index = row * cols + col
            neighbors: list[int] = []
            if row > 0:
                neighbors.append((row - 1) * cols + col)
            if row + 1 < rows:
                neighbors.append((row + 1) * cols + col)
            if col > 0:
                neighbors.append(row * cols + (col - 1))
            if col + 1 < cols:
                neighbors.append(row * cols + (col + 1))

            neighbor_tuple = tuple(sorted(neighbors))
            adjacency_rows.append(neighbor_tuple)
            weight = 1.0 / len(neighbor_tuple)
            for neighbor in neighbor_tuple:
                transition_matrix[index, neighbor] = weight

    return CellGraphDomain(
        rows=rows,
        cols=cols,
        neighborhood=neighborhood,
        coordinates=coordinates,
        adjacency=tuple(adjacency_rows),
        transition_matrix=transition_matrix,
    )


def adjacency_edges(adjacency: tuple[tuple[int, ...], ...]) -> list[tuple[int, int]]:
    """Return an undirected edge list without duplicate edges."""

    edges: list[tuple[int, int]] = []
    for source, neighbors in enumerate(adjacency):
        for target in neighbors:
            if source < target:
                edges.append((source, target))
    return edges
