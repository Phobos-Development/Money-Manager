import asyncio
import logging.handlers
import os
import sys

import discord
from discord.ext import commands

import config
from utils.database_handler import create_connection
from utils.database_handler import query_sql
from utils.database_handler import setup


class IncomeBot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            command_prefix="i!",
            case_insensitive=True,
            intents=discord.Intents.all(),
        )
        self.logger = logging.getLogger("bot")
        self.ready = False
        self.channels = query_sql(
            create_connection(), f"SELECT channel_id FROM income_channels", one=False
        )
        if self.channels is not None:
            self.channels = [channel[0] for channel in self.channels]

    @staticmethod
    def setup_logging() -> None:
        logging.getLogger("discord").setLevel(logging.INFO)
        logging.getLogger("discord.http").setLevel(logging.WARNING)
        logging.basicConfig(
            level=logging.INFO,
            format="%(levelname)s | %(asctime)s | %(name)s | %(message)s",
            stream=sys.stdout,
        )

    async def load_cogs(self, directory="./cogs") -> None:
        for file in os.listdir(directory):
            if file.endswith(".py") and not file.startswith("_"):
                await self.load_extension(
                    f"{directory[2:].replace('/', '.')}.{file[:-3]}"
                )
                self.logger.info(f"Loaded: {file[:-3]}")
            elif not (
                file in ["__pycache__"] or file.endswith(("pyc", "txt"))
            ) and not file.startswith("_"):
                await self.load_cogs(f"{directory}/{file}")

    async def on_ready(self):
        if not self.ready:
            await self.load_cogs()
            self.ready = True

    async def on_command_error(self, ctx, error):
        ignored = (
            commands.CommandNotFound,
            commands.DisabledCommand,
            commands.NoPrivateMessage,
            commands.CheckFailure,
        )

        if isinstance(error, ignored):
            return

        if hasattr(ctx.command, "on_error"):
            return

        error = getattr(error, "original", error)

        raise error


if __name__ == "__main__":
    bot = IncomeBot()
    bot.setup_logging()
    setup()
    bot.remove_command("help")
    bot.run(config.TOKEN)
