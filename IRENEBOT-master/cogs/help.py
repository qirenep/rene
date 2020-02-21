import discord

from discord.ext import commands


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i: i + n]


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def help_signature(self, command):
        parent = command.full_parent_name
        if len(command.aliases) > 0:
            fmt = f"[{command.name}|{'|'.join(command.aliases)}]"
            if parent:
                fmt = f"{parent} {fmt}"
        else:
            fmt = command.name if not parent else f"{parent} {command.name}"
        fmt = f"{fmt} {command.signature}"
        return fmt

    def make_pages(self):
        all_commands = {}
        for cog, instance in self.bot.cogs.items():
            # avoid showing commands for this cog/s
            if cog in ["Owner"]:
                continue
            commands = list(chunks(list(instance.get_commands()), 10))
            if len(commands) == 1:
                all_commands[cog] = commands[0]
            else:
                for i, j in enumerate(commands):
                    all_commands[f"{cog} ({i + 1}/{len(commands)})"] = j

        pages = []
        maxpages = len(all_commands)

        description = f"By scrolling the pages with the arrows you can check\n" \
            "all the available commands.\n" \
            f"Official Support Server: {self.bot.config.support}."

        embed = discord.Embed(
            title=f"{self.bot.user.name} Help",
            color=self.bot.color,
            description=description,
            timestamp=self.bot.timestamp
        ).set_thumbnail(
            url=self.bot.user.avatar_url
        )
        pages.append(embed)
        for i, (cog, commands) in enumerate(all_commands.items()):
            embed = discord.Embed(
                title=f"**{cog} Commands**",
                color=self.bot.color,
                timestamp=self.bot.timestamp
            )
            embed.set_footer(
                text=f"Page {i+1}/{maxpages}",
            )
            for command in commands:
                if command.callback.__doc__:
                    desc = command.callback.__doc__
                else:
                    desc = "No Description set"
                embed.add_field(
                    name=self.help_signature(command), value=desc, inline=False
                )
            pages.append(embed)
        return pages

    @commands.command()
    async def help(self, ctx, *, command: commands.clean_content(escape_markdown=True) = None):
        """Get usage information for commands."""
        if command:
            command = self.bot.get_command(command.lower())
            if not command:
                return await ctx.send("Sorry, typed command doesn't exist.")
            sig = self.help_signature(command)
            subcommands = getattr(command, "commands", None)
            form = discord.Embed(color=self.bot.color)
            if subcommands:
                clean_subcommands = "\n".join(
                    [
                        f"{c.name} - {getattr(c.callback, '__doc__')}"
                        for c in subcommands
                    ]
                )
                form.title = f"{ctx.prefix}{sig}"
                form.description = getattr(command.callback, '__doc__')
                form.add_field(
                    name="Commands",
                    value=clean_subcommands,
                    inline=False
                )
            else:
                form.title = f"{ctx.prefix}{sig}"
                form.description = getattr(command.callback, '__doc__')
            return await ctx.send(embed=form, delete_after=60)

        await self.bot.paginator.Paginator(extras=self.make_pages()).paginate(ctx)


def setup(bot):
    bot.add_cog(Help(bot))
