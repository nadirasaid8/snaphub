import sys
import asyncio

from src.core import main
from src.deeplchain import mrh, log, _banner,_clear

if __name__ == "__main__":
    _clear()
    _banner()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log(mrh + f"Bot interrupted by user.")
        sys.exit()