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

#! usr/bin/env python3
# countsync.py
import asyncio

async def get_some_values_from_io():
    alfa = [3]
    alfa.append(2)
    await asyncio.sleep(1)
    return alfa
        
vals = []

async def fetcher():
    io_vals = ['a','a']
    while True:
        
        io_vals = await get_some_values_from_io()
        print('A')
        for val in io_vals:
            vals.append(val)

async def monitor():
    while True:
        print (len(vals))
        print(vals)

        await asyncio.sleep(1)

async def main():
    await asyncio.gather(fetcher(), monitor())

##asyncio.run(main())

async def counter(name: str):
    for i in range(0, 100):
        print(f"{name}: {i!s}")
        await asyncio.sleep(0)

async def main():
    tasks = []
    for n in range(0, 4):
        tasks.append(asyncio.create_task(counter(f"task{n}")))

    while True:
        tasks = [t for t in tasks if not t.done()]
        if len(tasks) == 0:
            return

        await tasks[0]

asyncio.run(main())


