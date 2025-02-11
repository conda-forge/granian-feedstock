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
    failed = 0
    for p in reversed([path, *sorted(path.rglob("*"))]):
        print(f"... {p}")
        try:
            p.chmod(0o777)
            if p.is_dir():
                shutil.rmtree(p, ignore_errors=True)
            elif p.is_file():
                p.unlink()
        except Exception as err:
            print(f"!!! {err}", flush=True)
            failed += 1
    try:
        if path.exists():
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
    tmp = Path("_tmp").resolve()
    tmp.mkdir()
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

    clean(tmp, 3)

    return rc


if __name__ == "__main__":
    sys.exit(main())
