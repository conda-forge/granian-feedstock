import sys
import psutil

PYTEST = ["pytest", "-vv", "--color=yes", "--tb=long"]

SKIPS = [
    "test_reject",
    "(test_rsgi and test_body_stream_req)",
    "test_scope and workers",
]

SKIP_OR = " or ".join(SKIPS)
K = ["-k", f"not ({SKIP_OR})"]


def main():
    proc = psutil.Popen([*PYTEST])
    rc = proc.wait()
    all_procs = [*proc.children(recursive=True), proc]
    killed = []
    for p in all_procs:
        print(p, end="")
        if not p.is_running():
            print("... was not running")
            continue
        killed += [p]
        print("... killed")
    if killed:
        psutil.wait_procs(killed)
    return rc


if __name__ == "__main__":
    sys.exit(main())
