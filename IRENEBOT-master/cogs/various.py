import psutil
import distro
import platform

import discord

from discord.ext import commands


license_file = open("LICENSE", "r").read()


class Various(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["pong"])
    @commands.guild_only()
    async def ping(self, ctx):
        """Displays the bot's current websocket latency."""
        embed = discord.Embed(
            title="Heartbeat",
            description=self.bot.ping,
            color=self.bot.color
        )
        await ctx.send(embed=embed)

    # i don't even know why i created this command, but i'll leave it
    @commands.command(name="license")
    @commands.guild_only()
    async def _license(self, ctx):
        """Returns bot license."""
        await ctx.send("""
```text
{license}
```""".format(license=license_file)
        )

    @commands.command()
    @commands.guild_only()
    async def feedback(self, ctx, *, message: str):
        """Send a feedback/bug to the developer."""
        await ctx.message.delete()
        await ctx.send(f"{ctx.author.name}, thank you for your feedback!")

    @commands.command()
    @commands.guild_only()
    async def stats(self, ctx):
        """Displays the bot's statistics."""
        cpu_perc = psutil.cpu_percent()
        cores = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()[0]
        cpu_freq_conv = cpu_freq / 1000  # converted into GHz, default value is given in MHz
        ram = psutil.virtual_memory()
        os_name = distro.linux_distribution()[0]
        os_version = distro.linux_distribution()[1]

        host_stats = f"CPU Usage: **{cpu_perc}**%, **{cores}** cores @ **{round(cpu_freq_conv, 2)}** GHz\n" \
            f"Ram Usage: **{ram[2]}**%\n" \
            f"Operating System: **{os_name} {os_version}**\n" \
            f"Python Version: **{platform.python_version()}**\n" \
            f"Discord.py Version: **{discord.__version__}**"

        bot_stats = f"Developed by <@{self.bot.owner_id}>\n" \
            f"Commands used: **{self.bot.commands_used}**\n" \
            f"Lines of code: **{self.bot.linecount}**\n" \
            f"Uptime: **{self.bot.uptime}**\n" \
            f"Ping: **{self.bot.ping}**\n" \
            f"Shards: **{self.bot.shard_count}**"

        desc = f"Currently serving **{len(self.bot.users)}** users in **{len(self.bot.guilds)}** servers.\n" \
            f"Official Support Server: {self.bot.config.support}"

        embed = discord.Embed(
            title=f"{self.bot.user.name} Statistics",
            description=desc,
            color=self.bot.color,
            timestamp=self.bot.timestamp
        )
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.set_footer(
            text=f"{self.bot.user.name} v{self.bot.version} - MIT licensed")
        embed.add_field(
            name="Bot Statistics",
            value=bot_stats
        ).add_field(
            name="Host Statistics",
            value=host_stats
        )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def status(self, ctx):
        """Returns Overwatch servers status."""
        async with ctx.typing():
            embed = discord.Embed(
                title="Overwatch servers status",
                color=self.bot.color,
                timestamp=self.bot.timestamp
            )
            embed.set_footer(text="Data taken from downdetector.com")
            try:
                embed.description = await self.bot.get_servers_status()
            except Exception:
                embed.description = "[Overwatch Servers Status](https://downdetector.com/status/overwatch/)"
            await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def news(self, ctx):
        """Returns the first 5 news about Overwatch."""
        async with ctx.typing():
            pages = []
            try:
                title, link, desc, img = await self.bot.get_news()
            except Exception:
                embed = discord.Embed(
                    title="Latest Overwatch News",
                    description=f"[Click here to check out all the new Overwatch news.]({self.bot.config.news})",
                    color=self.bot.color
                )
                embed.set_footer(text="Blizzard Entertainment")
                await ctx.send(embed=embed)
            else:
                for i in range(5):
                    embed = discord.Embed(
                        title=title[i],
                        url=link[i],
                        description=desc[i],
                        color=self.bot.color,
                        timestamp=self.bot.timestamp
                    )
                    embed.set_image(url=f"https:{img[i]}")
                    embed.set_footer(
                        text=f"Page {i+1}/5 - Blizzard Entertainment")
                    pages.append(embed)
                await self.bot.paginator.Paginator(extras=pages).paginate(ctx)

    @commands.command()
    @commands.guild_only()
    async def patch(self, ctx):
        """Returns most recent patch note about Overwatch."""
        async with ctx.typing():
            try:
                title = await self.bot.get_patch_notes()
            except Exception:
                title = "Latest Overwatch Patch Notes"
            embed = discord.Embed(
                title=title,
                color=self.bot.color
            )
            embed.add_field(
                name="Patch Notes",
                value="[Click here to view all the patch notes](https://playoverwatch.com/ko-kr/news/patch-notes/pc)"
            )
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Various(bot))
