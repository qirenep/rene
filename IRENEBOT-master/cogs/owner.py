import textwrap
import traceback
import copy
import io

import discord

from contextlib import redirect_stdout
from discord.ext import commands

from utilsmy.database import select_all, remove_duplicates
from utilsmy.embed import exception


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i: i + n]


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

    @commands.command(aliases=["ld"], hidden=True)
    @commands.is_owner()
    async def load(self, ctx, *, cog: str):
        """
        [Owner Only] Loads a module.
        Use cogs.cog_name as cog parameter.
        """
        try:
            self.bot.load_extension(cog)
        except Exception as ex:
            await ctx.send(f"""
```diff
- [ERROR] Cannot load the module.
> [{type(ex).__name__}] {ex}
```""")
        else:
            await ctx.send("""
```diff
+ Module successfully loaded.
```""")

    @commands.command(aliases=["uld"], hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, *, cog: str):
        """[Owner Only] Unloads a module."""
        try:
            self.bot.unload_extension(cog)
        except Exception as ex:
            await ctx.send(f"""
```diff
- [ERROR] Cannot unload the module.
> [{type(ex).__name__}] {ex}
```""")
        else:
            await ctx.send("""
```diff
+ Module successfully unloaded.
```""")

    @commands.command(name="reload", aliases=["rld"], hidden=True)
    @commands.is_owner()
    async def _reload(self, ctx, *, cog: str):
        """[Owner Only] Reloads a module. Use cogs.cog_name as cog parameter."""
        try:
            self.bot.reload_extension(cog)
        except Exception as ex:
            await ctx.send(f"""
```diff
- [ERROR] Cannot reload the module.
> [{type(ex).__name__}] {ex}
```""")
        else:
            await ctx.send("""
```diff
+ Module successfully reloaded.
```""")

    @commands.command(aliases=['kys', 'die'], hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
        """[Owner Only] Kills the bot session."""
        await ctx.send(f"""
```asciidoc
Successfully gone offline
-------------------------
Uptime :: {self.bot.uptime}
Commands used :: {self.bot.commands_used}
```""")
        await self.bot.close()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def runas(self, ctx, member: discord.Member, *, command: str):
        """[Owner Only] Run a command as if you were the user."""
        msg = copy.copy(ctx.message)
        msg._update(
            dict(channel=ctx.channel, content=ctx.prefix + command))
        msg.author = member
        new_ctx = await ctx.bot.get_context(msg)
        try:
            await ctx.bot.invoke(new_ctx)
        except Exception as ex:
            await ctx.send(f"""
```diff
- [ERROR] Something went wrong.
> [{type(ex).__name__}] {ex}
```""")

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        if content.startswith("```") and content.endswith("```"):
            return "\n".join(content.split("\n")[1:-1])
        return content.strip("` \n")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def ex(self, ctx, *, body: str):
        """[Owner Only] Evaluates a code."""
        try:
            env = {
                "bot": self.bot,
                "ctx": ctx,
                "channel": ctx.channel,
                "author": ctx.author,
                "guild": ctx.guild,
                "message": ctx.message,
                "__last__": self._last_result,
            }

            env.update(globals())

            body = self.cleanup_code(body)
            stdout = io.StringIO()

            to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

            try:
                exec(to_compile, env)
            except Exception as e:
                return await ctx.send(f"```py\n{e.__class__.__name__}: {e}\n```")

            func = env["func"]
            try:
                with redirect_stdout(stdout):
                    ret = await func()
            except Exception:
                value = stdout.getvalue()
                await ctx.send(f"```py\n{value}{traceback.format_exc()}\n```")
            else:
                value = stdout.getvalue()
                try:
                    await ctx.message.add_reaction("✅")
                except discord.Forbidden:
                    pass

                if ret is None:
                    if value:
                        await ctx.send(f"```py\n{value}\n```")
                else:
                    self._last_result = ret
                    await ctx.send(f"```py\n{value}{ret}\n```")
        except Exception as ex:
            await ctx.send(ex)

    @commands.command()
    @commands.is_owner()
    async def prefixes(self, ctx):
        async with ctx.typing():
            pages = []
            rows = await select_all("prefixes")
            x = list(chunks(rows, 12))
            for i, k in enumerate(x):
                embed = discord.Embed(
                    title=f"Prefixes ({i+1}/{len(x)})",
                    description="All the OverBot prefixes stored in the database.",
                    color=self.bot.color
                )
                embed.set_footer(text=f"{len(rows)} prefixes")
                for row in k:
                    server_id, prefix = row
                    embed.add_field(name=server_id, value=prefix)
                pages.append(embed)
            await self.bot.paginator.Paginator(extras=pages).paginate(ctx)

    @commands.command()
    @commands.is_owner()
    async def profiles(self, ctx):
        async with ctx.typing():
            pages = []
            rows = await select_all("profiles")
            x = list(chunks(rows, 10))
            for i, k in enumerate(x):
                embed = discord.Embed(
                    title=f"Profiles ({i+1}/{len(x)})",
                    description="All the OverBot profiles stored in the database.",
                    color=self.bot.color
                )
                embed.set_footer(text=f"{len(rows)} profiles")
                for row in k:
                    user_id, platform, name = row
                    embed.add_field(name="User ID", value=user_id)
                    embed.add_field(name="Platform", value=platform)
                    embed.add_field(name="Name", value=name)
                    if len(k) < 10:
                        return await ctx.send(embed=embed)
                pages.append(embed)
            await self.bot.paginator.Paginator(extras=pages).paginate(ctx)

    @commands.command()
    @commands.is_owner()
    async def duplicates(self, ctx):
        try:
            await remove_duplicates()
            await ctx.send("""
```diff
+ Duplicates have been successfully removed.
```""")
        except Exception as ex:
            embed = exception(ex)
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Owner(bot))
