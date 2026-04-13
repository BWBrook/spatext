from __future__ import annotations

import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st

from spatext.spatial import adjacency_edges, build_square_lattice_domain


@given(rows=st.integers(min_value=2, max_value=8), cols=st.integers(min_value=2, max_value=8))
def test_square_lattice_domain_has_symmetric_rook_adjacency(rows: int, cols: int) -> None:
    domain = build_square_lattice_domain(rows, cols)

    assert domain.cell_count == rows * cols
    assert domain.coordinates.shape == (rows * cols, 2)

    for source, neighbors in enumerate(domain.adjacency):
        for target in neighbors:
            assert source in domain.adjacency[target]

    edges = adjacency_edges(domain.adjacency)
    assert len(edges) == ((rows - 1) * cols) + (rows * (cols - 1))


def test_square_lattice_domain_rejects_invalid_shape_and_neighborhood() -> None:
    with pytest.raises(ValueError, match="positive"):
        build_square_lattice_domain(0, 5)

    with pytest.raises(ValueError, match="unsupported neighborhood"):
        build_square_lattice_domain(5, 5, neighborhood="hex")


def test_square_lattice_domain_metadata_and_reshape_helpers() -> None:
    domain = build_square_lattice_domain(3, 4)
    metadata = domain.to_metadata()

    assert metadata == {"rows": 3, "cols": 4, "cell_count": 12, "neighborhood": "rook"}

    values = np.arange(12, dtype=np.float64)
    reshaped = domain.reshape_vector(values)
    assert reshaped.shape == (3, 4)
    assert reshaped[2, 3] == pytest.approx(11.0)
