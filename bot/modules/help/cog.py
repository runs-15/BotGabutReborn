from inspect import formatargvalues
import discord, datetime
from discord import Embed
from discord.ext.commands import Cog, command
# from discord_components import Button, ButtonStyle, InteractionType
# import asyncio
from db import servers_con, version
from discord.utils import get

def syntax(command):
    cmd_and_aliases = "|".join([str(command), *command.aliases])
    params = []
    
    for key, value in command.params.items():
        if key not in ("self", "ctx"):
            params.append(f"[{key}]" if "=" in str(value) else f"<{key}>")
    params = " ".join(params)
    return f"```{cmd_and_aliases} {params}```"
    
class Help(Cog):
    """
    > Show this help message and controlling help for commands.
    """
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command("help")
                
    async def cmd_help(self, ctx, command):
        embed = Embed(title=f"Bantuan perintah `{command}`", description=syntax(command), colour=int(hex(int("2f3136", 16)), 0), timestamp=datetime.datetime.now())
        embed.add_field(name="Deskripsi perintah: ", value=command.help)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        await ctx.send(embed=embed)
        
    @command(name = "help")
    async def help(self, ctx, cmd=None):
        prefix = servers_con['servers']['server'].find({'server_id' : ctx.guild.id})[0]['prefix']
        emb = Embed(title='Modules and Command', color=int(hex(int("2f3136", 16)), 0),
                            description=f'Use `{prefix}help <command>` to gain more information about that command\n',
                            timestamp=datetime.datetime.now())
        emb.set_thumbnail(url=self.bot.user.avatar.url)
        emb.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar.url)
        if cmd is None:
            cogs_desc = ''
            for cog in sorted(self.bot.cogs):
                cmd_list = ''
                if len([c for c in self.bot.get_cog(cog).get_commands() if not c.hidden]) != 0:
                    for cmd in self.bot.get_cog(cog).get_commands():
                        if not cmd.hidden:
                            cmd_list += f'`{cmd.name}` '
                    desc = '{}> {}'.format(self.bot.cogs[cog].__doc__, cmd_list)
                    cmd_count = f'[{len([c for c in self.bot.get_cog(cog).get_commands() if not c.hidden])}]'
                    emb.add_field(name=f'**※{cog} Module {cmd_count}**', value=desc, inline=False)
                
            # integrating trough uncategorized commands
            commands_desc = ''
            for cmd in self.bot.walk_commands():
                # if cog not in a cog
                # listing command if cog name is None and command isn't hidden
                if not cmd.cog_name and not cmd.hidden:
                    commands_desc += f'`{cmd.name}`\n> {cmd.help}\n'
                
            # adding those commands to embed
            if commands_desc:
                emb.add_field(name='Not belonging to a module', value=commands_desc, inline=False)
                
            # setting information about author
            emb.add_field(name="About", value=f"Discord bot based on version `{discord.__version__}` of `pycord`")
            emb.set_footer(text=f"Bot is running on {version}")
                        
            await ctx.send(embed=emb)
        else:
            if (command := get(self.bot.commands, name=cmd)):
                await self.cmd_help(ctx, command)
            else:
                # for i in self.bot.commands:
                #     for j in i.aliases:
                #         if str(cmd) in str(i) or str(cmd) in str(j):
                #             try:
                #                 hlp = await ctx.send(f"Command not available, or maybe call `{prefix}help {i}` instead?", components=[[Button(style=ButtonStyle.green, label=f"help {i}")]])
                #                 res = await self.bot.wait_for("button_click", check=lambda i: i.author == ctx.author, timeout=10)
                #                 if res.component.label == f"help {i}":
                #                     await hlp.edit(components=[])
                #                     await res.respond(type=6)
                #                     await self.cmd_help(ctx, i)
                #                 break
                #             except:
                #                 await hlp.edit(components=[])
                #                 break
                pass
    
def setup(bot):
    bot.add_cog(Help(bot))