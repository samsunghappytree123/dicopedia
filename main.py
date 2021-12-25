import os

import colorlog
import config
import discord
import jishaku
from config import LOGGER as logger
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext


class Bot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=discord.Intents.all(),
            owner_ids=config.OWNER_IDS,
            help_command=None,
        )
        slash = SlashCommand(self, sync_commands=True)

        self.logger = logger
        self.config = config

        try:
            self.load_extension("jishaku")
            logger.info(f"✅ jishaku 로드 완료")
        except:
            logger.error(f"❎ jishaku 로드 실패")

        for filename in os.listdir("cogs"):
            if filename.endswith(".py"):
                try:
                    self.load_extension(f"cogs.{filename[:-3]}")
                    logger.info(f"✅ {filename} 로드 완료")
                except Exception as e:
                    logger.error(f"❎ {filename} 로드 실패 ({e})")

    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_commands(message)


def setup_logger():
    logger.setLevel("DEBUG")
    handler = colorlog.StreamHandler()
    handler.setFormatter(
        colorlog.ColoredFormatter(
            "{log_color}{asctime} {message}", "[%y-%m-%d %H:%M:%S]", style="{"
        )
    )
    logger.addHandler(handler)
    logger.debug("Logging enabled")
    return logger


if __name__ == "__main__":
    setup_logger()
    bot = Bot()
    bot.run(config.BOT_TOKEN, reconnect=True)
