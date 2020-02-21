import discord
from discord.ext import commands

from json import JSONDecodeError


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error, bypass=False):

        if (
            hasattr(ctx.command, "on_error")
            or (ctx.command and hasattr(ctx.cog, f"_{ctx.command.cog_name}__error"))
            and not bypass
        ):
            # do nothing if a command has its own error handler
            return

        if isinstance(error, commands.CommandNotFound):
            return

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You are missing a required argument: `{arg}`".format(
                arg=error.param.name))

        elif isinstance(error, commands.BadArgument):
            await ctx.send("You are using a bad argument.")

        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have enough permissions.")

        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send("You can't use `{command}` command for `{seconds}` seconds.".format(
                command=ctx.command.name, seconds=round(error.retry_after, 2)
            ))

        elif isinstance(error, commands.NotOwner):
            await ctx.send("It seems you do not own this bot.")

        elif hasattr(error, "original") and isinstance(
                error.original, discord.HTTPException):
            return

        elif isinstance(error, JSONDecodeError):
            await ctx.send("An API error occured. Please be patient and try again.")


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
