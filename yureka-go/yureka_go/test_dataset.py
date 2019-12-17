import pytest
import torch
import random

from typing import List

from yureka_go.dataset import move_plane, stone_plane, GoDataView


@pytest.mark.parametrize(
    'plane,plane_tensor',
    (
        (
            # nothing
            hex(int('0000000000000000000' * 19, 2))[2:].zfill(91),
            torch.zeros(19, 19),
        ),
        (
            # upper left corner
            hex(int('1000000000000000000' + '0000000000000000000' * 18, 2))[2:].zfill(91),
            torch.tensor([1] + [0] * 360).float().view(19, 19),
        ),
        (
            # upper right corner
            hex(int('0000000000000000001' + '0000000000000000000' * 18, 2))[2:].zfill(91),
            torch.tensor([0] * 18 + [1] + [0] * 342).float().view(19, 19),
        ),
        (
            # bottom left corner
            hex(int('0000000000000000000' * 18 + '1000000000000000000', 2))[2:].zfill(91),
            torch.tensor([0] * 342 + [1] + [0] * 18).float().view(19, 19),
        ),
        (
            # bottom right corner
            hex(int('0000000000000000000' * 18 + '0000000000000000001', 2))[2:].zfill(91),
            torch.tensor([0] * 360 + [1]).float().view(19, 19),
        ),
        (
            # middle
            hex(int('0000000000000000000' * 9 + '0000000001000000000' + '0000000000000000000' * 9, 2))[2:].zfill(91),
            torch.tensor([0] * 180 + [1] + [0] * 180).float().view(19, 19),
        ),
    )
)
def test_stone_plane(plane: str, plane_tensor: torch.Tensor):
    assert stone_plane(plane).equal(plane_tensor)


@pytest.mark.parametrize(
    'turn,planes',
    (
        ('0', [torch.ones(19, 19), torch.zeros(19, 19)]),
        ('1', [torch.zeros(19, 19), torch.ones(19, 19)]),
    )
)
def test_move_plane(turn: str, planes: List[torch.Tensor]):
    assert all(a.equal(b) for a, b in zip(move_plane(turn), planes))


@pytest.mark.parametrize(
    'filenames,length',
    (
        (['test-data/kgs.0.gz'], 6366),
        (['test-data/kgs.1.gz'], 6658),
        (['test-data/kgs.0.gz', 'test-data/kgs.1.gz'], 13024)
    )
)
def test_go_data_view(filenames: List[str], length: int):
    view = GoDataView(filenames)
    assert len(view) == length
    random_idx = random.randrange(0, len(view))

    planes, probs, outcome = view[random_idx]
    assert planes.size() == (18, 19, 19)
    assert probs.size() == (19 * 19 + 1,)
    assert outcome.item() in (-1, 1)

    # check the cache
    cached_planes, cached_probs, cached_outcome = view.cache[random_idx]
    assert cached_planes.equal(planes)
    assert cached_probs.equal(probs)
    assert cached_outcome.equal(outcome)

    # retrieve again
    planes, probs, outcome = view[random_idx]
    assert cached_planes.equal(planes)
    assert cached_probs.equal(probs)
    assert cached_outcome.equal(outcome)