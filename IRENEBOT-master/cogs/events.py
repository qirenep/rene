import textwrap

import discord

from discord.ext import commands


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """Print info in the terminal."""
        print(textwrap.dedent(
            f"""
            -----------------
            Connection established.
            Logged in as {self.bot.user.display_name} - {self.bot.user.id}
            Using discord.py {discord.__version__}
            Running {self.bot.user.display_name} {self.bot.version} in {len(self.bot.guilds)} guilds
            -----------------
            """
        ))
        await self.change_presence()

    async def change_presence(self):
        await self.bot.wait_until_ready()
        await self.bot.change_presence(
            activity=discord.Activity(
                name="for -help",
                type=discord.ActivityType.watching
            ),
            status=discord.Status.idle
        )

    async def send_join_message(self, guild):
        """Sends a welcome message once a guild join."""
        embed = discord.Embed(
            color=self.bot.color,
            timestamp=self.bot.timestamp
        )
        embed.set_author(
            name=self.bot.user.name,
            icon_url=self.bot.user.avatar_url
        )
        embed.set_image(url=self.bot.config.thumbnail)
        embed.set_footer(text=f"Joined {guild.name}")

        embed.add_field(
            name="Thank you for invite OverBot to your discord server!",
            value="The purpose of OverBot is to allow players to check their Overwatch statistics.",
            inline=False
        ).add_field(
            name="Get started",
            value="""
            To get started type `-help` or `@OverBot help`.
            Default prefix is `-` or you can mention the bot.
            You can change it by using `-settings` command and following the instructions.
            """,
            inline=False
        ).add_field(
            name="Important links",
            value=f"""
            [Support Server]({self.bot.config.support})
            [Vote]({self.bot.config.vote})
            [Invite]({self.bot.config.invite})
            [GitHub]({self.bot.config.github})
            """
        )
        channels = list(
            filter(
                lambda c: c.permissions_for(
                    guild.me).send_messages, guild.text_channels
            )
        )
        if channels:
            await channels[0].send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.send_join_message(guild)


def setup(bot):
    bot.add_cog(Events(bot))
