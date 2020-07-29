import json
import time
from socket import socket

from discord import Embed
from asyncio import sleep as delay

import discord
from locals import *
from mcrcon import MCRcon


class SpaceCraftManager(Command):
    name = ("<@!737413136583229519>", "<@&737413136583229519>", "<@737413136583229519>")

    MC_CHANNEL = 704025530244005964  # MAIN CHANNEL ID

    def __init__(self):
        self.players = []
        self.server_ready = False

    async def on_load(self, bot: Client):
        bot.loop.create_task(
            self.status_fetch_task(bot)
        )
        bot.loop.create_task(
            self.auto_shut_down(bot)
        )
        await bot.get_channel(self.MC_CHANNEL).send(
            embed=Embed(
                title="Initializing Server",
                description="You can download AMCL to connect to this server from\n__https://github.com/xvzihao/SpacecraftClient/releases/download/1.6/Setup-AMCL.exe__",
                colour=0x87dc49
            )
        )

    async def auto_shut_down(self, bot: Client):
        last_result = self.players
        while not bot.is_closed():
            await delay(2)
            if not self.players:  # self.player is empty
                empty_since = time.time()
                warned = False
                stopped = False
                while not bot.is_closed() and not self.players:
                    await delay(1)
                    if time.time() - empty_since > AUTO_STOP_TIME and not warned:
                        await bot.get_channel(self.MC_CHANNEL).send(":warning:** Server was idled for 10min. **")
                        await delay(1.2)
                        await bot.get_channel(self.MC_CHANNEL).send(
                            ":warning:** Server will shutdown automatically within 1 minute if nobody joins. **")
                        warned = True
                    if time.time() - empty_since > AUTO_STOP_TIME + 60 and not stopped:
                        await bot.get_channel(self.MC_CHANNEL).send("<@&737090936680742982> stop server")
                        stopped = True

    async def status_fetch_task(self, bot):
        while not bot.is_closed():
            try:
                result = eval(await fetch("http://localhost:2005/ready"))
                if result != self.server_ready:
                    self.server_ready = result
                    if result:
                        await bot.get_channel(self.MC_CHANNEL).send(
                            embed=Embed(
                                title=f"SpaceCraft is ready",
                                description="**Server address:** __mc.alex-xu.site__",
                                colour=0x79f50a
                            )
                        )
                    else:
                        self.players = []
                        await bot.get_channel(self.MC_CHANNEL).send(
                            embed=Embed(
                                title=f"SpaceCraft is closed",
                                colour=0xff0000
                            )
                        )

                result = eval(await fetch("http://localhost:2005/players"))
                if result != self.players:
                    left = set(self.players) ^ set(result)
                    for player in left:
                        if player not in self.players:
                            await bot.get_channel(self.MC_CHANNEL).send(
                                embed=Embed(
                                    title=f"**{player}** join the server",
                                    colour=0x90c561
                                )
                            )
                            try:
                                s = socket()
                                s.settimeout(1)
                                s.connect((ADDRESS, 25575))
                                s.close()
                                with MCRcon(ADDRESS, PASSWORD) as rcon:
                                    rcon.connect()
                                    await rcon_title(
                                        rcon,
                                        {"text": "Welcome to", "color": "gold"},
                                        {"text": "SpaceCraft Server", "color": "blue"},
                                        mention=player
                                    )
                            except Exception as e:
                                print(e)
                        else:
                            await bot.get_channel(self.MC_CHANNEL).send(
                                embed=Embed(
                                    title=f"**{player}** left the server",
                                    colour=0xf7630c
                                )
                            )
                    self.players = result

                await delay(2)
            except Exception as e:
                await delay(3)

    async def on_active(self, args: List[int], message: Message, bot: Client):
        if args in (
                ['mods'], ['mods', 'list'],
                ['plugins'], ['list', 'mods']
        ):
            with open('mods.json') as f:
                content = json.load(f)

            embed = Embed(
                title="Mods list",
                colour=0x0482ff
            )

            for name in content:
                embed.add_field(
                    name=name,
                    value=f"__{content[name]['link']}__",
                )

            await message.channel.send(embed=embed)

            return 0

        if args in (
                ['players'], ['list'], ['online', 'players'],
                ['players', 'online'], ['online']
        ):
            try:
                if not self.server_ready:
                    await message.channel.send(
                        embed=Embed(
                            title=":warning: Could not fetch player list.",
                            description="Server is closed or not ready.",
                            colour=0xfff300
                        )
                    )
                    return 0
                if self.players:
                    embed = Embed(
                        title=f"There are {len(self.players)} player{'s' if len(self.players) > 1 else ''} online: ",
                        description='**' + ", ".join(self.players) + '**',
                        colour=0x7196ff
                    )
                else:
                    embed = Embed(
                        title=f"No one is playing in this server",
                        colour=0x7196ff
                    )
                await message.channel.send(embed=embed)
            except Exception as e:
                await message.channel.send(embed=Embed(
                    title=":warning:Failed to get players online",
                    description=str(e),
                    colour=0xff0000
                ))
            return 0
        return 1


commands = [
    SpaceCraftManager,
]
