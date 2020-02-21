import secrets
import yaml

import discord

from discord.ext import commands


with open("assets/heroes.yml") as fp:
    hero = yaml.safe_load(fp.read())

TANK_LOGO = hero["roles"]["icon"]["tank"]
SUPPORT_LOGO = hero["roles"]["icon"]["support"]
DAMAGE_LOGO = hero["roles"]["icon"]["damage"]
FLEX_LOGO = hero["roles"]["icon"]["flex"]
ALL_HEROES = hero["heroes"]["all"]
ALL_ROLES = hero["roles"]["name"]
TANK = hero["heroes"]["tank"]
SUPPORT = hero["heroes"]["support"]


class Randoms(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def hero_color(rand):
        if rand in TANK:
            return 0xFAA528
        elif rand in SUPPORT:
            return 0x13A549
        else:
            return 0xE61B23

    def random_hero(self):
        rand = secrets.choice(ALL_HEROES)
        hero_logo = f"https://d1u1mce87gyfbn.cloudfront.net/hero/{rand}/hero-select-portrait.png"
        hero_color = self.hero_color(rand)

        embed = discord.Embed(color=hero_color)
        embed.set_thumbnail(url=hero_logo)
        embed.add_field(
            name="**{hero}**".format(hero=rand.upper()),
            value="\u200b"
        )
        return embed

    @commands.guild_only()
    @commands.command()
    @commands.cooldown(5, 5, commands.BucketType.user)
    async def hero(self, ctx):
        """Returns a random hero to play with."""
        e = self.random_hero()
        await ctx.send(embed=e)

    @staticmethod
    def role_attr(rand):
        if rand == "tank":
            return (0xFAA528, TANK_LOGO)  # create a tuple to store these data
        elif rand == "support":
            return (0x13A549, SUPPORT_LOGO)
        elif rand == "damage":
            return (0xE61B23, DAMAGE_LOGO)
        else:
            return (0xfa9c1e, FLEX_LOGO)

    def random_role(self):
        rand = secrets.choice(ALL_ROLES)
        # getting data from the tuple (in order)
        role_color, role_logo = self.role_attr(rand)

        embed = discord.Embed(color=role_color)
        embed.set_thumbnail(url=role_logo)
        embed.add_field(
            name="**{role}**".format(role=rand.upper()),
            value="\u200b"
        )
        return embed

    @commands.guild_only()
    @commands.command()
    @commands.cooldown(5, 5, commands.BucketType.user)
    async def role(self, ctx):
        """Returns a random role to play."""
        try:
            e = self.random_role()
        except Exception as ex:
            await ctx.send(ex)
        else:
            await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(Randoms(bot))
