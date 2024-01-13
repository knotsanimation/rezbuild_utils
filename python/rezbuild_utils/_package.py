import contextlib
import os

import rez.package_resources


@contextlib.contextmanager
def preserve_build_attributes():
    """
    Dirty hack to avoid package creation to remove build attributes.

    Use at your own risk.

    Example::

        with preserve_build_attributes(), make_package("python", ".") as package:
            package.version = "0.1.0"
            package.build_command = "python {root}/build.py"
            # ...


    """
    initial = rez.package_resources.package_build_only_keys
    rez.package_resources.package_build_only_keys = tuple()
    try:
        yield
    finally:
        rez.package_resources.package_build_only_keys = initial


class BuildPackageVersion:
    """
    An object to manipulate the version attribute following Knots conventions.

    It assumes a package with a traditional semver versioning is being built.

    **Knots specificities:**

    * The **extra-patch** is an additional "sub-patch" token for rez versioning of vendor packages.
    """

    def __init__(self):
        self._source = os.environ["REZ_BUILD_PROJECT_VERSION"]
        self._split = self._source.split(".")

    @property
    def full_version(self) -> str:
        return self._source

    @property
    def vendor_version(self) -> str:
        # without extra_patch
        return ".".join(self._split[:-1])

    @property
    def major(self) -> str:
        return self._split[0]

    @property
    def minor(self) -> str:
        return self._split[1]

    @property
    def patch(self) -> str:
        return self._split[2]

    @property
    def extra_patch(self) -> str:
        return self._split[3]
