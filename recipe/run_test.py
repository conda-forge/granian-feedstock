import sys
import psutil
import time
import shutil
import os
from pathlib import Path


SKIPS = [
    "(test_ws and test_reject)",
    "(test_rsgi and test_body_stream_req)",
    "(test_scope and workers)",
]

SKIP_OR = " or ".join(SKIPS)
K = ["-k", f"not ({SKIP_OR})"]

PYTEST = ["pytest", "-vv", "--color=yes", "--tb=long", *K]


def clean(path: Path, retries: int = 1) -> None:
    time.sleep(1)
    print("setting permissions...", flush=True)
    for path in path.rglob("*"):
        print(".", end="")
        path.chmod(0o777)
    print("\ncleaning...", path, flush=True)
    try:
        shutil.rmtree(path)
    except Exception as err:
        print("!!!", err, flush=True)
        if retries:
            print(f"... trying {retries} more time(s)", flush=True)
            clean(path, retries - 1)
    else:
        return

    shutil.rmtree(path, ignore_errors=True)


def main():
    print(">>>", *PYTEST, flush=True)
    tmp = Path("tmp").resolve()
    env = dict(os.environ)
    env.update(PYTHONDONTWRITEBYTECODE="1")
    env["TMP"] = env["TEMP"] = str(tmp / "TEMP")
    shutil.copytree(Path("tests").resolve(), tmp / "tests")
    proc = psutil.Popen([*PYTEST], cwd=str(tmp), env=env)
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

    clean(tmp)

    return rc


if __name__ == "__main__":
    sys.exit(main())
