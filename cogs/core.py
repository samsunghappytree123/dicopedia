import datetime

import discord
from discord.ext import commands
from discord_slash import SlashContext, cog_ext
from discord_slash.model import ButtonStyle, SlashCommandPermissionType
from discord_slash.utils.manage_commands import create_choice, create_option
from discord_slash.utils.manage_components import (
    create_actionrow,
    create_button,
    wait_for_component,
)

from utils.embed import Embed


class Core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger

    @cog_ext.cog_slash(
        name="핑",
        description="봇의 응답 시간을 확인해요.",
    )
    async def ping(self, ctx):
        now: datetime = ctx.created_at
        embed = Embed.default(title="🏓 Pinging...", timestamp=ctx.created_at)
        Embed.user_footer(embed, ctx)
        target = await ctx.send(embed=embed)
        target_time: datetime = target.created_at
        msg_ping = target_time - now
        embed = Embed.default(
            title="🏓 Pong!",
            description=f"``Discord API LATENCY`` : {round(self.bot.latency * 1000)}ms\n``Discord MESSAGE Ping`` : {int(msg_ping.total_seconds() * 1000)}ms",
            timestamp=ctx.created_at,
        )
        Embed.user_footer(embed, ctx)
        await target.edit(
            embed=embed,
        )

    @cog_ext.cog_slash(
        name="개발자",
        description="봇의 개발자를 확인해요.",
    )
    async def dev_check(self, ctx):
        owner = ""
        for i in self.bot.owner_ids:
            owner += f"{self.bot.get_user(i)} ({i})\n"

        embed = Embed.default(
            timestamp=ctx.created_at,
            title=f"{self.bot.user.name} 개발자",
            description=f"```{owner}```",
        )
        Embed.user_footer(embed, ctx)
        await ctx.send(embed=embed)

    @commands.command(name="hellothisisverification")
    async def dev_check_msg(self, ctx):
        owner = ""
        for i in self.bot.owner_ids:
            owner += f"{self.bot.get_user(i)} ({i})\n"

        embed = Embed.default(
            timestamp=ctx.message.created_at,
            title=f"{self.bot.user.name} 개발자",
            description=f"```{owner}```",
        )
        Embed.user_footer(embed, ctx)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Core(bot))
