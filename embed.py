import datetime
import yaml
import re

import discord

from config import main_color


with open("assets/emotes.yml") as e, open("assets/heroes.yml") as h:
    emotes = yaml.safe_load(e.read())
    hero = yaml.safe_load(h.read())

# Awards
AWARDS = emotes["awards"]

# Rank
ROLES_ICON = emotes["icons"]["roles"]
SR = emotes["icons"]["rank"]["sr"]
NES = emotes["icons"]["rank"]["nes"]

# Competitive / Quickplay
emotes_list = [
    emotes["stats"]["game"],
    emotes["stats"]["assists"],
    emotes["stats"]["best"],
    emotes["stats"]["combat"]
]

ALL_ROLES = hero["roles"]["name"]


class NoCompetitiveStats(Exception):
    """Exception raised when a player has no competitive stats."""

    pass


class Embeds:

    def __init__(self, data, platform, name):
        self.data = data
        self.platform = platform
        self.name = name
        self.api_name = data["name"]
        self.api_icon = data["icon"]
        self.api_level_icon = data["levelIcon"]
        self.color = main_color
        self.profile = self.get_ow_profile(self.platform, self.name)
        self.stats = ["game", "assists", "best", "combat"]
        self.mods = ["quickPlayStats"]

    @property
    def timestamp(self):
        return datetime.datetime.utcnow()

    @staticmethod
    def get_ow_profile(platform, name):
        """Returns official Overwatch website player profile link."""
        name = name.replace('#', '-').replace(' ', '%20')
        return f"https://playoverwatch.com/ko-kr/career/{platform}/{name}"

    @staticmethod
    def add_space(key):
        """From camel case to title (testTest -> Test Test)."""
        return re.sub("([a-z])([A-Z])", "\g<1> \g<2>", key).title()

    @staticmethod
    def get_rating_icon(rating):
        if rating <= 1499:
            return "<:bronze:632281015863214096>"
        elif rating > 1499 and rating <= 1999:
            return "<:silver:632281054211997718>"
        elif rating > 1999 and rating <= 2499:
            return "<:gold:632281064596832278>"
        elif rating > 2499 and rating <= 2999:
            return "<:platinum:632281092875091998>"
        elif rating > 2999 and rating <= 3499:
            return "<:diamond:632281105571119105>"
        elif rating > 3500 and rating <= 3999:
            return "<:master:632281117394993163>"
        elif rating > 3999:
            return "<:grandmaster:632281128966946826>"

    def rank(self):
        """Returns players rank."""
        embed = discord.Embed(color=self.color)
        embed.set_author(
            name=self.api_name,
            icon_url=self.api_icon,
            url=self.profile
        )

        if not self.data["ratings"]:
            for i in range(3):
                role_name = ALL_ROLES[i]
                role_icon = ROLES_ICON[i]
                embed.add_field(
                    name=f"{role_icon} **{role_name.upper()}**",
                    value=f"{NES} **Unranked**"
                )
            return embed

        i = 0
        for rate in self.data["ratings"]:
            rating_level = rate["level"]
            rating_icon = self.get_rating_icon(rating_level)
            role_name = rate["role"]
            role_icon = ROLES_ICON[i]
            i += 1
            embed.add_field(
                name=f"{role_icon} **{role_name.upper()}**",
                value=f"{rating_icon} **{rating_level}**{SR}"
            )
        return embed

    def awards(self):
        """Returns players awards."""
        embed = discord.Embed(color=self.color)
        embed.set_author(
            name=self.api_name,
            icon_url=self.api_icon,
            url=self.profile
        )

        if not self.data["competitiveStats"]["careerStats"]:
            pass

        else:
            self.mods.append("competitiveStats")

        for mod in self.mods:
            i = 0
            tmp = ""
            for key, value in self.data[mod]["awards"].items():
                new_key = self.add_space(key)
                award_icon = AWARDS[i]
                i += 1
                tmp += f"{award_icon} {new_key}: **{value}**\n"
            embed.add_field(
                name="**{}**".format(mod.replace('Stats', '').capitalize()),
                value=tmp,
                inline=True
            )
        return embed

    def _stats(self, ctx):
        """Returns competitive or quickplay players stats."""
        if ctx.command.name == "competitive":
            if not self.data["competitiveStats"]["topHeroes"] or not self.data["competitiveStats"]["careerStats"]:
                raise NoCompetitiveStats()
            else:
                mod = "competitiveStats"
        else:
            mod = "quickPlayStats"

        embed = discord.Embed(
            title=f"**See full competitive stats for {self.api_name}**",
            url=self.profile,
            color=self.color,
            timestamp=self.timestamp
        )
        embed.set_author(
            name=self.api_name,
            icon_url=self.api_icon,
            url=self.profile
        )
        embed.set_thumbnail(url=self.api_level_icon)
        embed.set_footer(text=f"Requested by {ctx.author}")

        i = 0
        for stat in self.stats:
            tmp = ""
            for key, value in self.data[mod]["careerStats"]["allHeroes"][stat].items():
                new_key = self.add_space(key)
                new_key = new_key.replace(" Most In Game", "")
                tmp += f"{new_key}: **{value}**\n"
            embed.add_field(
                name="{} **{}**".format(
                    emotes_list[i],
                    stat.capitalize() if stat != "best" else stat.capitalize() + " (*Most in game*)"),
                value=tmp,
                inline=True
            )
            i += 1
            if stat in ["assists", "combat"]:
                embed.add_field(
                    name="\u200b",
                    value="\u200b"
                )
        return embed

    def is_private(self, ctx):
        """Returns an embed with private profile information."""
        embed = discord.Embed(color=0xff3232, timestamp=self.timestamp)
        embed.set_author(
            name=self.api_name,
            icon_url=self.api_icon,
            url=self.profile
        )
        embed.set_footer(
            text=f"Requested by {ctx.author.name}")
        embed.add_field(
            name="**THIS PROFILE IS PRIVATE**",
            value="Profiles are set to private by default.\nYou can modify this setting in Overwatch under `Options - Social`.\nPlease note that these changes will take effect after about 5 minutes."
        )
        return embed

    @staticmethod
    def exception(ex):
        """Returns a custom embed for exceptions."""
        embed = discord.Embed(color=0xff3232)
        embed.add_field(
            name=":x: An error occured.",
            value="Please report the following error to the developer by clicking [here](https://discord.gg/eZU69EV).",
            inline=False
        ).add_field(
            name="Error",
            value=f"{ex}",
            inline=False
        )
        return embed
