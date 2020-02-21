import yaml

import discord

from discord.ext import commands


with open("assets/emotes.yml") as fp:
    emotes = yaml.safe_load(fp.read())

# AWARDS
AWARDS = emotes["awards"]

# RANK
ROLES_ICON = emotes["icons"]["roles"]
SR = emotes["icons"]["rank"]["sr"]
NES = emotes["icons"]["rank"]["nes"]

# COMP/QUICK
GAME = emotes["stats"]["game"]
ASSISTS = emotes["stats"]["assists"]
BEST = emotes["stats"]["best"]
COMBAT = emotes["stats"]["combat"]

with open("assets/heroes.yml") as fp:
    hero = yaml.safe_load(fp.read())

ALL_ROLES = hero["roles"]["name"]


class EmbedAwards:

    def __init__(self, bot):
        self.bot = bot

    async def embed_awards(self, data, platform, name):
        # Player info
        name = data["name"]
        icon = data["icon"]
        profile = await self.bot.get_ow_profile(platform, name)

        embed = discord.Embed(
            title="AWARDS",
            url=profile,
            color=self.bot.color
        )
        embed.set_author(
            name=name,
            icon_url=icon,
            url=profile
        )

        # *** competitive awards ***
        if data["competitiveStats"]["careerStats"] == {}:
            pass

        else:
            comp_awards = ""
            i = 0
            for key, value in data["competitiveStats"]["awards"].items():
                new_key = await self.bot.add_space(key)
                award_icon = AWARDS[i]
                i += 1
                comp_awards += f"{award_icon} {new_key}: **{value}**\n"
            embed.add_field(
                name="**COMPETITIVE**",
                value=comp_awards,
                inline=True
            )

        # *** quickplay awards ***
        quick_awards = ""
        i = 0
        for key, value in data["quickPlayStats"]["awards"].items():
            new_key = await self.bot.add_space(key)
            award_icon = AWARDS[i]
            i += 1
            quick_awards += f"{award_icon} {new_key}: **{value}**\n"
        embed.add_field(
            name="**QUICKPLAY**",
            value=quick_awards,
            inline=True
        )
        return embed


class EmbedRank:

    def __init__(self, bot):
        self.bot = bot

    async def embed_rank(self, data, platform, name):
        name = data["name"]
        icon = data["icon"]
        profile = await self.bot.get_ow_profile(platform, name)
        embed = discord.Embed(
            color=self.bot.color
        )
        embed.set_author(
            name=name,
            icon_url=icon,
            url=profile
        )

        if data["ratings"] is None:
            for i in range(3):
                role_name = ALL_ROLES[i]
                role_icon = ROLES_ICON[i]
                embed.add_field(
                    name=f"{role_icon} **{role_name.upper()}**",
                    value=f"{NES} **Unranked**"
                )
            return embed

        else:
            async def get_rating_icon(rating):
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

            i = 0
            for rate in data["ratings"]:
                rating_level = rate["level"]
                rating_icon = await get_rating_icon(rating_level)
                role_name = rate["role"]
                role_icon = ROLES_ICON[i]
                i += 1
                embed.add_field(
                    name=f"{role_icon} **{role_name.upper()}**",
                    value=f"{rating_icon} **{rating_level}**{SR}"
                )
            return embed


