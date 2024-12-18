import asyncio
import logging
import sys

from aiogram import Router

from .config import dp, bot
from .src.start_handler import start_handler
from .src.user_handlers import handler_toyifalar, handler_buyurtmachilar, handler_requests

router = Router()


async def main() -> None:
    dp.include_router(router)
    dp.include_router(start_handler.router)
    dp.include_router(handler_toyifalar.router)
    dp.include_router(handler_buyurtmachilar.router)
    dp.include_router(handler_requests.router)
    await dp.start_polling(bot)


# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO, stream=sys.stdout)
#     asyncio.run(main())
