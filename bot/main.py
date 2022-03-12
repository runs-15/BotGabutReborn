import os, server, discord, db, datetime
#import pynacl
#import dnspython
from discord.ext import commands
from discord.ext.commands import when_mentioned_or
from time import sleep
from discord.utils import get
from discord import Embed

description = """An example bot to showcase the discord.ext.commands extension module.
There are a number of utility commands being showcased here."""

intents = discord.Intents.all()

def get_prefix(bot, message):
    prefix = db.servers_con.servers.server.find({'server_id' : message.guild.id})[0]['prefix']
    return when_mentioned_or(prefix)(bot, message)

bot = commands.Bot(command_prefix=get_prefix, description=description, intents=intents)
TOKEN = os.getenv('BOT_TOKEN')
    
for folder in os.listdir("bot/modules"):
    sleep(0.5)
    if os.path.exists(os.path.join("bot/modules", folder, "cog.py")):
        bot.load_extension(f"modules.{folder}.cog")
        print(f"    {folder} cogs loaded!")
        
def syntax(command):
    cmd_and_aliases = "|".join([str(command), *command.aliases])
    params = []
    
    for key, value in command.params.items():
        if key not in ("self", "ctx"):
            params.append(f"[{key}]" if "=" in str(value) else f"<{key}>")
    params = " ".join(params)
    return f"```{cmd_and_aliases} {params}```"
        
async def cmd_help(ctx, command):
    embed = Embed(title=f"Bantuan perintah `{command}`", description=syntax(command), colour=int(hex(int("2f3136", 16)), 0), timestamp=datetime.datetime.now())
    embed.add_field(name="Deskripsi perintah: ", value=command.help)
    embed.set_author(name=bot.user.name, icon_url=bot.user.avatar.url)
    await ctx.send(embed=embed)

@bot.listener()        
async def on_command_error(ctx, exc):
    if isinstance(exc, discord.ext.commands.CommandNotFound):
        cmd_lst = ''
        for i in bot.commands:
            if ctx.message.content.split()[0].lstrip(db.servers_con['servers']['server'].find({'server_id' : ctx.guild.id})[0]['prefix']) in i.name or ctx.message.content.split()[0].lstrip(db.servers_con['servers']['server'].find({'server_id' : ctx.guild.id})[0]['prefix']) in ' '.join(i.aliases):
                cmd_lst += f'`{i or " ".join(i.aliases)}` '
                continue
        if cmd_lst != '':
            hlp = await ctx.reply(f"Command not available, or maybe call {cmd_lst}instead?")
        else:
            hlp = await ctx.reply("Command not available")
    else:
        print(exc)
                    
        if (command := get(bot.commands, name=ctx.message.content.split()[0].lstrip(db.servers_con['servers']['server'].find({'server_id' : ctx.guild.id})[0]['prefix']))):
            await ctx.reply(f"```{str(exc)}```", embed=await cmd_help(ctx, command))

@bot.event
async def on_ready():
    await bot.wait_until_ready()
    print(f"We have logged in as {bot.user}")

server.server()
bot.run(TOKEN)