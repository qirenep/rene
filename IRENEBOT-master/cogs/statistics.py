from discord.ext import commands

from utilsmy.http1 import Fetch, PlayerNotFound
from utilsmy.embed import Embeds, NoCompetitiveStats
from classes.converters import Platform, Battletag


class Statistics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["rating"])
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def rank(self, ctx, platform: Platform, *, name: Battletag):
        """
        Returns player rank.
        Platform must be: pc, psn or xbl.
        Name must be a battletag if paltform is pc else type your console online id.
        E.g. -rank pc battletag (pc)
        E.g. -rank psn name (psn or xbl)
        Note: name and battletag are case sensitive.
        """
        async with ctx.typing():
            try:
                fetch = Fetch(platform, name)
                data = await fetch.data()
                fmt = Embeds(data, platform, name)
                if data["private"]:
                    embed = fmt.is_private(ctx)
                else:
                    embed = fmt.rank()
                return await ctx.send(embed=embed)
            except PlayerNotFound:
                await ctx.send("Account not found. Make sure you typed in the correct name.")
            except Exception as ex:
                embed = fmt.exception(ex)
                await ctx.send(embed=embed)

    @commands.command(aliases=["medals"])
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def awards(self, ctx, platform: Platform, *, name: Battletag):
        """Returns player awards."""
        async with ctx.typing():
            try:
                fetch = Fetch(platform, name)
                data = await fetch.data()
                fmt = Embeds(data, platform, name)
                if data["private"]:
                    embed = fmt.is_private(ctx)
                else:
                    embed = fmt.awards()
                return await ctx.send(embed=embed)
            except PlayerNotFound:
                await ctx.send("Account not found. Make sure you typed in the correct name.")
            except Exception as ex:
                embed = fmt.exception(ex)
                await ctx.send(embed=embed)

    @commands.command(aliases=["quick"])
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def quickplay(self, ctx, platform: Platform, *, name: Battletag):
        """Returns player quickplay stats."""
        async with ctx.typing():
            try:
                fetch = Fetch(platform, name)
                data = await fetch.data()
                fmt = Embeds(data, platform, name)
                if data["private"]:
                    embed = fmt.is_private(ctx)
                else:
                    embed = fmt._stats(ctx)
                return await ctx.send(embed=embed)
            except PlayerNotFound:
                await ctx.send("Account not found. Make sure you typed in the correct name.")
            except Exception as ex:
                embed = fmt.exception(ex)
                await ctx.send(embed=embed)

    @commands.command(aliases=["comp"])
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def competitive(self, ctx, platform: Platform, *, name: Battletag):
        """Returns player competitive stats."""
        async with ctx.typing():
            try:
                fetch = Fetch(platform, name)
                data = await fetch.data()
                fmt = Embeds(data, platform, name)
                if data["private"]:
                    embed = fmt.is_private(ctx)
                else:
                    embed = fmt._stats(ctx)
                return await ctx.send(embed=embed)
            except PlayerNotFound:
                await ctx.send("Account not found. Make sure you typed in the correct name.")
            except NoCompetitiveStats:
                await ctx.send("This profile has no competitive stats")
            except Exception as ex:
                embed = fmt.exception(ex)
                await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Statistics(bot))
