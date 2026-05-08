"""
Pytest configuration:
    1. Add `pytest` starting directory for load `fortranmagic.py` and
       compiled testing modules;
    2. Fixture for verbosity level at session start;
    3. Fixture for workaround probable bug `numpy.f2py` on Windows.
"""

import os
import shutil
import subprocess
import sys

import IPython.core.interactiveshell as ici
import pytest

_VERBOSE = None

_NUMPY_CORRECT_COMPILERS = []
_FORTRAN_COMPILERS = (
    "gfortran",
    "flang-new",
    "flang",
    "nvfortran",
    "pgfortran",
    "ifort",
    "ifx",
    "g95",
)
_FORTRAN_COMPILER = next((compiler for compiler in _FORTRAN_COMPILERS if shutil.which(compiler)), None)

print("XXXXX>>>>> Detect _HAS_LAPACK", file=sys.stderr)
try:
    subprocess.run(
        [sys.executable, "-m", "numpy.f2py", "--dep=lapack", "-c", "-m", "detect_lapack", "tests/solve.f90"], check=True
    )
    import detect_lapack

    assert detect_lapack.solve.__doc__
    _HAS_LAPACK = True
except Exception:  # noqa: BLE001
    _HAS_LAPACK = False
print(f"XXXXX>>>>> _HAS_LAPACK={_HAS_LAPACK}", file=sys.stderr)


@pytest.fixture(scope="session", autouse=True)
def isolate_ipython_dir(tmp_path_factory):
    ipdir = tmp_path_factory.mktemp("ipython")
    mp = pytest.MonkeyPatch()
    mp.setenv("IPYTHONDIR", str(ipdir))
    yield
    mp.undo()


def pytest_configure(config) -> None:
    """Get verbosity level"""

    global _VERBOSE
    _VERBOSE = config.getoption("verbose")

    sys.path.insert(0, os.getcwd())
    config.addinivalue_line("markers", "requires_fortran: requires a working Fortran compiler")
    config.addinivalue_line("markers", "requires_lapack: requires LAPACK")


def pytest_collection_modifyitems(config, items) -> None:
    if _FORTRAN_COMPILER is None:
        skip = pytest.mark.skip(reason="No Fortran compiler found in PATH")
        for item in items:
            if "requires_fortran" in item.keywords:
                item.add_marker(skip)
    if not _HAS_LAPACK:
        skip = pytest.mark.skip(reason="LAPACK not found via numpy.f2py --dep")
        for item in items:
            if "requires_lapack" in item.keywords:
                item.add_marker(skip)


@pytest.fixture(scope="session")
def has_lapack():
    return _HAS_LAPACK


@pytest.fixture(scope="session")
def verbose():
    """Access to verbosity level"""
    return _VERBOSE


@pytest.fixture(scope="session")
def numpy_correct_compilers():
    """Corrected `numpy.f2py` flags"""

    return _NUMPY_CORRECT_COMPILERS


@pytest.fixture(scope="module")
def use_fortran_config():
    """Init & reset %fortran_config


    Use: @pytest.mark.usefixtures("use_fortran_config")
    """

    f_config = "--defaults"
    ish = ici.InteractiveShell()
    ish.run_cell("%load_ext fortranmagic")
    ish.run_cell("%fortran_config " + f_config)

    yield

    ish.run_cell("%fortran_config " + f_config)
    # Unfortunately, the state of the `FortranMagics` class cannot be
    # reset because in `fortranmagic.py ` there is no
    # `unload_extension()` function.
