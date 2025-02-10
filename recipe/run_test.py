import sys
import psutil
import tempfile
import shutil
from pathlib import Path


SKIPS = [
    "(test_ws and test_reject)",
    "(test_rsgi and test_body_stream_req)",
    "(test_scope and workers)",
]

SKIP_OR = " or ".join(SKIPS)
K = ["-k", f"not ({SKIP_OR})"]

PYTEST = ["pytest", "-vv", "--color=yes", "--tb=long", *K]


def main():
    print(">>>", *PYTEST, flush=True)
    tmp = Path(tempfile.mkdtemp())
    shutil.copytree(Path("tests"), tmp / "tests")
    proc = psutil.Popen([*PYTEST], cwd=str(tmp))
    rc = proc.wait()
    all_procs = [*proc.children(recursive=True), proc]
    killed = []
    for p in all_procs:
        print(p, end="")
        if not p.is_running():
            print("... was not running", flush=True)
            continue
        killed += [p]
        print("... killed", flush=True)
    if killed:
        psutil.wait_procs(killed)
    print("cleaning...", tmp, flush=True)
    shutil.rmtree(tmp, ignore_errors=True)
    return rc


if __name__ == "__main__":
    sys.exit(main())
