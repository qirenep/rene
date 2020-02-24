from discord.ext import commands

from utilsmy.http1 import Fetch, PlayerNotFound
from utilsmy.embed import Embeds, NoCompetitiveStats, exception
from classes.converters import Platform, Battletag


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def get_stats(ctx, platform, name):
        """Get players stats."""
        cmd = str(ctx.command.name).lower()
        fetch = Fetch(platform, name)
        data = await fetch.data()
        fmt = Embeds(data, platform, name)
        if data["private"]:
            return fmt.is_private(ctx)
        if cmd == "rank":
            return fmt.rank()
        elif cmd == "awards":
            return fmt.awards()
        return fmt._stats(ctx)

    async def embed_stats(self, ctx, platform, name):
        """Returns players formatted stats."""
        try:
            pages = await self.get_stats(ctx, platform, name)
            try:
                await self.bot.paginator.Paginator(extras=pages).paginate(ctx)
            except TypeError:  # if there are no pages, normal embeds
                await ctx.send(embed=pages)
        except PlayerNotFound:
            await ctx.send("Account not found. Make sure you typed in the correct name.")
        except NoCompetitiveStats:
            await ctx.send("This profile has no competitive stats")
        except Exception as ex:
            embed = exception(ex)
            await ctx.send(embed=embed)

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
            await self.embed_stats(ctx, platform, name)

    @commands.command(aliases=["medals"])
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def awards(self, ctx, platform: Platform, *, name: Battletag):
        """Returns player awards."""
        async with ctx.typing():
            await self.embed_stats(ctx, platform, name)

    @commands.command(aliases=["quick"])
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def quickplay(self, ctx, platform: Platform, *, name: Battletag):
        """Returns player quickplay stats."""
        async with ctx.typing():
            await self.embed_stats(ctx, platform, name)

    @commands.command(aliases=["comp"])
    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def competitive(self, ctx, platform: Platform, *, name: Battletag):
        """Returns player competitive stats."""
        async with ctx.typing():
            await self.embed_stats(ctx, platform, name)


def setup(bot):
    bot.add_cog(Stats(bot))
