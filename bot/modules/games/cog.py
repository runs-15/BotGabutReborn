from discord import Member
from discord import Embed
from discord.ext.commands import Cog, command, slash_command, cooldown, BucketType
import random, discord, db, datetime, asyncio
from discord.utils import get
from discord.ui import InputText, Modal
import numpy as np
                
class Games(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name='quiz.basic-math')
    @cooldown(1, 60, BucketType.user)
    async def basic_math(self, ctx):
        """
        > Shows a simple mathematic sentence. Your task is to answer correctly. Rewards `30 + (operator * 10) + (length each operand * 5)` exp if win and minus half of the rewards if lost. You should answer within `5 + (operator * 3) + (length each operand * 2)` seconds.

        **Params:**
        >    takes no parameter

        **Returns:**
        >    **`embed`** → math question

        **Example:**
        > ```<prefix>quiz.basic-math```
        """
        randomizer = random.randint(1, 6)
        math_sentence = ''
        operand = np.random.choice([x for x in range(1, 101)], randomizer + 1)
        operator = np.random.choice(['+', '-', '*'], randomizer, p=[0.4, 0.4, 0.2])
        
        for i in range(randomizer):
            math_sentence += f'{operand[i]} {operator[i]} '
            
        math_sentence += operand[randomizer]
            
        timeout = 5 + (len(operator) * 3) + (sum(len(str(x)) for x in operand) * 2)
        exp_multiplier = 30 + (len(operator) * 10) + (sum(len(str(x)) for x in operand) * 5)
        
        answer = eval(math_sentence)

        soal_embed = Embed(title = 'Answer this question!')
        soal_embed.add_field(name='Math sentence', value=f'```{math_sentence}```', inline=True)
        soal_embed.add_field(name='Answer Timeout', value=f'```{timeout} seconds```', inline=True)
        soal_embed.add_field(name='Potential Reward', value=f'```{exp_multiplier} exp```', inline=True)
        soal_embed.add_field(name='Clue', value=f'```The right answer has {len(str(answer))} digits```', inline=True)
        soal = await ctx.send(embed=soal_embed)

        def is_correct(m):
            return m.author == ctx.author and m.content.isdigit()

        try:
            guess = await self.bot.wait_for("message", check=is_correct, timeout=timeout)
        except asyncio.TimeoutError:
            db.add_exp(ctx.author.id, -1/2*exp_multiplier)
            return await soal.edit(embed=Embed(title='Time Up!', description=f'Your exp was decreased by **`{exp_multiplier}`**'))

        if guess.content == answer:
            db.add_exp(ctx.author.id, exp_multiplier)
            
            await soal.edit(embed=Embed(title='You got that!', description=f'Your exp was increased by **`{exp_multiplier}`**'))
            await guess.delete()
            
        else:
            db.add_exp(ctx.author.id, -1/2*exp_multiplier)
            await soal.edit(embed=Embed(title='Oops!', description=f'Your exp was decreased by **`{exp_multiplier}`**'))
            await guess.delete()
            
    @command(name='quiz.jumbled-word')
    @cooldown(1, 60, BucketType.user)
    async def jumbled_word(self, ctx):
        """
        > Takes a shuffled word from an English dictionary. Your task is to rearrange the word correctly. Rewards `60 + (word length * 10)` exp if win and minus half of the rewards if lost. You should answer within `5 + (word length * 3)` seconds.

        **Params:**
        >    takes no parameter

        **Returns:**
        >    **`embed`** → jumbled word and clues

        **Example:**
        > ```<prefix>quiz.jumbled-word```
        """
        randomizer = random.randint(0, 54554)
        temp = db.others_con['others']['eng_dict'].find({'index' : randomizer})[0]
        word = answer =  temp['word'].lower()
        clue = temp['meaning']
        taken_by = [temp['taken_by']]
        word = ''
        
        while ctx.author.id in taken_by or len(word) < 3:
            randomizer = random.randint(0, 54554)
            temp = db.others_con['others']['eng_dict'].find({'index' : randomizer})[0]
            answer =  temp['word'].lower()
            clue = temp['meaning']
            taken_by = [temp['taken_by']]
            word = ''
        
        for i in answer.split(' '):
            word += " ".join(random.sample(i, len(i)))
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
            return await soal.edit(embed=Embed(title='Time Up!', description=f'Your exp was decreased by **`{exp_multiplier}`**'))

        if answer in guess.content:
            db.add_exp(ctx.author.id, exp_multiplier)
            taken_by.append(ctx.author.id)
            
            db.others_con['others']['eng_dict'].update_one({'index' : randomizer}, {"$set": {'taken_by': taken_by}})
            await soal.edit(embed=Embed(title='You got that!', description=f'Your exp was increased by **`{exp_multiplier}`**'))
            await guess.delete()
            
        else:
            db.add_exp(ctx.author.id, -1/2*exp_multiplier)
            await soal.edit(embed=Embed(title='Oops!', description=f'Your exp was decreased by **`{exp_multiplier}`**'))
            await guess.delete()
            
def setup(bot):
    bot.add_cog(Games(bot))