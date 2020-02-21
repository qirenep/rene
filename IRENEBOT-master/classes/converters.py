from discord.ext import commands


class InvalidPlatform(commands.BadArgument):
    pass


class Platform(commands.Converter):
    async def convert(self, ctx, arg):
        x = arg.lower()
        if x not in ["pc", "psn", "xbl"]:
            raise InvalidPlatform()
        return x


class Battletag(commands.Converter):
    async def convert(self, ctx, arg):
        return arg.replace('#', '-')
