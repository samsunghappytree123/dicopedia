import asyncio
from datetime import datetime
import traceback

import discord, random
from discord.ext import commands
import discord_slash
from discord_slash.context import ComponentContext
from discord_slash import ComponentContext, SlashContext, cog_ext
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import create_actionrow, create_button, create_select, create_select_option, wait_for_component
from utils.database import USER_DATABASE, WIKI_DATABASE

from utils.embed import Embed

class Listener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info(f"📡 {self.bot.user} ({self.bot.user.id}) 준비 완료")
        await self.bot.change_presence(
            status=discord.Status.idle, activity=discord.Game("꿀잠 자는 중..")
        )
        
    @commands.Cog.listener()
    async def on_slash_command(self, ctx):
        print(f"{ctx.author}({ctx.author.id}) - {ctx.command}")

    @commands.Cog.listener()
    async def on_slash_command_error(self, ctx, error):
        ignoredError = (commands.CommandNotFound, commands.errors.CheckFailure, discord_slash.error.CheckFailure)
        if isinstance(error, ignoredError):
            return

        elif isinstance(error, commands.CommandOnCooldown):
            cooldown = int(error.retry_after)
            hours = cooldown // 3600
            minutes = (cooldown % 3600) // 60
            seconds = cooldown % 60
            time = []
            if not hours == 0:
                time.append(f"{hours}시간")
            if not minutes == 0:
                time.append(f"{minutes}분")
            if not seconds == 0:
                time.append(f"{seconds}초")
            embed = Embed.warn(
                timestamp=ctx.created_at,
                description=f"사용하신 명령어는 ``{' '.join(time)}`` 뒤에 사용하실 수 있습니다.",
            )
            Embed.user_footer(embed, ctx)
            return await ctx.send(embed=embed, hidden=True)

        elif isinstance(error, commands.MissingPermissions):
            a = ""
            for p in error.missing_perms:
                if str(p) == "manage_messages":
                    p = "메시지 관리"
                elif str(p) == "kick_members":
                    p = "멤버 추방"
                elif str(p) == "ban_members":
                    p = "멤버 차단"
                elif str(p) == "administrator":
                    p = "관리자"
                elif str(p) == "create_instant_invite":
                    p = "초대링크 생성"
                elif str(p) == "manage_channels":
                    p = "채널 관리"
                elif str(p) == "manage_guild":
                    p = "서버 관리"
                elif str(p) == "add_reactions":
                    p = "메시지 반응 추가"
                elif str(p) == "view_audit_log":
                    p = "감사 로그 보기"
                elif str(p) == "read_messages":
                    p = "메시지 읽기"
                elif str(p) == "send_messages":
                    p = "메시지 보내기"
                elif str(p) == "read_message_history":
                    p = "이전 메시지 읽기"
                elif str(p) == "mute_members":
                    p = "멤버 음소거 시키기"
                elif str(p) == "move_members":
                    p = "멤버 채널 이동시키기"
                elif str(p) == "change_nickname":
                    p = "자기자신의 닉네임 변경하기"
                elif str(p) == "manage_nicknames":
                    p = "다른유저의 닉네임 변경하기"
                elif str(p) == "manage_roles":
                    p = "역활 관리하기"
                elif str(p) == "manage_webhooks":
                    p = "웹훅크 관리하기"
                elif str(p) == "manage_emojis":
                    p = "이모지 관리하기"
                elif str(p) == "use_slash_commands":
                    p = "/ 명령어 사용"
                if p != error.missing_perms[len(error.missing_perms) - 1]:
                    a += f"{p}, "
                else:
                    a += f"{p}"
            embed = Embed.warn(
                timestamp=ctx.created_at,
                description=f"당신의 권한이 부족합니다.\n\n> 필요 권한 : {str(a)}",
            )
            Embed.user_footer(embed, ctx)
            return await ctx.send(
                embed=embed,
                hidden=True,
            )

        elif isinstance(error, commands.BotMissingPermissions):
            a = ""
            for p in error.missing_perms:
                if str(p) == "manage_messages":
                    p = "메시지 관리"
                elif str(p) == "kick_members":
                    p = "멤버 추방"
                elif str(p) == "ban_members":
                    p = "멤버 차단"
                elif str(p) == "administrator":
                    p = "관리자"
                elif str(p) == "create_instant_invite":
                    p = "초대링크 생성"
                elif str(p) == "manage_channels":
                    p = "채널 관리"
                elif str(p) == "manage_guild":
                    p = "서버 관리"
                elif str(p) == "add_reactions":
                    p = "메시지 반응 추가"
                elif str(p) == "view_audit_log":
                    p = "감사 로그 보기"
                elif str(p) == "read_messages":
                    p = "메시지 읽기"
                elif str(p) == "send_messages":
                    p = "메시지 보내기"
                elif str(p) == "read_message_history":
                    p = "이전 메시지 읽기"
                elif str(p) == "mute_members":
                    p = "멤버 음소거 시키기"
                elif str(p) == "move_members":
                    p = "멤버 채널 이동시키기"
                elif str(p) == "change_nickname":
                    p = "자기자신의 닉네임 변경하기"
                elif str(p) == "manage_nicknames":
                    p = "다른유저의 닉네임 변경하기"
                elif str(p) == "manage_roles":
                    p = "역활 관리하기"
                elif str(p) == "manage_webhooks":
                    p = "웹훅크 관리하기"
                elif str(p) == "manage_emojis":
                    p = "이모지 관리하기"
                elif str(p) == "use_slash_commands":
                    p = "/ 명령어 사용"
                if p != error.missing_perms[len(error.missing_perms) - 1]:
                    a += f"{p}, "
                else:
                    a += f"{p}"
            embed = Embed.warn(
                timestamp=ctx.created_at,
                description=f"봇의 권한이 부족합니다.\n\n> 필요 권한 : {str(a)}",
            )
            Embed.user_footer(embed, ctx)
            return await ctx.send(
                embed=embed,
            )

        elif isinstance(error, commands.MissingRequiredArgument):
            embed = Embed.warn(
                timestamp=ctx.created_at, description="필요한 값이 존재하지 않습니다."
            )
            Embed.user_footer(embed, ctx)
            return await ctx.send(
                embed=embed,
                hidden=True,
            )

        elif isinstance(error, commands.MemberNotFound):
            embed = Embed.warn(timestamp=ctx.created_at, description="존재하지 않는 멤버입니다.")
            Embed.user_footer(embed, ctx)
            return await ctx.send(
                embed=embed,
                hidden=True,
            )

        else:
            tb = traceback.format_exception(type(error), error, error.__traceback__)
            err = [line.rstrip() for line in tb]
            errstr = "\n".join(err)
            # f = open(f"logs/{code}.log", "a", encoding="utf-8")
            # f.write(f"{ctx.author}({ctx.author.id}) -{ctx.message.content}\n에러 발생 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            # f.write("\n\n")
            # f.write(errstr)
            # f.close()
            embed = Embed.error(
                timestamp=ctx.created_at, description=f"```py\n{errstr}\n```"
            )
            Embed.user_footer(embed, ctx)
            print(errstr)

            return await ctx.send(
                embed=embed,
            )

    @commands.Cog.listener()
    async def on_component(self, ctx: ComponentContext):
        if str(ctx.custom_id).startswith("report-"):
            idString = (ctx.custom_id).replace("report-", "")
            # print(idString)
            print(ctx.channel, type(ctx.channel))
            if type(ctx.channel) != discord.channel.DMChannel: await ctx.send("DM을 확인해주세요!", hidden=True)

            embed = Embed.warn(
                description = f"`{idString}` 문서에 대한 신고를 진행하셨어요.\n해당 문서가 위반한 항목을 선택해주세요.",
                timestamp = ctx.created_at,
            )
            Embed.user_footer(embed, ctx)
            
            count = 0
            selects = []
            listemoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
            reportObject = ["성적인 내용이 포함된 문서", "폭력물이 포함된 문서", "괴롭힘, 따돌림 등이 포함된 문서", "자살, 자해가 포함된 문서", "거짓 정보가 포함된 문서", "스팸, 허가되지 않은 홍보가 포함된 문서", "혐오스러운 내용의 문서", "테러와 관련된 문서", "대한민국에서 불법적인 내용을 다룬 문서", "다른 문제 (기타)"]
            
            for i in reportObject:
                count += 1
                if count > 10: break
                selects.append(create_select_option(value=str(i), emoji=listemoji[count-1], label=i, default=False))
            selects.append(create_select_option(value="취소하기", emoji="❌", label="취소하기", default=False))
            select = create_select(
                options=selects,
                placeholder="위반 항목을 선택하세요.",
                min_values=0,
                max_values=1,
            )
            m = await ctx.author.send(embed=embed, components = [create_actionrow(select)])
            def Ccheck(res):
                return (
                    res.author_id == ctx.author.id
                    and res.channel == m.channel
                    and res.origin_message_id == m.id
                )

            try:
                res: ComponentContext = await wait_for_component(
                    self.bot, messages=m, check=Ccheck, timeout=60.0
                )
                if str(res.custom_id) == "cancel":
                    embed = Embed.warn(description="사용자에 의해 취소되었어요.", timestamp=ctx.created_at)
                    Embed.user_footer(embed, ctx)
                    return await m.edit(
                        embed=embed,
                        components=[],
                    )
            except asyncio.TimeoutError:
                cancel_embed = Embed.warn(
                    description="시간초과로 취소되었어요.",
                    timestamp=ctx.created_at,
                )
                Embed.user_footer(cancel_embed, ctx)
                return await m.edit(embed=cancel_embed, components=[])

            if str(res.custom_id) == "다른 문제 (기타)":
                def mCheck(content):
                    return ctx.author == content.author and ctx.channel == content.channel
                
                content = await self.bot.wait_for("message", timeout=60, check=mCheck)
                embed = Embed.default(
                    title = "신고 진행",
                    description = f"``{idString}`` 문서를 ```\n{content.content}\n```사유로 신고하시겠어요?",
                    timestamp = ctx.created_at
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
                await ctx.author.send(embed=embed, components = [create_actionrow(*buttons)])
                
                try:
                    res: ComponentContext = await wait_for_component(
                        self.bot,
                        components = create_actionrow(*buttons),
                        check = Ccheck,
                        timeout=60.0
                    )
                    if res.custom_id == "no":
                        cancel_embed = Embed.warn(
                            description="사용자에 의해 취소되었어요.",
                            timestamp=ctx.created_at,
                        )
                        Embed.user_footer(cancel_embed, ctx)
                        return await m.edit(embed=cancel_embed, components=[])

                except asyncio.TimeoutError:
                    cancel_embed = Embed.warn(
                        description="시간초과로 취소되었어요.",
                        timestamp=ctx.created_at,
                    )
                    Embed.user_footer(cancel_embed, ctx)
                    return await m.edit(embed=cancel_embed, components=[])
                reportType = content.content
            else:
                reportType = str(res.custom_id)
            
            result = await WIKI_DATABASE.wiki_add_report(idString, reportType, ctx.author.id)
            if result["status"] == "success":
                embed = Embed.default(
                    title="✅ 신고 접수 완료.",
                    description=result["content"],
                    timestamp=ctx.created_at,
                )
            else:
                embed = Embed.error(
                    description = f"신고 접수에 실패했어요\n{result['content']}",
                    timestamp = ctx.created_at
                )
            Embed.user_footer(embed, ctx)
            await m.edit(embed = embed, components = [])
        elif str(ctx.custom_id).startswith("edit-"):
            idString = str(ctx.custom_id).replace("edit-", "")
            doc2 = await WIKI_DATABASE.wiki_content_find(idString, ctx.author.id)
            embed = Embed.default(
                description=f"`{doc2['title']}` 문서에 넣을 내용을 입력해주세요.",
                timestamp=ctx.created_at,
            )
            embed.add_field(name="현재 내용", value=f"```{doc2['content']['content']}```")
            m = await ctx.send(embed=embed)

            def check(content):
                return content.author == ctx.author and content.channel == ctx.channel

            try:
                content = await self.bot.wait_for("message", timeout=60, check=check)
                if content.content == "취소":
                    return await m.edit(content="사용자에 의해 취소되었습니다.", embed = None)
                result = await WIKI_DATABASE.wiki_edit(idString, content.content, ctx.author.id)
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
    bot.add_cog(Listener(bot))