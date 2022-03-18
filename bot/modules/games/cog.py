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
        > Shows a simple mathematic sentence. Your task is to answer correctly. Rewards `30 + (operator * 10) + (length each operand * 10)` exp if win and minus half of the rewards if lost. You should answer within `5 + (operator * 3) + (length each operand * 2)` seconds.

        **Params:**
        >    takes no parameter

        **Returns:**
        >    **`embed`** → math question

        **Example:**
        > ```<prefix>quiz.basic-math```
        """
        randomizer = random.randint(1, 6)
        math_sentence = ''
        operand = np.random.choice([x for x in range(1, 10)], randomizer + 1)
        operator = np.random.choice(['+', '-', '*'], randomizer, p=[0.4, 0.4, 0.2])
        
        for i in range(randomizer):
            math_sentence += f'{operand[i]} {operator[i]} '
            
        math_sentence += str(operand[randomizer])
            
        timeout = 5 + (len(operator) * 3) + (sum(len(str(x)) for x in operand) * 2)
        exp_multiplier = 30 + (len(operator) * 10) + (sum(len(str(x)) for x in operand) * 10)
        
        answer = eval(math_sentence)

        soal_embed = Embed(title = 'Answer this question!')
        soal_embed.add_field(name='Math sentence', value=f'```{math_sentence}```', inline=True)
        soal_embed.add_field(name='Answer Timeout', value=f'```{timeout} seconds```', inline=True)
        soal_embed.add_field(name='Potential Reward', value=f'```{exp_multiplier} exp```', inline=True)
        soal_embed.add_field(name='Clue', value=f'```The right answer has {len(str(answer))} digits```', inline=True)
        soal = await ctx.reply(embed=soal_embed)

        def is_correct(m):
            return m.author == ctx.author and m.content.isdigit()

        try:
            guess = await self.bot.wait_for("message", check=is_correct, timeout=timeout)
        except asyncio.TimeoutError:
            db.add_exp(ctx.author.id, -1/2*exp_multiplier)
            return await soal.edit(embed=Embed(title='Time Up!', description=f'Your exp was decreased by **`{-1/2 * exp_multiplier}`**'), delete_after=60)

        if int(guess.content) == int(answer) or float(guess.content) == float(answer):
            db.add_exp(ctx.author.id, exp_multiplier)
            
            await soal.edit(embed=Embed(title='You got that!', description=f'Your exp was increased by **`{exp_multiplier}`**'), delete_after=60)
            await guess.delete()
            
        else:
            db.add_exp(ctx.author.id, -1/2*exp_multiplier)
            await soal.edit(embed=Embed(title='Oops!', description=f'Your exp was decreased by **`{-1/2 * exp_multiplier}`**'), delete_after=60)
            await guess.delete()
            
        await ctx.message.delete()
        
    @command(name='quiz.intermediate-math')
    @cooldown(1, 60, BucketType.user)
    async def intermediate_math(self, ctx):
        """
        > Shows a simple mathematic sentence. Your task is to answer correctly. Rewards `30 + (operator * 60) + (length each operand * 20)` exp if win and minus half of the rewards if lost. You should answer within `10 + (operator * 5) + (length each operand * 3)` seconds.

        **Params:**
        >    takes no parameter

        **Returns:**
        >    **`embed`** → math question

        **Example:**
        > ```<prefix>quiz.intermediate-math```
        """
        randomizer = random.randint(1, 6)
        math_sentence = ''
        operand = np.random.choice([x for x in range(10, 100)], randomizer + 1)
        operator = np.random.choice(['+', '-', '*'], randomizer, p=[0.35, 0.35, 0.3])
        
        for i in range(randomizer):
            math_sentence += f'{operand[i]} {operator[i]} '
            
        math_sentence += str(operand[randomizer])
            
        timeout = 10 + (len(operator) * 5) + (sum(len(str(x)) for x in operand) * 3)
        exp_multiplier = 30 + (len(operator) * 10) + (sum(len(str(x)) for x in operand) * 5)
        
        answer = eval(math_sentence)

        soal_embed = Embed(title = 'Answer this question!')
        soal_embed.add_field(name='Math sentence', value=f'```{math_sentence}```', inline=True)
        soal_embed.add_field(name='Answer Timeout', value=f'```{timeout} seconds```', inline=True)
        soal_embed.add_field(name='Potential Reward', value=f'```{exp_multiplier} exp```', inline=True)
        soal_embed.add_field(name='Clue', value=f'```The right answer has {len(str(answer))} digits```', inline=True)
        soal = await ctx.reply(embed=soal_embed)

        def is_correct(m):
            return m.author == ctx.author and m.content.isdigit()

        try:
            guess = await self.bot.wait_for("message", check=is_correct, timeout=timeout)
        except asyncio.TimeoutError:
            db.add_exp(ctx.author.id, -1/2*exp_multiplier)
            return await soal.edit(embed=Embed(title='Time Up!', description=f'Your exp was decreased by **`{-1/2 * exp_multiplier}`**'), delete_after=60)

        if int(guess.content) == int(answer) or float(guess.content) == float(answer):
            db.add_exp(ctx.author.id, exp_multiplier)
            
            await soal.edit(embed=Embed(title='You got that!', description=f'Your exp was increased by **`{exp_multiplier}`**'), delete_after=60)
            await guess.delete()
            
        else:
            db.add_exp(ctx.author.id, -1/2*exp_multiplier)
            await soal.edit(embed=Embed(title='Oops!', description=f'Your exp was decreased by **`{-1/2 * exp_multiplier}`**'), delete_after=60)
            await guess.delete()
            
        await ctx.message.delete()
    
    @command(name='quiz.complex-math')
    @cooldown(1, 60, BucketType.user)
    async def complex_math(self, ctx):
        """
        > Shows a simple mathematic sentence. Your task is to answer correctly. Rewards `30 + (operator * 120) + (length each operand * 30)` exp if win and minus half of the rewards if lost. You should answer within `15 + (operator * 7) + (length each operand * 5)` seconds.

        **Params:**
        >    takes no parameter

        **Returns:**
        >    **`embed`** → math question

        **Example:**
        > ```<prefix>quiz.basic-math```
        """
        randomizer = random.randint(1, 6)
        math_sentence = ''
        operand = np.random.choice([x for x in range(100, 1000)], randomizer + 1)
        operator = np.random.choice(['+', '-', '*'], randomizer, p=[0.3, 0.3, 0.4])
        
        for i in range(randomizer):
            math_sentence += f'{operand[i]} {operator[i]} '
            
        math_sentence += str(operand[randomizer])
            
        timeout = 15 + (len(operator) * 7) + (sum(len(str(x)) for x in operand) * 5)
        exp_multiplier = 30 + (len(operator) * 120) + (sum(len(str(x)) for x in operand) * 30)
        
        answer = eval(math_sentence)

        soal_embed = Embed(title = 'Answer this question!')
        soal_embed.add_field(name='Math sentence', value=f'```{math_sentence}```', inline=True)
        soal_embed.add_field(name='Answer Timeout', value=f'```{timeout} seconds```', inline=True)
        soal_embed.add_field(name='Potential Reward', value=f'```{exp_multiplier} exp```', inline=True)
        soal_embed.add_field(name='Clue', value=f'```The right answer has {len(str(answer))} digits```', inline=True)
        soal = await ctx.reply(embed=soal_embed)

        def is_correct(m):
            return m.author == ctx.author and m.content.isdigit()

        try:
            guess = await self.bot.wait_for("message", check=is_correct, timeout=timeout)
        except asyncio.TimeoutError:
            db.add_exp(ctx.author.id, -1/2*exp_multiplier)
            return await soal.edit(embed=Embed(title='Time Up!', description=f'Your exp was decreased by **`{-1/2 * exp_multiplier}`**'), delete_after=60)

        if int(guess.content) == int(answer) or float(guess.content) == float(answer):
            db.add_exp(ctx.author.id, exp_multiplier)
            
            await soal.edit(embed=Embed(title='You got that!', description=f'Your exp was increased by **`{exp_multiplier}`**'), delete_after=60)
            await guess.delete()
            
        else:
            db.add_exp(ctx.author.id, -1/2*exp_multiplier)
            await soal.edit(embed=Embed(title='Oops!', description=f'Your exp was decreased by **`{-1/2 * exp_multiplier}`**'), delete_after=60)
            await guess.delete()
            
        await ctx.message.delete()
            
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
        answer = temp['word'].lower()
        clue = temp['meaning']
        taken_by = [temp['taken_by']]
        word = ''
        
        while ctx.author.id in taken_by or len(answer) < 3:
            randomizer = random.randint(0, 54554)
            temp = db.others_con['others']['eng_dict'].find({'index' : randomizer})[0]
            answer = temp['word'].lower()
            clue = temp['meaning']
            taken_by = [temp['taken_by']]
            word = ''
        
        if ' ' in answer:
            lst = []
            for i in answer.split(' '):
                lst.append("".join(random.sample(i, len(i))))
            word = " ".join(random.sample(lst, len(lst)))
        else:
            word = "".join(random.sample(answer, len(answer)))

        timeout = 5 + len(word) * 3
        exp_multiplier = 60 + len(word) * 10

        soal_embed = Embed(title = 'Arrange the word!')
        soal_embed.add_field(name='Jumbled word', value=f'```{word}```', inline=True)
        soal_embed.add_field(name='Answer Timeout', value=f'```{timeout} seconds```', inline=True)
        soal_embed.add_field(name='Potential Reward', value=f'```{exp_multiplier} exp```', inline=True)
        soal_embed.add_field(name='Clue', value=f'```{clue}```', inline=True)
        soal = await ctx.reply(embed=soal_embed)

        def is_correct(m):
            return m.author == ctx.author

        try:
            guess = await self.bot.wait_for("message", check=is_correct, timeout=timeout)
        except asyncio.TimeoutError:
            db.add_exp(ctx.author.id, -1/2*exp_multiplier)
            return await soal.edit(embed=Embed(title='Time Up!', description=f'Your exp was decreased by **`{-1/2 * exp_multiplier}`**'), delete_after=60)

        if answer in guess.content:
            db.add_exp(ctx.author.id, exp_multiplier)
            taken_by.append(ctx.author.id)
            
            db.others_con['others']['eng_dict'].update_one({'index' : randomizer}, {"$set": {'taken_by': taken_by}})
            await soal.edit(embed=Embed(title='You got that!', description=f'Your exp was increased by **`{exp_multiplier}`**'), delete_after=60)
            await guess.delete()
            
        else:
            db.add_exp(ctx.author.id, -1/2*exp_multiplier)
            await soal.edit(embed=Embed(title='Oops!', description=f'Your exp was decreased by **`{-1/2 * exp_multiplier}`**'), delete_after=60)
            await guess.delete()
            
        await ctx.message.delete()
            
    @slash_command(name="deadly-rps", guild_ids=db.guild_list, description='Rock-Paper-Scissors with your friend with exp as bid')
    @cooldown(1, 300, BucketType.user)
    async def deadly_rps(self, ctx, member : discord.Member):
        player = {}
        
        class MyView(discord.ui.View):
            @discord.ui.select(
                placeholder="Pick your side. Remember: you cannot change this later",
                min_values=1,
                max_values=1,
                options=[
                    discord.SelectOption(emoji = '🗿', label="Rock"),
                    discord.SelectOption(emoji = '📄', label="Paper"),
                    discord.SelectOption(emoji = '✂', label="Scissors"),
                ],
            )
            async def callback(self, interaction: discord.Interaction):
                if ctx.author.id not in player.keys():
                    player[ctx.author.id] = self.values[0]
                    await interaction.response.send_message(f"You selected {self.values[0]}.", ephemeral=True)
                if member.id not in player.keys():
                    player[member.id] = self.values[0]
                    await interaction.response.send_message(f"You selected {self.values[0]}.", ephemeral=True)
                await interaction.response.send_message(f"not eligible", ephemeral=True)

        view = MyView()
        await ctx.interaction.response.send_message(f"deadly rps between {ctx.author.mention} v.s. {member.mention}", view=view)
    
def setup(bot):
    bot.add_cog(Games(bot))