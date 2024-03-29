from pathlib import Path

from .reader import ctc_reader


def napari_get_reader(path):
    """A basic implementation of a Reader contribution.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    function or None
        If the path is a recognized format, return a function that accepts the
        same path or list of paths, and returns a list of layer data tuples.
    """
    if isinstance(path, list):
        # open multiple folders
        raise NotImplementedError("Open multiple folders at once")

    # if we know we cannot read the file, we immediately return None.
    path = Path(path)
    if not path.is_dir():
        return None

    # otherwise we return the *function* that can read ``path``.
    return ctc_reader(path)


# def reader_function(path):
#     """Take a path or list of paths and return a list of LayerData tuples.

#     Readers are expected to return data as a list of tuples, where each tuple
#     is (data, [add_kwargs, [layer_type]]), "add_kwargs" and "layer_type" are
#     both optional.

#     Parameters
#     ----------
#     path : str or list of str
#         Path to file, or list of paths.

#     Returns
#     -------
#     layer_data : list of tuples
#         A list of LayerData tuples where each tuple in the list contains
#         (data, metadata, layer_type), where data is a numpy array, metadata is
#         a dict of keyword arguments for the corresponding viewer.add_* method
#         in napari, and layer_type is a lower-case string naming the type of
#         layer. Both "meta", and "layer_type" are optional. napari will
#         default to layer_type=="image" if not provided
#     """
#     # handle both a string and a list of strings
#     paths = [path] if isinstance(path, str) else path
#     # load all files into array
#     arrays = [np.load(_path) for _path in paths]
#     # stack arrays into single array
#     data = np.squeeze(np.stack(arrays))

#     # optional kwargs for the corresponding viewer.add_* method
#     add_kwargs = {}

#     layer_type = "image"  # optional, default is "image"
#     return [(data, add_kwargs, layer_type)]
