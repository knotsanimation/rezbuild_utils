import logging
import re
import shutil
import subprocess
import tempfile
from typing import List
from typing import Optional
from pathlib import Path

from pythonning.filesystem import rmtree

LOGGER = logging.getLogger(__name__)


def install_pip_package(
    pip_package: str,
    python_version: str,
    target_dir: Path,
    pip_args: Optional[List[str]] = None,
):
    """
    Install the given pip package AND its dependencies at the given location.

    Example structure of target_dir with ``pip_package=PySide2``::

        target_dir/
            PySide2/
            PySide2-5.15.2.1.dist-info/
            shiboken2/
            shiboken2-5.15.2.1.dist-info/

    Args:
        pip_package:
            pip name of the package and its version.
            specified like ``packageName==version``.
        python_version: version to use for python. can be a shortened variant like ``3.9``.
        target_dir: path to a non-existing directory.
        pip_args: additional argument directly passed to pip
    """

    # find the latest corresponding full rez python version
    rez_python_version = subprocess.check_output(
        ["rez", "search", f"python-{python_version}", "--latest"]
    )
    rez_python_version = rez_python_version.decode("utf-8")
    rez_python_version = rez_python_version.rstrip("\n").rstrip("\r")

    # convert it to a full python version
    python_version_f = rez_python_version.split("-", 1)[-1]
    python_version_f = python_version_f.split(".")[:-1]
    python_version_f = ".".join(python_version_f)

    # we need the local path just to create the python package copy
    rez_local_packages_path = subprocess.check_output(
        ["rez", "config", "local_packages_path"]
    )
    rez_local_packages_path = rez_local_packages_path.decode("utf-8")
    rez_local_packages_path = rez_local_packages_path.rstrip("\n").rstrip("\r")

    dir_prefix = re.sub(r"(^\w)", pip_package, "-")
    pip_download_dir = Path(tempfile.mkdtemp(prefix=f"rez_pip_{dir_prefix}"))

    try:
        LOGGER.info(
            f"copying '{rez_python_version}' to '{rez_local_packages_path}' ..."
        )
        subprocess.run(
            [
                "rez",
                "cp",
                rez_python_version,
                "--reversion",
                python_version_f,
                "--dest-path",
                rez_local_packages_path,
            ],
            check=True,
        )

        rez_pip_args = [
            "rez",
            "python",
            "-m",
            "rez_pip",
            pip_package,
            "--python-version",
            f"=={python_version_f}",
            "--prefix",
            str(pip_download_dir),
        ]
        if pip_args:
            rez_pip_args += ["--"]
            rez_pip_args += pip_args

        # XXX: we assume rez-pip2 is installed in rez own venv
        LOGGER.debug(f"installing '{pip_package}' to '{pip_download_dir}' ...")
        subprocess.run(rez_pip_args, check=True)

        # XXX: we assume rez-pip always put pip packages in a python/ folder
        pip_packages_content = list(pip_download_dir.glob("**/python/"))

        for pip_package_content in pip_packages_content:
            LOGGER.info(f"copying '{pip_package_content}' to '{target_dir}' ...")
            shutil.copytree(pip_package_content, target_dir, dirs_exist_ok=True)

    finally:
        LOGGER.debug(f"removing {pip_download_dir}")
        rmtree(pip_download_dir)
