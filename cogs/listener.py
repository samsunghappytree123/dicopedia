import traceback

import discord
from discord.ext import commands

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
    async def on_slash_command_error(self, ctx, error):
        ignoredError = (commands.CommandNotFound, commands.errors.CheckFailure)
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
            embed = Embed.error(
                timestamp=ctx.created_at, description=f"```py\n{errstr}\n```"
            )
            Embed.user_footer(embed, ctx)
            return await ctx.send(
                embed=embed,
            )


def setup(bot):
    bot.add_cog(Listener(bot))
