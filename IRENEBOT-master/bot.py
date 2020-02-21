"""
MIT License

Copyright (c) 2019-2020 Davide Tacchini

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import aiosqlite
import textwrap
import datetime
import aiohttp
# import asyncio
import time
import os

import config
from utilsmy import paginator
from discord.ext import commands

from termcolor import colored
from bs4 import BeautifulSoup




class Bot(commands.AutoShardedBot):
    """Custom bot class for OverBot."""

    def __init__(self):
        super().__init__(
            command_prefix=self.get_pre,
            case_insensitive=True
        )
        self.remove_command("help")
        self.config = config
        self.version = config.version
        self.color = config.main_color
        self.linecount = 0
        self.commands_used = 0
        self.get_linecount()
        self.start_time = time.time()

        self.paginator = paginator

        for extension in os.listdir("cogs"):
            if extension.endswith(".py"):
                try:
                    self.load_extension(f"cogs.{extension[:-3]}")
                except Exception as error:
                    print("[" + colored("ERROR", "red") + "]" +
                          " {:20}\tfailed its loading! [{}]".format(extension, error))
                else:
                    print("[" + colored("OK", "green") + "]" +
                          " {:20}\tsuccessfully loaded!".format(extension))

    def get_linecount(self):
        for root, dirs, files in os.walk(os.getcwd()):
            for file_ in files:
                if file_.endswith(".py"):
                    with open(f"{root}/{file_}", 'rt', encoding='UTF8') as f:
                        self.linecount += len(f.readlines())

    async def on_resumed(self):
        """On client resumed."""
        print(textwrap.dedent(
            """
            ------------------
            Connection resumed.
            ------------------
            """
        ))

    async def on_command(self, ctx):
        """Count commands used."""
        self.commands_used += 1

    async def on_message(self, message):
        await self.process_commands(message)

    @staticmethod
    async def get_pre(bot, message):
        """Returns the prefix."""
        if not message.guild:
            return
        async with aiosqlite.connect("main.sqlite") as conn:
            async with conn.execute("SELECT prefix FROM prefixes WHERE id=?", (message.guild.id,)) as pool:
                x = await pool.fetchall()
                if x:
                    return commands.when_mentioned_or(x[0][0])(bot, message)
                return commands.when_mentioned_or(config.default_prefix)(bot, message)

    async def get_servers_status(self):
        """Returns Overwatch servers status."""
        async with aiohttp.ClientSession() as session:
            async with session.get(self.config.servers) as r:
                content = await r.read()
                page = BeautifulSoup(content, features="html.parser")
                status = page.find(class_="entry-title")
                return status.get_text()

    async def get_news(self):
        """Returns Overwatch news."""
        async with aiohttp.ClientSession() as session:
            async with session.get(self.config.news) as r:
                content = await r.read()
                page = BeautifulSoup(content, features="html.parser")
                titles, links, descs, imgs = [], [], [], []
                for x in page.find_all('a', {"class": "link-title"}, href=True):
                    titles.append(x.get_text())
                    links.append("https://playoverwatch.com" + x['href'])
                for desc in page.find_all(class_="summary"):
                    descs.append(desc.get_text())
                for img in page.find_all('img', {"class", "media-card-fill"}):
                    imgs.append(img['src'])
                return [titles, links, descs, imgs]

    async def get_patch_notes(self):
        """Returns Overwatch latest patch notes."""
        async with aiohttp.ClientSession() as session:
            async with session.get(self.config.patch) as r:
                content = await r.read()
                page = BeautifulSoup(content, features="html.parser")
                for patch in page.find(class_="patch-notes-patch"):
                    title = next(patch.children, None)
                    if title is not None:
                        return str(title).strip()

    @property
    def uptime(self):
        current_time = time.time()
        difference = int(round(current_time - self.start_time))
        return str(datetime.timedelta(seconds=difference))

    @property
    def timestamp(self):
        return datetime.datetime.utcnow()

    @property
    def ping(self):
        return f"{round(self.latency * 1000)}ms"

    async def close(self):
        await super().close()

    def run(self):
        super().run(config.token, reconnect=True)

    # def run(self, *args, **kwargs):
    #     try:
    #         self.loop.run_until_complete(self.start(config.token))
    #     except KeyboardInterrupt:
    #         self.loop.run_until_complete(self.logout())
    #         for task in asyncio.all_tasks(self.loop):
    #             task.cancel()
    #         try:
    #             self.loop.run_until_complete(
    #                 asyncio.gather(*asyncio.all_tasks(self.loop))
    #             )
    #         except asyncio.CancelledError:
    #             print("Tasks have been cancelled.")
    #         finally:
    #             print("Shutting down")
