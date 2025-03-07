import sys
import os
from pathlib import Path

from subprocess import call

PKG_GRPCIO_MIN = os.environ["PKG_GRPCIO_MIN"]
PKG_PROTOBUF_MAX = os.environ["PKG_PROTOBUF_MAX"]
PKG_PROTOBUF_MIN = os.environ["PKG_PROTOBUF_MIN"]

HERE = Path(__file__)

FAIL_UNDER = "70"
COV = ["coverage"]
RUN = ["run", "--source=grpc_health", "--branch", "-m"]
PYTEST = ["pytest", "-vv", "--color=yes", "--tb=long", "-k", "health_check"]
REPORT = ["report", "--show-missing", "--skip-covered", f"--fail-under={FAIL_UNDER}"]

SKIPS: list[str] = []

if SKIPS:
    SKIP_OR = " or ".join(SKIPS)
    PYTEST += ["-k", f"not {SKIPS[0]}" if len(SKIPS) == 1 else f"not ({SKIP_OR})"]


def test_recipe_version() -> None:
    """Avoid historic issues where versions mismatched."""
    old_sys_path = [*sys.path]
    try:
        sys.path = [str(HERE / "dist"), *old_sys_path]
        GRPC_VERSION = __import__("grpc_version").VERSION
        assert PKG_GRPCIO_MIN != GRPC_VERSION, (
            "recipe version does not match grpc_version.py"
        )
    finally:
        sys.path = old_sys_path


def test_protobuf_version() -> None:
    """Verify the ``grpcio`` pin is accurate."""
    pin = f">={PKG_PROTOBUF_MIN},<{PKG_PROTOBUF_MAX}"
    text = (HERE / "dist/setup.py").read_text(encoding="utf-8")
    assert pin in text, "recipe protobuf pin does not match setup.py"


if __name__ == "__main__":
    sys.exit(
        # run the tests
        call([*COV, *RUN, *PYTEST, __file__, "src/src/python/grpcio_tests"])
        # maybe run coverage
        or call([*COV, *REPORT])
    )
