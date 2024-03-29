"""
TODOs
- add progress bar in the viewer: https://github.com/napari/napari/blob/main/examples/progress_bar_minimal_.py
- sync colors of tracking and segmentation layers
- put in the color-by-child layer as well, invisible
- speed up the format checker
- add typing
- add tests
"""
from pathlib import Path

import numpy as np
from skimage.measure import regionprops
from tifffile import imread
from tqdm import tqdm


def ctc_reader(path: Path):
    segmentation, man_track = _load_tra(path)
    _check_ctc_tracks(segmentation, man_track)
    tracks, tracks_graph = _ctc_to_napari_tracks(segmentation, man_track)
    return lambda path: [
        (segmentation, dict(name="labels"), "labels"),  # noqa
        (tracks, dict(graph=tracks_graph, name="tracks"), "tracks"),  # noqa
    ]


def _ctc_to_napari_tracks(segmentation, man_track):
    """convert a traccuracy graph to napari tracks"""

    tracks = []
    for t, frame in tqdm(
        enumerate(segmentation),
        total=len(segmentation),
        leave=False,
        desc="Computing centroids",
    ):
        for r in regionprops(frame):
            tracks.append((r.label, t) + r.centroid)

    tracks_graph = {}
    for idx, _, _, parent in tqdm(
        man_track,
        desc="Converting CTC to napari tracks",
        leave=False,
    ):
        if parent != 0:
            tracks_graph[idx] = [parent]

    return tracks, tracks_graph


class FoundTracks(Exception):
    pass


def _load_tra(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Load segmentation and tracks from a folder.

    Checks for
    - alphanumerically ordered *.tif files
    - tracks in txt format, preferably called `man_track.txt` or `res_track.txt`.

    Args:
        path (Path): Folder with segmentations and tracks.

    Raises:
        ValueError:

    Returns:
        np.ndarray: stacked segmentations as T x 2D/3D array
        np.ndarray: tracks as N x 4 array
    """
    tracks_globs = ["man_track.txt", "res_track.txt", "*.txt"]

    try:
        for _glob in tracks_globs:
            print(f"Trying to load tracks with `glob {path / _glob}`")
            for _cand in path.glob(_glob):
                tracks_file = path / _cand
                if tracks_file.exists():
                    tracks = np.loadtxt(tracks_file, delimiter=" ").astype(int)
                    raise FoundTracks
    except FoundTracks:
        print(f"Loaded tracks from {tracks_file}")
    else:
        raise ValueError(f"Did not find a .txt file with tracks in {path}.")

    files = sorted(path.glob("*.tif"))
    segmentation = np.stack(
        [
            imread(x)
            for x in tqdm(
                files,
                desc="Loading segmentations",
                leave=True,
            )
        ]
    )
    print(f"Found {len(segmentation)} .tif files with stem `{files[0].stem}`.")

    return segmentation, tracks


def _check_ctc_tracks(masks: np.ndarray, tracks: np.ndarray):
    """sanity check of all labels in a CTC dataframe are present in the masks"""
    for t in tqdm(
        range(tracks[:, 1].min(), tracks[:, 1].max() + 1),
        leave=False,
        desc="Checking CTC",
    ):
        sub = tracks[(tracks[:, 1] <= t) & (tracks[:, 2] >= t)]
        sub_lab = set(sub[:, 0])
        masks_lab = set(np.unique(masks[t])) - {0}
        if not sub_lab.issubset(masks_lab):
            print(f"Missing labels in masks at t={t}: {sub_lab-masks_lab}")
            return False
    return True
