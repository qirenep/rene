import discord
import asyncio

from discord.ext import commands

from utilsmy.http1 import PlayerNotFound
from utilsmy.embed import NoCompetitiveStats, exception, profile_info, group_embed
from utilsmy.database import (link_profile, unlink_profile,
                            update_profile, select, ProfileNotLinked, ProfileAlreadyLinked)
from classes.converters import Platform, Battletag
from cogs.stats import Stats


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def profile(self, ctx, commands: str = None):
        """Get usage information for 'profile' commands."""
        embed = group_embed(ctx, self.bot.get_command(ctx.command.name))
        await ctx.send(embed=embed)

    @profile.command(aliases=["bind"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def link(self, ctx):
        """Link your Overwatch profile to your Discord account."""
        embed = discord.Embed(
            title="Link your Overwatch profile to your discord ID.",
            color=self.bot.color
        )
        embed.add_field(
            name="Guide",
            value="React with the platform you play on.\nNext you will be asked for your battletag/gamertag.\nType in your battletag if you have selected '<:battlenet:679469162724196387>' else insert you gamertag."
        )
        embed.add_field(
            name="Platforms",
            value="<:battlenet:679469162724196387> - PC\n<:psn:679468542541693128> - PS4\n<:xbl:679469487623503930> - XBOX ONE",
            inline=False
        )
        msg = await ctx.send(embed=embed, delete_after=30)
        platform = await self.get_platform(ctx, msg)
        if platform is None:
            return
        await ctx.send("Type in your battletag if you selected '<:battlenet:679469162724196387>' else insert your gamertag.")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            name = await self.bot.wait_for('message', check=check, timeout=30)
        except asyncio.TimeoutError:
            await ctx.send("You took too long to reply.")
        else:
            try:
                await link_profile(ctx.author.id, platform, str(name.content).replace('#', '-'))
                await ctx.send(f"Profile successfully linked. Run `{ctx.prefix}profile info` to see your profile information.")
            except ProfileAlreadyLinked:
                await ctx.send("You have already linked a profile.")
            except Exception as ex:
                embed = exception(ex)
                await ctx.send(embed=embed)

    @profile.command(aliases=["unbind"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def unlink(self, ctx):
        """Unlink your Overwatch profile from your Discord account."""
        platform, name = await select(ctx.author.id)
        embed = discord.Embed(
            title="Unlink the Overwatch profile linked to your Discord ID.",
            color=self.bot.color
        )
        embed.add_field(
            name="Note",
            value=f"If you agree by clicking ✅, the Overwatch profile linked to your account will be removed.\nYou can always add a new one by running `{ctx.prefix}profile link`.\nBelow you can check your current data.",
            inline=False
        )
        embed.add_field(
            name="Platform",
            value=platform
        )
        embed.add_field(
            name="Name",
            value=name
        )

        msg = await ctx.send(embed=embed, delete_after=30)

        reactions = [
            "✅",
            "❌"
        ]

        for r in reactions:
            await msg.add_reaction(r)

        def check(r, u):
            rcheck = (str(r.emoji) in reactions)
            ucheck = (u == ctx.author)

            return rcheck and ucheck

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30, check=check)
            await msg.delete()
        except asyncio.TimeoutError:
            await ctx.send("You took too long to confirm.")

        if str(reaction.emoji) == "✅":
            try:
                await unlink_profile(ctx.author.id,)
                return await ctx.send("Profile successfully unlinked.")
            except Exception as ex:
                embed = exception(ex)
                await ctx.send(embed=embed)
        await ctx.send("Your profile has **NOT** been reset.")

    @profile.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def update(self, ctx, platform: Platform, name: Battletag):
        """Update your Overwatch profile linked to your Discord account."""
        try:
            await update_profile(ctx.author.id, platform, name)
            await ctx.send(f"Profile successfully updated.\nRun `{ctx.prefix}profile info` to see the changes.")
        except ProfileNotLinked:
            await ctx.send(f"No profile linked yed. Connect it by typing `{ctx.prefix}profile link`")
        except Exception as ex:
            embed = exception(ex)
            await ctx.send(embed=embed)

    @profile.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def info(self, ctx):
        """Shows your linked profile information."""
        try:
            platform, name = await select(ctx.author.id)
            embed = profile_info(ctx, platform, name)
            await ctx.send(embed=embed)
        except ProfileNotLinked:
            await ctx.send(f"Connect your profile by running `{ctx.prefix}profile link`")
        except Exception as ex:
            embed = exception(ex)
            await ctx.send(embed=embed)

    async def embed_stats(self, ctx):
        """Embeds stats for commands."""
        try:
            platform, name = await select(ctx.author.id)
            pages = await Stats.get_stats(ctx, platform, name)
            try:
                await self.bot.paginator.Paginator(extras=pages).paginate(ctx)
            except TypeError:  # if there are no pages, normal embeds
                await ctx.send(embed=pages)
        except PlayerNotFound:
            await ctx.send("Account not found. Make sure you typed in the correct name.")
        except NoCompetitiveStats:
            await ctx.send("This profile has no competitive stats")
        except ProfileNotLinked:
            await ctx.send(f"Connect your profile by running `{ctx.prefix}profile link`")
        except Exception as ex:
            embed = exception(ex)
            await ctx.send(embed=embed)

    @profile.command(aliases=["rating"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def rank(self, ctx):
        """Returns linked profiles rank."""
        async with ctx.typing():
            await self.embed_stats(ctx)

    @profile.command(aliases=["medals"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def awards(self, ctx):
        """Returns linked profiles awards."""
        async with ctx.typing():
            await self.embed_stats(ctx)

    @profile.command(aliases=["quick"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def quickplay(self, ctx):
        """Returns linked profiles quickplay stats."""
        async with ctx.typing():
            await self.embed_stats(ctx)

    @profile.command(aliases=["comp"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def competitive(self, ctx):
        """Returns linked profiles competitive stats."""
        async with ctx.typing():
            await self.embed_stats(ctx)

    async def get_platform(self, ctx, msg):
        reactions = [
            "<:battlenet:679469162724196387>",
            "<:psn:679468542541693128>",
            "<:xbl:679469487623503930>",
            "❌"
        ]

        for r in reactions:
            await msg.add_reaction(r)

        def check(r, u):
            rcheck = (str(r.emoji) in reactions)
            ucheck = (u == ctx.author)

            return rcheck and ucheck

        try:
            reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=30)
            await msg.delete()
        except asyncio.TimeoutError:
            await ctx.send("You took too long to confirm.")

        if str(reaction.emoji) == "<:battlenet:679469162724196387>":
            return "pc"
        elif str(reaction.emoji) == "<:psn:679468542541693128>":
            return "psn"
        elif str(reaction.emoji) == "<:xbl:679469487623503930>":
            return "xbl"
        else:
            return


def setup(bot):
    bot.add_cog(Profile(bot))
