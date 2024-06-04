#! usr/bin/env python3
# countsync.py

import time
import numpy as np
import asyncio

def count():
    print("One")
    time.sleep(1)
    print("Two")

def main():
    for _ in range(3):
        count()

async def archiver():
    myArchive = []
    try:
        print("[ ", end="")
        while True:
            processValue = np.random.random()
            myArchive.append(processValue)
            print(f"{myArchive[-1]}, ", end = "")
            await time.sleep(1)
    except KeyboardInterrupt:
        print("]", end="\n\n")
        print("Close, The archiver is stopped\n")

if __name__ == "__main__":
    s = time.perf_counter()
    asyncio.run(archiver())
    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed: 0.2f} seconds.")


