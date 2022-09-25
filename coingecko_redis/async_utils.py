import asyncio
from functools import partial, wraps
from typing import Any


def wrap_async(func: Any) -> Any:
    """Wraps sync functions and makes them async

    Args:
        func (func): function to wrap and make async

    Returns:
        func: async function
    """

    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)

    return run
