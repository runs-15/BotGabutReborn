from discord import Member
from discord import Embed
from discord.ext.commands import Cog, command, slash_command
import random, discord, db, datetime
from discord.utils import get

class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="slap", aliases=["hit", "tampar"])
    async def slap(self, ctx, member: Member, *, reason = "no reason"):
        await ctx.send(f"{ctx.author.display_name} menampar {member.mention} karena {reason}")

    @command(name="echo", aliases=["bot.say"])
    async def echo(self, ctx, *, message):
        await ctx.message.delete()
        await ctx.send(message)

    @command(name="slot", aliases=["slots", "bet"])
    async def slot(self, ctx):
        """Mesin slot keberuntungan!!!"""
        emojis = "🍎🍊🍐🍋🍉🍇🍓🍒"
        a = random.choice(emojis)
        b = random.choice(emojis)
        c = random.choice(emojis)

        mesinslot = f"**[ {a} {b} {c} ]\n{ctx.author.name}**,"

        if (a == b == c):
            await ctx.send(f"{mesinslot} Rupanya jatah luck anda setahun habis!! 🎉")
        elif (a == b) or (a == c) or (b == c):
            await ctx.send(f"{mesinslot} Hmm, not bad not bad (☞ﾟヮﾟ)☞)")
        else:
            await ctx.send(f"{mesinslot} Noob emang (￣(工)￣)")

    @command(name="avatar", aliases=["pp", "pic"])
    async def avatar(self, ctx, member: Member):
        if member == None:
            member = ctx.author
            embed = Embed(title=f"Profile Picture", description=f"{member.mention}'s profile picture!", colour=ctx.author.colour)
            embed.set_image(url=member.avatar.url)
            await ctx.send(embed=embed)
        else:
            embed = Embed(title=f"Profile Picture", description=f"{member.mention}'s profile picture!", colour=ctx.author.colour)
            embed.set_image(url=member.avatar.url)
            await ctx.send(embed=embed)
            
    @slash_command(guild_ids=[850284530501812224], name="rps", description="Rock Paper Scissor with me")
    async def rps(self, ctx, pilihan):
        await ctx.respond(pilihan)
        
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
        
    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("fun")
            
def setup(bot):
    bot.add_cog(Fun(bot))