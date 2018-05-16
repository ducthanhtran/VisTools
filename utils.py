import os
import shutil
import logging


def copy_files(
        file_list: [str],
        output_dir: str,
        base: str = None,
        logger: logging.Logger = None):

    if not os.path.exists(output_dir):
        if logger is not None:
            logger.info("create output directory %s" % output_dir)
        os.makedirs(output_dir)

    path_base = os.path.dirname(os.path.realpath(__file__)) if base is None else base

    # Copy required files
    for file in file_list:
        if logger is not None:
            logger.info("copy file %s to %s" % (file, output_dir))
        shutil.copy2(os.path.join(path_base, file), output_dir)
