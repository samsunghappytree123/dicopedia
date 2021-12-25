import discord
import asyncio
import datetime
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
from utils.database import USER_DATABASE, WIKI_DATABASE


class Wiki(commands.Cog, name="위키"):
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger

    @cog_ext.cog_slash(
        name="생성",
        description="새로운 문서를 생성해요.",
        options=[
            create_option(
                name="제목",
                description="생성할 문서의 제목을 입력해주세요.",
                option_type=3,
                required=True,
            ),
        ],
    )
    async def doc_create(self, ctx, 제목: str):
        if (await WIKI_DATABASE.wiki_find(제목, ctx.author.id)) != None:
            embed = Embed.warn(
                timestamp=ctx.created_at,
                description=f"이미 내용이 존재하는 문서에요.",
            )
            Embed.user_footer(embed, ctx)
            return await ctx.send(embed=embed, hidden=True)

        embed = Embed.warn(description="")
        m = await ctx.send("문서에 등록할 내용을 입력해주세요.")

        def check(content):
            return content.author == ctx.author and content.channel == ctx.channel

        try:
            content = await self.bot.wait_for("message", timeout=60, check=check)
            result = await WIKI_DATABASE.wiki_create(제목, content.content, ctx.author.id)
            if result["status"] == "success":
                embed = Embed.default(
                    timestamp=ctx.created_at,
                    description=f"성공적으로 문서가 생성되었어요.",
                )
                Embed.user_footer(embed, ctx)
                await m.delete()
                return await ctx.send(embed=embed, hidden=True)
            else:
                embed = Embed.error(
                    timestamp=ctx.created_at,
                    description=f"문서 생성을 실패하였습니다.\n다시 시도해주세요.\n\n실패 사유 : {result['content']}",
                )
                Embed.user_footer(embed, ctx)
                await m.delete()
                return await ctx.send(embed=embed, hidden=True)

        except asyncio.TimeoutError:
            cancel_embed = Embed.warn(
                description="시간초과로 취소되었어요.",
                timestamp=content.created_at,
            )
            Embed.user_footer(cancel_embed, ctx)
            await m.delete()
            return await ctx.send(embed=cancel_embed, hidden=True)

    @cog_ext.cog_slash(
        name="보기",
        description="문서를 확인해요.",
        options=[
            create_option(
                name="제목",
                description="생성할 문서의 제목을 입력해주세요.",
                option_type=3,
                required=True,
            ),
            create_option(
                name="편집판",
                description="확인하고 싶은 편집판을 입력해주세요. (입력하지 않을 경우 기본 편집판을 확인합니다.)",
                option_type=3,
                required=False,
            ),
        ],
    )
    async def doc_view(self, ctx, 제목: str, 편집판: int = None):
        if (await WIKI_DATABASE.wiki_find(제목, ctx.author.id)) == None:
            embed = Embed.warn(
                timestamp=ctx.created_at,
                description=f"존재하지 않는 문서에요.",
            )
            Embed.user_footer(embed, ctx)
            return await ctx.send(embed=embed, hidden=True)

        result = await WIKI_DATABASE.wiki_content_find(제목, 편집판, ctx.author.id)

        if result["status"] == "failed":
            embed = Embed.warn(description=result["content"])
            Embed.user_footer(embed, ctx)
            return await ctx.send(embed=embed)
        embed = Embed.default(
            title=f"{result['title']} (r{result['r']}판)",
            description=result["content"]["content"],
            timestamp=result["content"]["updated_at"] - datetime.timedelta(hours=9),
        )
        embed.set_footer(text=f"작성자 ID : {result['content']['author']}")
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="수정",
        description="작성된 문서를 수정해요.",
        options=[
            create_option(
                name="제목",
                description="수정할 문서의 제목을 입력해주세요.",
                option_type=3,
                required=True,
            ),
        ],
    )
    async def doc_modify(self, ctx, 제목: str):
        doc = await WIKI_DATABASE.wiki_find(제목, ctx.author.id)
        if doc == None:
            embed = Embed.warn(
                description="존재하지 않는 문서에요.\n해당 제목을 가진 문서를 생성하시겠어요?",
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
            target = await ctx.send(
                embed=embed, components=[create_actionrow(*buttons)]
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
                embed = Embed.default(
                    title="✅ 문서 생성이 완료되었어요.",
                    description=f"문서에 입력할 내용을 입력해주세요.",
                    timestamp=ctx.created_at,
                )
                Embed.user_footer(embed, ctx)
                await target.edit(embed=embed, components=[])

                def check(content):
                    return (
                        content.author == ctx.author and content.channel == ctx.channel
                    )

                try:
                    content = await self.bot.wait_for(
                        "message", timeout=60, check=check
                    )
                    result = await WIKI_DATABASE.wiki_create(
                        제목, content.content, ctx.author.id
                    )
                    if result["status"] == "success":
                        embed = Embed.default(
                            timestamp=ctx.created_at,
                            description=f"성공적으로 문서가 생성되었어요.",
                        )
                        Embed.user_footer(embed, ctx)
                        await target.delete()
                        return await ctx.send(embed=embed, hidden=True)
                    else:
                        embed = Embed.error(
                            timestamp=ctx.created_at,
                            description=f"문서 생성을 실패하였습니다.\n다시 시도해주세요.\n\n실패 사유 : {result['content']}",
                        )
                        Embed.user_footer(embed, ctx)
                        await target.delete()
                        return await ctx.send(embed=embed, hidden=True)
                except asyncio.TimeoutError:
                    cancel_embed = Embed.warn(
                        description="시간초과로 취소되었어요.",
                        timestamp=ctx.created_at,
                    )
                    Embed.user_footer(cancel_embed, ctx)
                    return await target.edit(embed=cancel_embed, components=[])
            except asyncio.TimeoutError:
                cancel_embed = Embed.warn(
                    description="시간초과로 취소되었어요.",
                    timestamp=ctx.created_at,
                )
                Embed.user_footer(cancel_embed, ctx)
                return await target.edit(embed=cancel_embed, components=[])

        embed = Embed.default(
            description=f"`{doc['content']['_id']}` 문서에 넣을 내용을 입력해주세요.",
            timestamp=ctx.created_at,
        )
        m = await ctx.send(embed=embed)

        def check(content):
            return content.author == ctx.author and content.channel == ctx.channel

        try:
            content = await self.bot.wait_for("message", timeout=60, check=check)
            result = await WIKI_DATABASE.wiki_edit(제목, content.content, ctx.author.id)
            if result["status"] == "success":
                embed = Embed.default(
                    description=f"성공적으로 문서가 수정되었어요.",
                    timestamp=ctx.created_at,
                )
                Embed.user_footer(embed, ctx)
                await m.delete()
                return await ctx.send(embed=embed, hidden=True)
            else:
                embed = Embed.error(
                    description=f"문서 수정을 실패하였습니다.\n다시 시도해주세요.\n\n실패 사유 : {result['content']}",
                    timestamp=ctx.created_at,
                )
                Embed.user_footer(embed, ctx)
                await m.delete()
                return await ctx.send(embed=embed, hidden=True)
        except asyncio.TimeoutError:
            cancel_embed = Embed.warn(
                description="시간초과로 취소되었어요.",
                timestamp=content.created_at,
            )
            Embed.user_footer(cancel_embed, ctx)
            await m.delete()
            return await ctx.send(embed=cancel_embed, hidden=True)


def setup(bot):
    bot.add_cog(Wiki(bot))
