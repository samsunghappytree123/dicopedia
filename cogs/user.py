import discord
import asyncio
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.utils.manage_components import (
    create_button,
    create_actionrow,
    wait_for_component,
)
from discord_slash.model import ButtonStyle, SlashCommandPermissionType
from utils.embed import Embed
from utils.database import USER_DATABASE


class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger

    @cog_ext.cog_slash(
        name="가입",
        description="봇의 서비스에 가입해요.",
    )
    async def register(self, ctx):
        if await USER_DATABASE.user_find(ctx.author.id):
            embed = Embed.warn(
                timestamp=ctx.created_at,
                description=f"이미 {self.bot.user.name} 서비스에 가입되어 있어요.",
            )
            Embed.user_footer(embed, ctx)
            return await ctx.send(embed=embed, hidden=True)
        embed = Embed.default(
            title="서비스 가입",
            description="암튼 내용임 ㅇㅇ",
            timestamp=ctx.created_at,
        )
        Embed.user_footer(embed, ctx)
        buttons = [
            create_button(
                style=ButtonStyle.green,
                emoji="✅",
                label="네",
                custom_id="yes",
            ),
            create_button(
                style=ButtonStyle.red,
                emoji="❎",
                label="아니오",
                custom_id="no",
            ),
        ]
        target = await ctx.send(embed=embed, components=[create_actionrow(*buttons)])

        def check(res):
            return (
                res.author_id == ctx.author.id
                and res.channel == ctx.channel
                and res.origin_message_id == target.id
            )

        try:
            res: ComponentContext = await wait_for_component(
                self.bot,
                components=create_actionrow(*buttons),
                check=check,
                timeout=60.0,
            )
            if res.custom_id == "no":
                cancel_embed = Embed.warn(
                    description="사용자에 의해 취소되었어요.",
                    timestamp=ctx.created_at,
                )
                Embed.user_footer(cancel_embed, ctx)
                return await target.edit(embed=cancel_embed, components=[])
        except asyncio.TimeoutError:
            cancel_embed = Embed.warn(
                description="시간 초과로 취소되었어요.",
                timestamp=ctx.created_at,
            )
            Embed.user_footer(cancel_embed, ctx)
            return await target.edit(embed=cancel_embed, components=[])
        await USER_DATABASE.user_add(ctx.author.id)
        embed = Embed.default(
            title="✅ 서비스 가입이 완료되었어요.",
            description=f"``{self.bot.user.name} 서비스``에 가입이 완료되었어요!",
            timestamp=ctx.created_at,
        )
        Embed.user_footer(embed, ctx)
        await target.edit(embed=embed, components=[])

    @cog_ext.cog_slash(
        name="정보수정",
        description="사용자의 정보를 수정해요. 6시간마다 한 번씩 변경이 가능해요.",
        options=[
            create_option(
                name="설명",
                description="변경할 사용자 설명을 입력해주세요. 최대 30자까지 가능해요.",
                option_type=3,
                required=True,
            ),
        ],
    )
    @commands.cooldown(1, 21600, commands.BucketType.user)
    async def modify(self, ctx, 설명: str):
        if not (await USER_DATABASE.user_find(ctx.author.id)):
            embed = Embed.warn(
                timestamp=ctx.created_at,
                description=f"서비스에 가입되어있지 않아요. 가입하시겠어요?",
            )
            Embed.user_footer(embed, ctx)
            buttons = [
                create_button(
                    style=ButtonStyle.green,
                    emoji="✅",
                    label="네",
                    custom_id="yes",
                ),
                create_button(
                    style=ButtonStyle.red,
                    emoji="❎",
                    label="아니오",
                    custom_id="no",
                ),
            ]
            target = await ctx.send(
                embed=embed, hidden=True, components=[create_actionrow(*buttons)]
            )

            def check(res):
                return (
                    res.author_id == ctx.author.id
                    and res.channel == ctx.channel
                    and res.origin_message_id == target.id
                )

            try:
                res: ComponentContext = await wait_for_component(
                    self.bot,
                    components=create_actionrow(*buttons),
                    check=check,
                    timeout=60.0,
                )
                if res.custom_id == "no":
                    cancel_embed = Embed.warn(
                        description="사용자에 의해 취소되었어요.",
                        timestamp=ctx.created_at,
                    )
                    Embed.user_footer(cancel_embed, ctx)
                    ctx.message = ctx
                    self.bot.slash.commands[ctx.name].reset_cooldown(ctx)
                    return await target.edit(embed=cancel_embed, components=[])
            except asyncio.TimeoutError:
                cancel_embed = Embed.warn(
                    description="시간초과로 취소되었어요.",
                    timestamp=ctx.created_at,
                )
                Embed.user_footer(cancel_embed, ctx)
                ctx.message = ctx
                self.bot.slash.commands[ctx.name].reset_cooldown(ctx)
                return await target.edit(embed=cancel_embed, components=[])
            await USER_DATABASE.user_add(ctx.author.id)
            embed = Embed.default(
                title="✅ 서비스 가입이 완료되었어요.",
                description=f"``{self.bot.user.name} 서비스``에 가입이 완료되었어요!",
                timestamp=ctx.created_at,
            )
            Embed.user_footer(embed, ctx)
            await target.edit(embed=embed, components=[])

        embed = Embed.default(
            title="정보 수정",
            description=f"사용자의 설명을 ``{설명}``으로 변경하시겠어요?",
            timestamp=ctx.created_at,
        )
        buttons = [
            create_button(
                style=ButtonStyle.green,
                emoji="✅",
                label="네",
                custom_id="yes",
            ),
            create_button(
                style=ButtonStyle.red,
                emoji="❎",
                label="아니오",
                custom_id="no",
            ),
        ]

        target = await ctx.send(embed=embed, components=[create_actionrow(*buttons)])

        def check(res):
            return (
                res.author_id == ctx.author.id
                and res.channel == ctx.channel
                and res.origin_message_id == target.id
            )

        try:
            res: ComponentContext = await wait_for_component(
                self.bot,
                components=create_actionrow(*buttons),
                check=check,
                timeout=60.0,
            )
            if res.custom_id == "no":
                cancel_embed = Embed.warn(
                    description="사용자에 의해 취소되었어요.",
                    timestamp=ctx.created_at,
                )
                Embed.user_footer(cancel_embed, ctx)
                ctx.message = ctx
                self.bot.slash.commands[ctx.name].reset_cooldown(ctx)
                return await target.edit(embed=cancel_embed, components=[])
        except asyncio.TimeoutError:
            cancel_embed = Embed.warn(
                description="시간초과로 취소되었어요.",
                timestamp=ctx.created_at,
            )
            Embed.user_footer(cancel_embed, ctx)
            ctx.message = ctx
            self.bot.slash.commands[ctx.name].reset_cooldown(ctx)
            return await target.edit(embed=cancel_embed, components=[])
        result = await USER_DATABASE.user_edit_description(ctx.author.id, 설명)
        if result["status"] == "success":
            embed = Embed.default(
                title="✅ 정보 변경이 완료되었어요.",
                description=f"``{ctx.author}``님의 설명을 ``{설명}``으로 변경하였어요!",
                timestamp=ctx.created_at,
            )
        else:
            embed = Embed.default(
                title="❎ 정보 변경에 실패했어요.",
                description=f"{result['content']}",
                timestamp=ctx.created_at,
            )
        Embed.user_footer(embed, ctx)
        await target.edit(embed=embed, components=[])

    @cog_ext.cog_slash(
        name="정보",
        description="사용자의 정보를 확인합니다.",
        options=[
            create_option(
                name="유저", description="확인할 유저를 맨션하세요.", option_type=6, required=False
            )
        ],
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def user_find(self, ctx, 유저=None):
        if 유저 is None:
            유저 = ctx.author
        user = await USER_DATABASE.user_find(유저.id)
        if user is None:
            embed = Embed.default(
                title="사용자 정보",
                description=f"``{self.bot.get_user(유저.id).name}``님은 서비스에 가입하지 않았어요.",
                timestamp=ctx.created_at,
            )
            Embed.user_footer(embed, ctx)
            return await ctx.send(embed=embed)
        embed = Embed.default(
            title="사용자 정보",
            description=f"``{self.bot.get_user(user['_id']).name}``님의 정보입니다.",
            timestamp=ctx.created_at,
        )
        embed.set_thumbnail(url=self.bot.get_user(user["_id"]).avatar_url)
        embed.add_field(
            name="유저명",
            value=f"{self.bot.get_user(user['_id']).name}#{self.bot.get_user(user['_id']).discriminator}",
            inline=False,
        )
        embed.add_field(
            name="유저 소개",
            value=user["description"],
            inline=False,
        )
        embed.add_field(
            name=f"{self.bot.user.name} 가입일",
            value=user["created_at"].strftime("%Y년 %m월 %d일 %H시 %M분 %S초"),
            inline=False,
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(User(bot))
