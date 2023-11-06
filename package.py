name = "rezbuild_utils"

version = "2.1.1"

authors = ["Liam Collod"]

description = "Provide utilities to build rez packages."

uuid = "5971c4a79d0741c2a2038e202cd6a897"

requires = ["python-3+", "rez"]

private_build_requires = ["python-3+"]

build_command = "python {root}/build.py"

__test_command_base = (
    "pytest-launcher {root}/python/tests"
    " --config-file '${{PYTEST_CONFIG_FILE}}'"
    " --log-cli-level '${{PYTEST_LOG_CLI_LEVEL}}'"
)

tests = {
    "unit-37": {
        "command": __test_command_base,
        "requires": ["python-3.7", "pytest", "pytest_utils"],
    },
    "unit-39": {
        "command": __test_command_base,
        "requires": ["python-3.9", "pytest", "pytest_utils"],
    },
    "unit-310": {
        "command": __test_command_base,
        "requires": ["python-3.10", "pytest", "pytest_utils"],
    },
}

tools = [
    "rezbuild_utils-clearcache",
]


def commands():
    env.PYTHONPATH.append("{root}/python")

    alias(
        "rezbuild_utils-clearcache",
        "python -c 'import rezbuild_utils;rezbuild_utils.clear_download_cache()'",
    )
