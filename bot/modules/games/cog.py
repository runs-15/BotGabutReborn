from discord import Member
from discord import Embed
from discord.ext.commands import Cog, command, slash_command, cooldown, BucketType
import random, discord, db, datetime, asyncio
from discord.utils import get
from discord.ui import InputText, Modal
                
class Games(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name='quiz.jumbled-word')
    @cooldown(1, 60, BucketType.user)
    async def jumbled_word(self, ctx):
        randomizer = random.randint(0, 54554)
        temp = db.others_con['others']['eng_dict'].find({'index' : randomizer})[0]
        word = answer =  temp['word'].lower()
        clue = temp['meaning']
        taken_by = [temp['taken_by']]
        
        while ctx.author.id in taken_by:
            randomizer = random.randint(0, 54554)
            temp = db.others_con['others']['eng_dict'].find({'index' : randomizer})[0]
            word = answer =  temp['word'].lower()
            clue = temp['meaning']
            taken_by = [temp['taken_by']]
        
        word = "".join(random.sample(word, len(word)))
        timeout = 5 + len(word) * 3
        exp_multiplier = 60 + len(word) * 10
        
        soal_embed = Embed(title = 'Arrange the word!')
        soal_embed.add_field(name='Jumbled word', value=f'```{word}```', inline=True)
        soal_embed.add_field(name='Answer Timeout', value=f'```{timeout} seconds```', inline=True)
        soal_embed.add_field(name='Potential Reward', value=f'```{exp_multiplier} exp```', inline=True)
        soal_embed.add_field(name='Clue', value=f'```{clue}```', inline=True)
        soal = await ctx.send(embed=soal_embed)

        def is_correct(m):
            return m.author == ctx.author

        try:
            guess = await self.bot.wait_for("message", check=is_correct, timeout=timeout)
        except asyncio.TimeoutError:
            db.add_exp(ctx.author.id, -1/2*exp_multiplier)
            return await soal.edit(embed=Embed(title='Time Up!', description=f'Your exp decreased by **`{exp_multiplier}`**'))

        if answer in guess.content:
            db.add_exp(ctx.author.id, exp_multiplier)
            taken_by.append(ctx.author.id)
            
            db.others_con['others']['eng_dict'].update_one({'index' : randomizer}, {"$set": {'taken_by': taken_by}})
            await soal.edit(embed=Embed(title='You got that!', description=f'Your exp increased by **`{exp_multiplier}`**'))
            
        else:
            db.add_exp(ctx.author.id, -1/2*exp_multiplier)
            await soal.edit(embed=Embed(title='Oops!', description=f'Your exp decreased by **`{exp_multiplier}`**'))
            

    # @slash_command(name="modaltest", guild_ids=db.guild_list)
    # async def modal_slash(self, ctx):
    #     """Shows an example of a modal dialog being invoked from a slash command."""
    #     temp = db.others_con['others']['eng_dict'].find({'index' : random.randint(0, 54554)})
    #     word = temp['word']
    #     clue = temp['meaning']
        
    #     word = "".join(random.sample(word, len(word)))
    #     modal = Eng_Jumbled_Words(title = 'Arrange the word!')
    #     modal.add_item(
    #         InputText(
    #             label=f"Arrange this word: `{word}`",
    #             placeholder = 'insert answer here'
    #         )
    #     )
    #     async def callback(self, interaction: discord.Interaction):
    #         embed = discord.Embed(title="Your Modal Results", color=discord.Color.random())
    #         embed.add_field(name="First Input", value=self.children[0].value, inline=False)
    #         embed.add_field(name="Second Input", value=self.children[1].value, inline=False)
    #         await interaction.response.send_message(embeds=[embed])
        
    #     await ctx.send_modal(modal)
            
def setup(bot):
    bot.add_cog(Games(bot))