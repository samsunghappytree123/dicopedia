import discord


class Embed(discord.Embed):
    def default(title: str = None, description: str = None, **kwargs):
        embed = discord.Embed(**kwargs, color=0x5865F2)
        if not title is None:
            embed.title = title
        if not description is None:
            embed.description = description
        return embed

    def warn(description: str, **kwargs):
        embed = discord.Embed(
            **kwargs,
            colour=discord.Colour.gold(),
            title="⚠ 경고",
            description=description
        )
        return embed

    def error(description: str, **kwargs):
        embed = discord.Embed(
            **kwargs, color=0xFF0000, title="⚠ 오류 발생", description=description
        )
        return embed

    def user_footer(embed, ctx):
        return embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url)