class EmbedQuickplay:

    def __init__(self, bot):
        self.bot = bot

    async def embed_quick_stats(self, ctx, data, platform, name):
        # *** player info ***
        name = data["name"]
        icon = data["icon"]
        level_icon = data["levelIcon"]
        profile = await self.bot.get_ow_profile(platform, name)

        # *** create the embed ***
        embed = discord.Embed(
            title="**QUICKPLAY STATS**",
            url=profile,
            color=self.bot.color,
            timestamp=self.bot.timestamp
        )
        embed.set_author(
            name=name,
            icon_url=icon,
            url=profile
        )
        embed.set_thumbnail(url=level_icon)
        embed.set_footer(text=f"Requested by {ctx.author.name}")

        # *** games ***
        game = ""
        for key, value in data["quickPlayStats"]["careerStats"]["allHeroes"]["game"].items():
            new_key = await self.bot.add_space(key)
            game += f"{new_key}: **{value}**\n"
        embed.add_field(
            name="{} **Games**".format(GAME),
            value=game,
            inline=True
        )

        # *** assists ***
        assists = ""
        for key, value in data["quickPlayStats"]["careerStats"]["allHeroes"]["assists"].items():
            new_key = await self.bot.add_space(key)
            assists += f"{new_key}: **{value}**\n"
        embed.add_field(
            name="{} **Assists**".format(ASSISTS),
            value=assists,
            inline=True
        ).add_field(
            name="\u200b",
            value="\u200b",
        )

        # *** best ***
        best = ""
        for key, value in data["quickPlayStats"]["careerStats"]["allHeroes"]["best"].items():
            new_key = await self.bot.add_space(key)
            new_key = new_key.replace(" Most In Game", "")
            best += f"{new_key}: **{value}**\n"
        embed.add_field(
            name="{} **Best** (*Most in game*)".format(BEST),
            value=best,
            inline=True
        )

        # *** combat ***
        combat = ""
        for key, value in data["quickPlayStats"]["careerStats"]["allHeroes"]["combat"].items():
            new_key = await self.bot.add_space(key)
            combat += f"{new_key}: **{value}**\n"
        embed.add_field(
            name="{} **Combat**".format(COMBAT),
            value=combat,
            inline=True
        ).add_field(
            name="\u200b",
            value="\u200b",
        )

        return embed


class EmbedCompetitive:

    def __init__(self, bot):
        self.bot = bot

    async def embed_comp_stats(self, ctx, data, platform, name):
        if data["competitiveStats"]["topHeroes"] == {} or data["competitiveStats"]["careerStats"] == {}:
            return await ctx.send("This profile has no competitive stats.")

        # *** player info ***
        name = data["name"]
        icon = data["icon"]
        level_icon = data["levelIcon"]
        profile = await self.bot.get_ow_profile(platform, name)

        # *** create the embed ***
        embed = discord.Embed(
            title="**COMPETITIVE STATS**",
            url=profile,
            color=self.bot.color,
            timestamp=self.bot.timestamp
        )
        embed.set_author(
            name=name,
            icon_url=icon,
            url=profile
        )
        embed.set_thumbnail(url=level_icon)
        embed.set_footer(text="Requested by {author}".format(
            author=ctx.author.name
        ))

        # *** games ***
        about = ""
        for key, value in data["competitiveStats"]["careerStats"]["allHeroes"]["game"].items():
            new_key = await self.bot.add_space(key)
            about += f"{new_key}: **{value}**\n"
        embed.add_field(
            name="{} **Games**".format(GAME),
            value=about,
            inline=True
        )

        # *** assists ***
        assists = ""
        for key, value in data["competitiveStats"]["careerStats"]["allHeroes"]["assists"].items():
            new_key = await self.bot.add_space(key)
            assists += f"{new_key}: **{value}**\n"
        embed.add_field(
            name="{} **Assists**".format(ASSISTS),
            value=assists,
            inline=True
        ).add_field(
            name="\u200b",
            value="\u200b",
        )

        # *** best ***
        best = ""
        for key, value in data["competitiveStats"]["careerStats"]["allHeroes"]["best"].items():
            new_key = await self.bot.add_space(key)
            new_key = new_key.replace(" Most In Game", "")
            best += f"{new_key}: **{value}**\n"
        embed.add_field(
            name="{} **Best** (*Most in game*)".format(BEST),
            value=best,
            inline=True
        )

        # *** combat ***
        combat = ""
        for key, value in data["competitiveStats"]["careerStats"]["allHeroes"]["combat"].items():
            new_key = await self.bot.add_space(key)
            combat += f"{new_key}: **{value}**\n"
        embed.add_field(
            name="{} **Combat**".format(COMBAT),
            value=combat,
            inline=True
        ).add_field(
            name="\u200b",
            value="\u200b",
        )

        return embed


class EmbedException:

    def __init__(self, bot):
        self.bot = bot

    async def embed_exception(self, ex):
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
