import inspect
from os import listdir
from time import time
from typing import Dict, Tuple, NoReturn, List

import psutil
from nextcord.ext import commands

from ..bot import Bot
from ..utils.embed import Embed


class Info(commands.Cog):
    """A simple commands cog template."""

    def __init__(self, client: Bot):
        """Link to bot instance."""
        self.client: Bot = client
        Embed.load(self.client)

        # Preloading file content
        self.files_info: Dict[str, str] = {}

        folders: Tuple[str, ...] = (".", "botoven", "botoven/cogs", "botoven/utils", "botoven/core", "botoven/music_apis")

        for file, path in {
            _f: path for path in folders
            for _f in listdir(path) if _f.endswith(".py")
        }.items():
            with open(f"{path}/{file}", encoding="utf-8") as f:
                self.files_info[file] = f.read()

        self.files_info['Total'] = "\n".join(self.files_info.values())

    @staticmethod
    async def is_visible(ctx, command: commands.Command) -> bool:
        """Check whether a command is visible for an user"""
        if not len(command.checks):
            return True

        for check in command.checks:
            try:
                if inspect.iscoroutinefunction(check):
                    await check(ctx)
                else:
                    check(ctx)

            except commands.errors.CheckFailure:
                return False

        return True

    @commands.command(
        name="ping",
        description="Return Bot Latency",
        brief="Ping command"
    )
    async def ping_command(self, ctx) -> None:
        """Return Bot Latency."""
        t: str = time()

        ping_embed = Embed(ctx)(title="Pong !").add_field(
            name="Api latency",
            value=f"> `{self.client.latency * 1000:.3f}` ms"
        )

        message = await ctx.send(embed=ping_embed)

        await message.edit(
            embed=ping_embed.add_field(
                name="Client latency",
                value=f"> `{time(t) * 1000:,.3f}` ms"
            )
        )

    @commands.command(name="code")
    async def code_command(self, ctx) -> None:
        await ctx.send(
            embed=Embed(ctx)(
                title="Code Structure",
                description=(
                    "> This is the whole code structure of "
                    f"{self.client.user.name}!"
                )
            ).add_fields(
                self.files_info,
                map_title=lambda name: (
                    f"📝 {name}" if name != "Total" else "📊 Total"
                ),
                map_values=lambda file: (
                    f"`{len(file)}` characters"
                    f"\n `{len(file.splitlines())}` lines"
                ),
            )
        )

    @commands.command(
        name="help",
        description="A command to find ever information about an other command",
        brief="The global help command"
    )
    async def help_command_default(self, ctx) -> None:
        all_commands: Dict[str: List[commands.Command]] = {}
        total: int = 0

        for cog_name, cog in self.client.cogs.items():
            available_commands: List[commands.Command] = [
                command
                for command in cog.get_commands()
                if await self.is_visible(ctx, command)
            ]

            if len(available_commands):
                all_commands[cog_name] = available_commands.copy()
                total += len(available_commands)

        aliases: int = len(self.client.all_commands) - len(self.client.commands)

        await ctx.send(
            embed=Embed(ctx)(
                title=f"General Help {self.client.user.name}",
                description=(
                    f"- `{total}`/`{len(self.client.commands)}` "
                    f"available commands\n`{aliases}` aliases"
                )
            ).add_fields(
                all_commands,
                map_values=lambda cog_commands: ', '.join(
                    f"`{command.name}`" for command in cog_commands
                ),
                inline=False
            )
        )

    @commands.command(
        name='cmds',
        aliases=('all', 'all_cmds'),
        brief="List every command osf the bot"
    )
    async def all_commands(self, ctx) -> None:
        """
        Provide a list of every command available command for the user,
        split by extensions and organized in alphabetical order.
        Will not show the event-only extension
        """
        print(
            Embed(ctx)(
                title='All commands',
                description=(
                    f"> `{len(self.client.commands)}` "
                    "commands available"
                )
            ).add_fields(
                self.client.cogs.items(), checks=len,
                map_title=lambda cog_name: cog_name.capitalize()[:-3] or 'Missing',
                map_values=lambda cog: '  •  '.join(
                    sorted(f'`{c.name}`' for c in cog.get_commands())
                ),
                inline=False
            ).fields
        )
        await ctx.send(
            embed=Embed(ctx)(
                title='All commands',
                description=(
                    f"> `{len(self.client.commands)}` "
                    "commands available"
                )
            ).add_fields(
                self.client.cogs.items(), checks=len,
                map_title=lambda cog_name: cog_name.capitalize()[:-3] or 'A',
                map_values=lambda cog: '  •  '.join(
                    sorted(f'`{c.name}`' for c in cog.get_commands())
                ),
                inline=False
            )
        )

    @commands.command(
        name="panel",
        aliases=('pan',),
        brief="Some data about the panel"
    )
    @commands.is_owner()
    async def panel_stats(self, ctx) -> None:
        mb: int = 1024 ** 2

        vm = psutil.virtual_memory()
        cpu_freq = psutil.cpu_freq()
        cpu_percent = psutil.cpu_percent()
        disk = psutil.disk_usage('.')

        stats = {
            'ram': (
                100 * (vm.used / vm.total),
                f'{(vm.total / mb) / 1000:,.3f}',
                'Gb'
            ),
            'cpu': (
                cpu_percent,
                f"{cpu_freq.current / 1000:.1f}`/`{cpu_freq.max / 1000:.1f}",
                'Ghz'
            ),
            'disk': (
                100 * (disk.used / disk.total),
                f'{disk.total / mb:,.0f}', 'Mb'
            )
        }

        await ctx.send(
            embed=Embed(ctx)(
                title="Server Report",
                description="The bot is hosted on a private vps."
            ).add_fields(
                stats.items(),
                map_title=lambda name: name.upper(),
                map_values=lambda percent, info, unit: (
                    f"> `{percent:.3f}` **%**\n- `{info}` **{unit}**"
                )
            )
        )

    @commands.command(
        name="invite",
        aliases=("inv", "i"),
        brief="A link to invite the bot"
    )
    async def invite(self, ctx) -> None:
        """Command to get bot invitation link."""
        await ctx.send(
            embed=Embed(ctx)(
                title="Invite the Bot !",
                description=(
                    "> Click this link to invite this bot on your servers !\n"
                    "You need to have the required permissions on the server.\n"
                    "[invite me now](https://discord.com/api/oauth2/authorize\n"
                    f"?client_id={self.client.user.id}&permissions=8&scope=bot)"
                )
            )
        )
