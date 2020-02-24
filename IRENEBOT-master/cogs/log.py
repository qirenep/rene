import textwrap
import traceback

import discord

from discord.ext import commands


class Log(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command(self, ctx):
        await self.send_log(ctx)

    async def send_log(self, ctx):
        """Command logs on OverBot support server."""
        if ctx.command.name in ['rank', 'awards', 'competitive', 'quickplay']:
            ch = self.bot.get_channel(639731647243354114)
            message = ctx.message.content
        elif ctx.command.name == 'feedback':
            ch = self.bot.get_channel(639731647243354114)
            # getting the lenght of the prefix + cmd name to avoid priting it
            i = len(ctx.prefix) + len(ctx.command.name)
            message = ctx.message.content[i:]
        else:
            return

        embed = discord.Embed(
            color=self.bot.color,
            timestamp=self.bot.timestamp
        )
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_author(
            name=f"{ctx.author}",
            icon_url=f"{ctx.author.avatar_url}"
        )
        embed.add_field(
            name="Guild",
            value=f"{ctx.guild}",
            inline=True
        )
        embed.add_field(
            name="Channel",
            value=f"{ctx.message.channel}",
            inline=True
        )
        embed.add_field(
            name="Message",
            value=f"{message}",
            inline=False
        )
        await ch.send(embed=embed)

    async def send_server_log(self, em, guild):
        """Sends information about a joined guild."""
        ch = self.bot.get_channel(639731647243354114)
        em.title = guild.name
        em.set_thumbnail(url=guild.icon_url)
        em.add_field(name="Owner", value=guild.owner)
        em.add_field(name="Guild ID", value=guild.id)
        em.add_field(name="Region", value=guild.region)
        em.add_field(name="Members", value=guild.member_count)
        em.add_field(name="Channels", value=len(guild.channels))
        em.add_field(name="Roles", value=len(guild.roles))
        em.add_field(name="Premium Tier", value=guild.premium_tier)
        await ch.send(embed=em)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        embed = discord.Embed(color=0x4ca64c)
        await self.send_server_log(embed, guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        embed = discord.Embed(color=0xff3232)
        await self.send_server_log(embed, guild)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if not isinstance(error, (commands.CommandInvokeError, commands.ConversionError)):
            return

        error = error.original
        if isinstance(error, (discord.Forbidden, discord.NotFound)):
            return

        ch = self.bot.get_channel(639731647243354114)
        embed = discord.Embed(title="Error", color=0xff3232)
        embed.add_field(name="Command", value=ctx.command.qualified_name)
        embed.add_field(name="Author", value=ctx.author)

        fmt = f"Channel: {ctx.channel} (ID: {ctx.channel.id})"
        if ctx.guild:
            fmt = f"{fmt}\nGuild: {ctx.guild} (ID: {ctx.guild.id})"

        embed.add_field(name="Location", value=fmt, inline=False)
        embed.add_field(name="Content", value=textwrap.shorten(
            ctx.message.content, width=512))

        ex = "".join(traceback.format_exception(
            type(error), error, error.__traceback__, chain=False))
        embed.description = f"```py\n{ex}\n```"
        embed.timestamp = self.bot.timestamp
        await ch.send(embed=embed)


