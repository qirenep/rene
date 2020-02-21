import aiohttp

import discord

from discord.ext import commands


class Fetch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def fetch(self, ctx, platform, name):
        """Fetch player stats from the API."""
        address = f"https://ow-api.com/v2/stats/{self.platform}/{self.name}/complete"

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            async with session.get(address) as r:
                if r.status == 200:
                    data = await r.json()
                    if data["private"] is True:
                        profile = await self.bot.get_ow_profile(platform, name)
                        embed = discord.Embed(
                            color=0xff1919,
                            title="Profile",
                            url=profile,
                            timestamp=self.bot.timestamp
                        )
                        embed.set_author(
                            name=data["name"],
                            icon_url=data["icon"],
                            url=profile
                        )
                        embed.set_footer(
                            text=f"Requested by {ctx.author.name}")
                        embed.add_field(
                            name="**THIS PROFILE IS PRIVATE**",
                            value="Profiles are set to private by default.\nYou can modify this setting in Overwatch under `Options - Social`.\nPlease note that **Overwatch** usually update profile visibility after 4/5 minutes."
                        )
                        await ctx.send(embed=embed)
                    else:
                        return data
                elif r.status in [404, 400]:
                    await ctx.send("Account not found, please try again.")
                else:
                    await ctx.send(f"Error `{r.status}` occured, sorry for the inconvenience.")


def setup(bot):
    bot.add_cog(Fetch(bot))
