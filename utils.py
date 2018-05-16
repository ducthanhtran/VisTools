import os
import shutil
import logging


def copy_files(
        file_list: [str],
        output_dir: str,
        base: str = None,
        logger: logging.Logger = None):
    """
    copy a list of file to an output directory
    keep file metadata intact
    use logger if given
    :param file_list: list of files relative to the base directory
    :param output_dir: path to output directory
    :param base: (optional) base path instead of current directory
    :param logger: (optional) if not none enable logger
    :return:
    """
    if not os.path.exists(output_dir):
        if logger is not None:
            logger.info("create output directory %s" % output_dir)
        os.makedirs(output_dir)

    path_base = os.path.dirname(os.path.realpath(__file__)) if base is None else base

    # Copy required files
    for file in file_list:
        if logger is not None:
            logger.info("copy file %s to %s" % (file, output_dir))
        shutil.copy(os.path.join(path_base, file), output_dir)
