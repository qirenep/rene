import discord

from discord.ext import commands


class Links(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    async def support(self, ctx):
        """Returns OverBot official support server."""
        await ctx.send(self.bot.config.support)

    @commands.command()
    @commands.guild_only()
    async def vote(self, ctx):
        """Returns bot vote link."""
        await ctx.send(self.bot.config.vote)

    @commands.command()
    @commands.guild_only()
    async def invite(self, ctx):
        """Returns bot invite link."""
        await ctx.send(self.bot.config.invite)

    @commands.command(aliases=["git"])
    @commands.guild_only()
    async def github(self, ctx):
        """Returns the developer GitHub profile."""
        embed = discord.Embed(
            title="davidetacchini/OverBot",
            description="An Overwatch bot for Discord.",
            url=self.bot.config.github
        ).set_author(
            name="GitHub",
            icon_url=self.bot.config.github_logo
        ).set_thumbnail(
            url=self.bot.user.avatar_url
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Links(bot))
