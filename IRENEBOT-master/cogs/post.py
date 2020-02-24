import aiohttp
import aiosqlite

import config

from discord.ext import commands


header = {"Authorization": config.dbl_token}


class DbPost(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def reset_prefix(self, guild):
        """Reset prefix once the bot left a guild."""
        if not guild:
            return
        async with aiosqlite.connect("main.sqlite") as conn:
            await conn.execute("DELETE FROM prefixes WHERE id=?", (guild.id,))
            await conn.commit()

    async def update(self):
        payload = {"server_count": len(self.bot.guilds),
                   "shard_count": self.bot.shard_count}
        async with aiohttp.ClientSession() as s:
            await s.post(self.bot.config.dbl_token, data=payload, headers=header)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Update server count once a guild joined."""
        await self.update()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        """Update server count once a guild left."""
        await self.reset_prefix(guild)
        await self.update()


def setup(bot):
    bot.add_cog(DbPost(bot))
