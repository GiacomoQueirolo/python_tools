## logs to find memory leaks

import os
import psutil,tracemalloc

def log_memory(label=""):
    proc = psutil.Process(os.getpid())
    mb = proc.memory_info().rss / 1024**2
    print(f"[MEM] {label}: {mb:.0f} MB", flush=True)

# note: for the following it has to be preceded by
# tracemalloc.start()
# somewhere in the code
def log_top_allocs(label="", n=5):
    # and for tracking the top allocations:
    snapshot = tracemalloc.take_snapshot()
    stats    = snapshot.statistics("lineno")
    print(f"[TRACEMALLOC {label}]")
    for s in stats[:n]:
        print(f"  {s}")

