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
            
def setup(bot):
    bot.add_cog(Fun(bot))