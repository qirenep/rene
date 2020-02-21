import aiosqlite
import asyncio

import discord

from discord.ext import commands

from utilsmy.embed import group_embed


class Server(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def settings(self, ctx, command: str = None):
        """Change the settings for your Discord server."""
        embed = group_embed(ctx, self.bot.get_command(ctx.command.name))
        await ctx.send(embed=embed)

    @settings.command(name="prefix")
    @commands.has_permissions(manage_guild=True)
    async def _prefix(self, ctx, *, prefix: str):
        """Change the prefix for this server."""
        if len(prefix) > 10:
            return await ctx.send("Prefixes may not be longer than 10 characters.")

        async with aiosqlite.connect("main.sqlite") as conn:
            async with conn.execute("SELECT prefix FROM prefixes WHERE id=?;", (ctx.guild.id,)) as pool:
                rows = await pool.fetchall()
                if rows:
                    await pool.execute("UPDATE prefixes SET prefix=? WHERE id=?;",
                                       (prefix, ctx.guild.id))
                    await conn.commit()
                else:
                    await pool.execute("INSERT INTO prefixes VALUES(?,?);",
                                       (ctx.guild.id, prefix))
                    await conn.commit()

                await ctx.send(f"""```ini
Prefix has been successfully changed to: [ {prefix} ]
```""")

    @settings.command()
    async def reset(self, ctx):
        """Reset the server settings."""
        embed = discord.Embed(
            color=self.bot.color
        ).add_field(
            name="Are you sure?",
            value="This will reset your prefix"
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
            async with aiosqlite.connect("main.sqlite") as conn:
                await conn.execute("DELETE FROM prefixes WHERE id=?;", (ctx.guild.id,))
                await conn.commit()
            return await ctx.send("Settings has been successfully reset.")
        await ctx.send("Settings have **not** been reset.")

    async def get_guild_prefix(self, guild):
        """Get the prefix for a guild."""
        async with aiosqlite.connect("main.sqlite") as conn:
            async with conn.execute("SELECT prefix FROM prefixes WHERE id=?;", (guild,)) as pool:
                x = await pool.fetchall()
                if x:
                    return x[0][0]
                return self.bot.config.default_prefix

    @commands.command()
    @commands.guild_only()
    async def prefix(self, ctx):
        """Displays information about the prefix."""
        _prefix = await self.get_guild_prefix(ctx.guild.id)
        embed = discord.Embed(
            title="Prefix Information",
            color=self.bot.color
        )
        embed.add_field(
            name="Current prefix",
            value=f"`{_prefix}`",
        ).add_field(
            name="Want to change it?",
            value=f"`{_prefix}settings prefix <new_prefix>`",
        ).add_field(
            name="Note",
            value="`Manage Server` permission is required to change the prefix.",
            inline=False
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Server(bot))
