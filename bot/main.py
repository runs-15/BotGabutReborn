import os, server, discord, db, random
#import pynacl
#import dnspython
from discord.ext import commands
from discord.ext.commands import when_mentioned_or

description = """An example bot to showcase the discord.ext.commands extension module.
There are a number of utility commands being showcased here."""

intents = discord.Intents.default()
intents.members = True

def get_prefix(bot, message):
    prefix = db.servers_con.servers.server.find({'server_id' : message.guild.id})[0]['prefix']
    return when_mentioned_or(prefix)(bot, message)

bot = commands.Bot(command_prefix=get_prefix, description=description, intents=intents)
#TOKEN = os.getenv('BOT_TOKEN')
    
for folder in os.listdir("bot\modules"):
    if os.path.exists(os.path.join("bot\modules", folder, "cog.py")):
        bot.load_extension(f"modules.{folder}.cog")
        print(f"    {folder} cogs loaded!")

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

server.server()
bot.run(TOKEN)