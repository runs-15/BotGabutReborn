from distutils.util import check_environ
from logging.config import stopListening
from discord import Member, StoreChannel, user_command
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
    async def basic_math(self, ctx, level = 1):
        """
        > Shows a simple mathematic sentence. Your task is to answer correctly. Rewards `level * (30 + (operator * 10) + (length each operand * 10))` exp if win and minus half of the rewards if lost. You should answer within `level / 2 * (5 + (operator * 3) + (length each operand * 2))` seconds. Answer decimal with round 2 numbers behind dot.

        **Params:**
        >    **`level`** → question level, default to {`1`} max {`5`}

        **Returns:**
        >    **`embed`** → math question

        **Example:**
        > ```<prefix>quiz.basic-math 3```
        """
        if level < 1 or level > 5:
            ctx.command.reset_cooldown(ctx)
            raise Exception('level should not exceeds range between 1 and 5')
        
        det = {
            1 : [[1, 6], [1,  10],      [0.4, 0.4, 0.2, 0]],
            2 : [[2, 6], [10, 100],     [0.4, 0.4, 0.2, 0]],
            3 : [[3, 7], [100, 500],    [0.3, 0.4, 0.2, 0.1]],
            4 : [[4, 7], [100, 500],    [0.3, 0.3, 0.2, 0.2]],
            5 : [[5, 8], [100,  1000],  [0.25, 0.25, 0.25, 0.25]]
        }
        
        chc = det[int(level)]
        
        randomizer = random.randint(chc[0][0], chc[0][1])
        math_sentence = ''
        math_sentence_true = ''
        operand = np.random.choice([x for x in range(chc[1][0], chc[1][1])], randomizer + 1)
        operator = np.random.choice(['+', '-', '*', '/'], randomizer, p=chc[2])
        
        for i in range(randomizer):
            math_sentence_true += f'{operand[i]} {operator[i]} '
            math_sentence += f'{operand[i]}⠀{operator[i]}⠀' # inserting U+2800 as invisible character to prevent copy - paste
        
        math_sentence_true += str(operand[randomizer])
        math_sentence += str(operand[randomizer])
            
        timeout = level * (5 + (len(operator) * 3) + (sum(len(str(x)) for x in operand) * 2))
        exp_multiplier = level * (30 + (len(operator) * 10) + (sum(len(str(x)) for x in operand) * 5))
        
        answer = round(eval(math_sentence_true), 2)

        soal_embed = Embed(title = 'Solve this question!')
        soal_embed.add_field(name='Math sentence', value=f'```{math_sentence}```', inline=False)
        soal_embed.add_field(name='Answer Timeout', value=f'```{timeout} seconds```', inline=True)
        soal_embed.add_field(name='Potential Reward', value=f'```{exp_multiplier} exp```', inline=True)
        soal_embed.add_field(name='Reminder', value=f"```If the question contains division (/), always put dot, and round two numbers\nExample  : 12.345 → 12.35\n         : 12     → 12.00```", inline=False)
        soal = await ctx.reply(embed=soal_embed)

        def is_correct(m):
            return m.author == ctx.author

        try:
            guess = await self.bot.wait_for("message", check=is_correct, timeout=timeout)
        except asyncio.TimeoutError:
            db.add_exp(ctx.author.id, -1/2*exp_multiplier)
            
            soal_embed = Embed(title = 'Question Summary')
            soal_embed.add_field(name='Math sentence', value=f'```{math_sentence}```', inline=False)
            soal_embed.add_field(name='Answer Timeout', value=f'```{timeout} seconds```', inline=True)
            soal_embed.add_field(name='Potential Reward', value=f'```{exp_multiplier} exp```', inline=True)
            soal_embed.add_field(name='Correct Answer', value=f"```{answer}```", inline=False)
            await soal.edit(embed=soal_embed)
            
            return await ctx.reply(embed=Embed(title="Time's Up!", description=f'Your exp was decreased by **`{1/2 * exp_multiplier}`**'))

        if str(guess.content) == str(answer) or float(guess.content) == float(answer):
            db.add_exp(ctx.author.id, exp_multiplier)
            
            await ctx.reply(embed=Embed(title='You got that!', description=f'Your exp was increased by **`{exp_multiplier}`**'))
            
        else:
            db.add_exp(ctx.author.id, -1/2*exp_multiplier)
            
            soal_embed = Embed(title = 'Question Summary')
            soal_embed.add_field(name='Math sentence', value=f'```{math_sentence}```', inline=False)
            soal_embed.add_field(name='Answer Timeout', value=f'```{timeout} seconds```', inline=True)
            soal_embed.add_field(name='Potential Reward', value=f'```{exp_multiplier} exp```', inline=True)
            soal_embed.add_field(name='Correct Answer', value=f"```{answer}```", inline=False)
            await soal.edit(embed=soal_embed)
            
            await ctx.reply(embed=Embed(title='Oops!', description=f'Your exp was decreased by **`{1/2 * exp_multiplier}`**'))
            
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
            return await soal.edit(embed=Embed(title="Time's Up!", description=f'Your exp was decreased by **`{1/2 * exp_multiplier}`**.\nThe correct answer was **{answer}**'))

        if answer in guess.content:
            db.add_exp(ctx.author.id, exp_multiplier)
            taken_by.append(ctx.author.id)
            
            db.others_con['others']['eng_dict'].update_one({'index' : randomizer}, {"$set": {'taken_by': taken_by}})
            await soal.edit(embed=Embed(title='You got that!', description=f'Your exp was increased by **`{exp_multiplier}`**'))
            await guess.delete()
            
        else:
            db.add_exp(ctx.author.id, -1/2*exp_multiplier)
            await soal.edit(embed=Embed(title='Oops!', description=f'Your exp was decreased by **`{1/2 * exp_multiplier}`**\nThe correct answer was **{answer}**'))
            await guess.delete()
            
    @user_command(name="Deadly RPS", guild_ids=db.guild_list, description='Rock-Paper-Scissors with your friend with 100% lowest exp as bid')
    @cooldown(1, 300, BucketType.user)
    async def deadly_rps(self, ctx, member):
        
        if ctx.author.id == member.id:
            ctx.command.reset_cooldown(ctx)
            raise Exception('same player')
        
        player = {ctx.author.id : None, member.id : None}
        a_exp = db.servers_con['servers']['social_credit'].find({'discord_id' : ctx.author.id})[0]['u_exp']
        b_exp = db.servers_con['servers']['social_credit'].find({'discord_id' : member.id})[0]['u_exp']
        taruhan = 0
        
        if a_exp <= 0 or b_exp <= 0:
            ctx.command.reset_cooldown(ctx)
            raise Exception('one of the player has 0 or minus exp')
        
        if a_exp > b_exp:
            taruhan = b_exp
        else:
            taruhan = a_exp
        
        print(taruhan, a_exp, b_exp)
        
        class MyView(discord.ui.View):
            @discord.ui.select(
                placeholder="Pick your side. You CAN'T change this later",
                min_values=1,
                max_values=1,
                options=[
                    discord.SelectOption(emoji = '🗿', label="Rock", value = 'Rock'),
                    discord.SelectOption(emoji = '📄', label="Paper", value = 'Paper'),
                    discord.SelectOption(emoji = '✂', label="Scissors", value = 'Scissors'),
                ],
            )
            async def callback(self, select, interaction: discord.Interaction):
                user = interaction.user
                # Get the rb ole this button is for (stored in the custom ID).

                if user.id not in player.keys():
                    await interaction.response.send_message(f"not eligible", ephemeral=True)
                    return

                # Add the role and send a response to the uesr ephemerally (hidden to other users).
                if user.id in player.keys() and player[user.id] == None:
                    # Give the user the role if they don't already have it.
                    player[user.id] = select.values[0]
                    await interaction.response.send_message(f"You selected {select.values[0]}", ephemeral=True)
                        
                else:
                    await interaction.response.send_message(f"not allowed to change.", ephemeral=True)
                
                print(player)
                winner = None
                if player[ctx.author.id] != None and player[member.id] != None:
                    if player[ctx.author.id] == 'Rock' and player[member.id] == 'Paper':
                        winner = member
                        loser = ctx.author
                    
                    elif player[ctx.author.id] == 'Rock' and player[member.id] == 'Scissors':
                        winner = ctx.author
                        loser = member
                    
                    elif player[ctx.author.id] == 'Paper' and player[member.id] == 'Rock':
                        winner = ctx.author
                        loser = member
                    
                    elif player[ctx.author.id] == 'Paper' and player[member.id] == 'Scissors':
                        winner = member
                        loser = ctx.author
                    
                    elif player[ctx.author.id] == 'Scissors' and player[member.id] == 'Rock':
                        winner = member
                        loser = ctx.author
                    
                    elif player[ctx.author.id] == 'Scissors' and player[member.id] == 'Paper':
                        winner = ctx.author
                        loser = member
                    
                    else:
                        winner = None
                    
                    if winner != None:
                        db.add_exp(winner.id, taruhan)
                        db.add_exp(loser.id, -taruhan)
                        await interaction.channel.send(f"[{ctx.author.mention} with {player[ctx.author.id]} against {member.mention} with **{player[member.id]}**]\nThe RPS winner is {winner.mention}! Got a total of `{db.number_format(taruhan)}` exp")
                    else:
                        await interaction.channel.send(f"[{ctx.author.mention} with {player[ctx.author.id]} against {member.mention} with **{player[member.id]}**]\nThe RPS ended in a draw.")
          
        try:
            view = MyView()
            msg = await ctx.interaction.response.send_message(f"Deadly RPS between {ctx.author.mention} v.s. {member.mention} \n**`{db.number_format(taruhan)}` exp will be given to the winner**. The bid consist of:\n> {ctx.author.mention} with `{round(taruhan / a_exp * 100, 2)}%` of exp\n> {member.mention} with `{round(taruhan / b_exp * 100)}%` of exp", view=view)
        except asyncio.TimeoutError:
            msg = await ctx.interaction.response.edit_message('Timeout!')
            await msg.delete()
    
def setup(bot):
    bot.add_cog(Games(bot))