from functools import wraps
import os
from pathlib import Path
import pickle

try:
    from loguru import logger
except ImportError:
    from logging import getLogger

    logger = getLogger("trepro")
    logger.success = logger.info

try:
    import matplotlib
    from matplotlib import pyplot as plt
    from matplotlib.figure import Figure
except ImportError:
    logger.error("Failed to import matplotlib, matplotlib reproduction will not work.")
    raise

from subprocess import check_output, CalledProcessError, PIPE

mpl_savefig = Figure.savefig

separator_start = b"---Savefig_Metadata_Start---"
separator_end = b"---Savefig_Metadata_End---"
__version__ = "3.1.0"


def _get_git_info(include_diff=False):
    res = {
        "cwd": os.getcwd(),
        "os": os.uname(),
    }

    if include_diff:
        try:
            diff = check_output("git diff", shell=True, stderr=PIPE).decode("utf-8")
            res["git-diff"] = diff
        except CalledProcessError:
            ...

    cmd = 'git log -1 --date=iso8601 --format="%H || %ad || %an"'
    try:
        result = check_output(cmd, shell=True, stderr=PIPE).decode("utf-8")
        git_info = dict(
            zip(["git-hash", "git-date", "git-author"], result.split(" || "))
        )
        res.update(git_info)
    except CalledProcessError:
        ...

    # add git remote info
    try:
        remote = (
            check_output("git remote get-url origin", shell=True, stderr=PIPE)
            .decode("utf-8")
            .strip()
        )
        res["git-remote"] = remote
    except CalledProcessError:
        ...

    return res


def patch_savefig():
    @wraps(mpl_savefig)
    def inner(fig: Figure, file_name: str, *args, **kwargs):
        # get file extension
        ext = os.path.splitext(file_name)[1]
        if ext in [".png", ".pdf"]:
            # save fig pickle using Steganography
            saved_fig = mpl_savefig(fig, file_name, *args, **kwargs)

            try:
                git_info = _get_git_info()
            except Exception as e:
                logger.warning(f"Failed to get git info: {e}")
                git_info = {}

            # save metadata to file
            try:
                with open(file_name, "ab") as f:
                    f.write(separator_start)
                    pickle.dump(
                        {
                            "save_version": __version__,
                            "matplotlib_fig": fig,
                            "matplotlib_version": matplotlib.__version__,
                            **git_info,
                        },
                        f,
                    )
                    f.write(separator_end)

                logger.success(f"Metadata saved to {file_name}")
            except Exception as e:
                logger.warning(f"Failed to save metadata: {e}")
            finally:
                return saved_fig

        else:
            logger.warning(f"Metadata will not be saved for extention: '{ext}'\n")

            return mpl_savefig(file_name, *args, **kwargs)

    Figure.savefig = inner


def load_saved_figure(file_name: str | Path) -> tuple[Figure, dict]:
    # get ax: ax = fig.gca()
    file = Path(file_name)

    if not file.exists():
        raise FileNotFoundError(f"File not found: {file_name}")

    with file.open("rb") as f:
        data = f.read()

        if separator_start not in data or separator_end not in data:
            raise ValueError("File is not a valid Trepro-Visualization file")

        # find start and end
        start = data.index(separator_start) + len(separator_start)
        end = data.index(separator_end)

        # load metadata
        metadata = pickle.loads(data[start:end])

        # load figure
        fig = metadata.pop("matplotlib_fig")

        logger.success(
            f"ReLoaded figure from {file_name} (save version: {metadata['save_version']})"
        )
        return fig, metadata


if __name__ == "__main__":
    # test
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [4, 5, 6])
    patch_savefig()
    plt.savefig("test.png")
    # print(_get_git_info())
    # load
    fig, metadata = load_saved_figure("test.png")
    print(metadata)
