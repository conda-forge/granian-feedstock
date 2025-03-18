import sys
from subprocess import call

import platform

PLATFORM = platform.system()
ARCH = platform.processor()
LINUX = PLATFORM == "Linux"
X86_64 = ARCH == "x86_64"


SKIPS = [
    "(test_ws and test_reject)",
    "(test_rsgi and test_body_stream_req)",
    "(test_scope and workers)",
]

if LINUX and not X86_64:
    SKIPS += [
        # https://github.com/conda-forge/granian-feedstock/pull/50
        ## flaky in CI
        "(test_asgi and test_timeout)",
    ]

SKIP_OR = " or ".join(SKIPS)
K = ["-k", f"not ({SKIP_OR})"]

PYTEST = ["pytest", "-vv", "--color=yes", "--tb=long", *K]


if __name__ == "__main__":
    sys.exit(call(PYTEST))
