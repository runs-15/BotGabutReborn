from inspect import formatargvalues
import discord, datetime, db, time
import pandas as pd
from discord import Embed
from discord.ext.commands import Cog, command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
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
                if len(self.bot.get_cog(cog).get_commands()) != 0:
                    for cmd in self.bot.get_cog(cog).get_commands():
                        cmd_list += f'`{cmd.name}` '
                    desc = '{}> {}'.format(self.bot.cogs[cog].__doc__, cmd_list)
                    cmd_count = f'[{len(self.bot.get_cog(cog).get_commands())}]'
                    emb.add_field(name=f'**※{cog} Module {cmd_count}**', value=desc, inline=False)
                
            # integrating trough uncategorized commands
            commands_desc = ''
            for cmd in self.bot.walk_commands():
                # if cog not in a cog
                # listing command if cog name is None and command isn't hidden
                if not cmd.cog_name:
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
            
    def syntax(self, command):
        cmd_and_aliases = "|".join([str(command), *command.aliases])
        params = []
        
        for key, value in command.params.items():
            if key not in ("self", "ctx"):
                params.append(f"[{key}]" if "=" in str(value) else f"<{key}>")
        params = " ".join(params)
        return f"```{cmd_and_aliases} {params}```"
            
    async def cmd_help(self, ctx, command):
        embed = Embed(title=f"Bantuan perintah `{command}`", description=self.syntax(command), colour=int(hex(int("2f3136", 16)), 0), timestamp=datetime.datetime.now())
        embed.add_field(name="Deskripsi perintah: ", value=command.help)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        await ctx.send(embed=embed)
    
    @Cog.listener()        
    async def on_command_error(self, ctx, exc):
        if isinstance(exc, discord.ext.commands.CommandNotFound):
            cmd_lst = ''
            for i in self.bot.commands:
                if ctx.message.content.split()[0].lstrip(db.servers_con['servers']['server'].find({'server_id' : ctx.guild.id})[0]['prefix']) in i.name or ctx.message.content.split()[0].lstrip(db.servers_con['servers']['server'].find({'server_id' : ctx.guild.id})[0]['prefix']) in ' '.join(i.aliases):
                    cmd_lst += f'`{i or " ".join(i.aliases)}` '
                    continue
            if cmd_lst != '':
                hlp = await ctx.reply(f"Command not available, or maybe call {cmd_lst}instead?")
            else:
                hlp = await ctx.reply("Command not available")
        else:
            print(exc)
                        
            if (command := get(self.bot.commands, name=ctx.message.content.split()[0].lstrip(db.servers_con['servers']['server'].find({'server_id' : ctx.guild.id})[0]['prefix']))):
                await ctx.reply(f"```{str(exc)}```", embed=await self.cmd_help(ctx, command))

            
    async def backup(self):
        s = time.strftime("%x-%X-%Y")
        dtime = f'[{s}]_backup_'
        
        data_serversother = pd.DataFrame(db.servers_con['servers']['others'].find())
        data_serversother.to_csv(f'{dtime}data_servers_other.csv')
        
        data_servers = pd.DataFrame(db.servers_con['servers']['server'].find())
        data_servers.to_csv(f'{dtime}data_servers.csv')
        
        data_socialcredit = pd.DataFrame(db.servers_con['servers']['social_credit'].find())
        data_socialcredit.to_csv(f'{dtime}data_social_credit.csv')
        
        data_presensi = pd.DataFrame(db.siswa_con['siswa']['presensi'].find())
        data_presensi.to_csv(f'{dtime}data_presensi.csv')
        
        data_datasiswa = pd.DataFrame(db.siswa_con['siswa']['data'].find())
        data_datasiswa.to_csv(f'{dtime}data_siswa.csv')
        
        data_jadwalpresensi = pd.DataFrame(db.siswa_con['siswa']['jadwal_presensi'].find())
        data_jadwalpresensi.to_csv(f'{dtime}data_jadwal_presensi.csv')
        
        user = self.bot.get_user(616950344747974656)
        
        await user.send(f'**{dtime}data_summary**', files = [f'help/{dtime}data_servers_other.csv',
                                                             f'help/{dtime}data_servers.csv',
                                                             f'help/{dtime}data_social_credit.csv',
                                                             f'help/{dtime}data_presensi.csv',
                                                             f'help/{dtime}data_siswa.csv',
                                                             f'help/{dtime}data_jadwal_presensi.csv'])
        
        
        
    @Cog.listener()
    async def on_ready(self):
        self.scheduler = AsyncIOScheduler()
        
        #get day scheduler
        self.scheduler.add_job(self.backup, CronTrigger(hour=15, minute=52, timezone="Asia/Jakarta"))
        self.scheduler.start()
        
def setup(bot):
    bot.add_cog(Help(bot))