from discord import Intents, Embed
import discord
from glob import glob
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import when_mentioned_or
from discord.utils import get
import datetime
import os, server, discord, db, datetime
#import pynacl
#import dnspython
from discord.ext import commands
from discord.ext.commands import when_mentioned_or
from time import sleep
from discord import Embed


def get_prefix(bot, message):
    prefix = db.servers_con['servers']['server'].find({'server_id' : message.guild.id})[0]['prefix']
    return when_mentioned_or(prefix)(bot, message)

def syntax(command):
    cmd_and_aliases = "|".join([str(command), *command.aliases])
    params = []

    for key, value in command.params.items():
        if key not in ("self", "ctx"):
            params.append(f"[{key}]" if "=" in str(value) else f"<{key}>")
    params = " ".join(params)
    return f"```{cmd_and_aliases} {params}```"

class Ready(object):
    def __init__(self):
        for cog in os.listdir("bot/modules"):
            setattr(self, cog, False)
    
    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f" >{cog} cog ready")

    def all_ready(self):
        return all([getattr(self, cog) for cog in os.listdir("bot/modules")])

class Bot(BotBase):
    def __init__(self):
        self.ready = False
        self.cogs_ready = Ready()
        self.guild = None
        self.scheduler = AsyncIOScheduler()
        
        super().__init__(command_prefix=get_prefix, intents=Intents.all())

    def setup(self):
        for folder in os.listdir("bot/modules"):
            if os.path.exists(os.path.join("bot/modules", folder, "cog.py")):
                self.load_extension(f"modules.{folder}.cog")
                print(f"    {folder} cogs loaded!")
        print("setup completed")

    def run(self):

        print("running setup...")
        self.setup()
        self.TOKEN = os.getenv('BOT_TOKEN')

        print("running bot...")
        super().run(self.TOKEN, reconnect=True)

    # async def process_commands(self, message):
    #     ctx = await self.get_context(message, cls=Context)

    #     if ctx.command is not None and ctx.guild is not None:
    #         if self.ready:
    #             await self.invoke(ctx)
    #         else:
    #             await ctx.send("Belum siap menerima perintah. Tunggu beberapa saat")

    #async def rules_reminder(self):
    #    await self.stdout.send("I don't sleep")

    async def on_connect(self):
        print("bot connected")

    async def on_disconnect(self):
        print("bot disconnected")

    async def cmd_help(self, ctx, command):
        embed = Embed(title=f"Bantuan perintah `{command}`", description=syntax(command), colour=int(hex(int("2f3136", 16)), 0), timestamp=datetime.datetime.now())
        embed.add_field(name="Deskripsi perintah: ", value=command.help)
        embed.set_author(name=bot.user.name, icon_url=bot.user.avatar_url)
        await ctx.send(embed=embed)

    async def on_command_error(self, ctx, exc):
        if isinstance(exc, discord.ext.commands.CommandNotFound):
            cmd_lst = ''
            for i in bot.commands:
                if ctx.message.content.split()[0].lstrip(db.servers_con['servers']['server'].find({'server_id' : ctx.guild.id})[0]['prefix']) in ' '.join(i.aliases):
                    cmd_lst += f'`{i or " ".join(i.aliases)}` '
                    continue
            if cmd_lst != '':
                hlp = await ctx.reply(f"Command not available, or maybe call {cmd_lst}instead?")
            else:
                hlp = await ctx.reply("Command not available")
        else:
            print(exc)
            
            if (command := get(bot.commands, name=ctx.message.content.split()[0].lstrip(db.servers_con['servers']['server'].find({'server_id' : ctx.guild.id})[0]['prefix']))):
                await ctx.reply(f"```{str(exc)}```", embed=await self.cmd_help(ctx, command))

    async def on_ready(self):
        if not self.ready:
            # self.guild = self.get_guild(836835374696628244)
            # self.stdout = self.get_channel(846188467834978364)
            # count = db.field("SELECT launchCount FROM launchDebug")
            # db.execute("UPDATE launchDebug SET launchCount = ? WHERE launchCount = ?", int(count)+1, count)
            # db.commit()
            # await self.stdout.send(f"Now Online! -- This is the {count+1} launch-debug")
            # await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=f"the {count+1}{'-st' if str(count+1)[-1] == '1' else ('-nd' if str(count+1)[-1] == '2' else ('-rd' if str(count+1)[-1] == '3' else '-th'))} deployment | Version: {VERSION}"))
            
            self.scheduler.start()

            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            self.ready = True
            print("bot ready")

        else:
            print("bot reconnected")

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)

bot = Bot()