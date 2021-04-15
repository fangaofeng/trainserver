import asyncio
import time


async def say_after(delay, what):
    await asyncio.sleep(delay)
    print(what)


async def nested():
    return 42


async def main():
    task1 = asyncio.create_task(
        say_after(1, 'hello'))

    task2 = asyncio.create_task(
        say_after(2, 'world'))

    print(f"started at {time.strftime('%X')}")

    # Wait until both tasks are completed (should take
    # around 2 seconds.)
    await task1
    print('we22')
    await task2
    print('we')
    # await say_after(1, 'hello')
    # await say_after(2, 'world')
    print(f"finished at {time.strftime('%X')}")
# async def main():
#     # Nothing happens if we just call "nested()".
#     # A coroutine object is created but not awaited,
#     # so it *won't run at all*.
#         # with "main()".
#     task = asyncio.create_task(nested())

#     # "task" can now be used to cancel "nested()", or
#     # can simply be awaited to wait until it is complete:
#     ttt = await task

#     # Let's do it differently now and await it:
#     print(ttt)  # will print "42".
#     print(34)
asyncio.run(main())
