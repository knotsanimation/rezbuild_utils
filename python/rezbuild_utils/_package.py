import contextlib

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
