import sys
from subprocess import Popen

SKIPS = [
    "(test_ws and test_reject)",
    "(test_rsgi and test_body_stream_req)",
    "(test_scope and workers)",
]

SKIP_OR = " or ".join(SKIPS)
K = ["-k", f"not ({SKIP_OR})"]

PYTEST = ["pytest", "-vv", "--color=yes", "--tb=long", *K]


def main() -> int:
    proc = Popen(PYTEST)
    try:
        return proc.wait(timeout=400)
    finally:
        proc.kill()
        proc.terminate()
        return 1


if __name__ == "__main__":
    sys.exit(main())
