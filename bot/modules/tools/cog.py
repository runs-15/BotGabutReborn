from aiohttp import DataQueue
from discord.ext.commands import Cog, slash_command, command, message_command, user_command, cooldown, BucketType
from discord.ui import InputText, Modal, Select, Button
import discord, db, os, sys, random, datetime, math, asyncio
import pandas as pd
from discord.commands import Option
from asyncio import sleep
from discord.utils import get
import re, time, random
import seaborn as sns
import matplotlib.pyplot as plt
from numpy import *

def string2func(string):
    ''' evaluates the string and returns a function of x '''
    # find all words and check if all are allowed:
    replacements = {
        'sin' : 'np.sin',
        'cos' : 'np.cos',
        'exp': 'np.exp',
        'sqrt': 'np.sqrt',
        '^': '**',
        'pi': 'np.pi',
        'floor' : 'np.floor'
    }

    allowed_words = [
        'x',
        'sin',
        'cos',
        'sqrt',
        'exp',
        'pi',
        'time',
        'floor',
        'np',
        'tan',
        'ceil',
        'fix',
        'rint',
        'trunc'
    ]

    for word in re.findall('[a-zA-Z_]+', string):
        if word not in allowed_words:
            raise ValueError(
                '"{}" is forbidden to use in math expression'.format(word)
            )

    #for old, new in replacements.items():
        #string = string.replace(old, new)

    def func(x):
        return eval(string)

    return func

class MyModal(Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(InputText(label="Short Input", placeholder="Placeholder Test"))

        self.add_item(
            InputText(
                label="Longer Input",
                value="Longer Value\nSuper Long Value",
                style=discord.InputTextStyle.long,
            )
        )

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Your Modal Results", color=discord.Color.random())
        embed.add_field(name="First Input", value=self.children[0].value, inline=False)
        embed.add_field(name="Second Input", value=self.children[1].value, inline=False)
        await interaction.response.send_message(embeds=[embed])
        
class createVC(Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.custom_vc = {}
        self.add_item(InputText(label="Channel Name", placeholder="Wumpus Land"))
        self.add_item(InputText(label="User Limit", placeholder="64"))
        self.add_item(InputText(label="Bitrate", placeholder="64"))
        self.add_item(InputText(label="Region Override", placeholder="automatic", required = False))
        # self.add_item(Button(label="Region Override", style = discord.ButtonStyle.secondary, disabled=True))
        # self.add_item(Select(label="Region Override",placeholder="Automatic", 
        #                      options=
        #                      [Select.add_option(label = "Automatic", value = "automatic", default = True),
        #                       Select.add_option(label = "Brazil", value = "brazil"),
        #                       Select.add_option(label = "Hong Kong", value = "hongkong"),
        #                       Select.add_option(label = "India", value = "india"),
        #                       Select.add_option(label = "Japan", value = "japan"),
        #                       Select.add_option(label = "Rotterdam", value = "amsterdam"),
        #                       Select.add_option(label = "Russia", value = "russia"),
        #                       Select.add_option(label = "Singapore", value = "singapore"),
        #                       Select.add_option(label = "South Africa", value = "southafrica"),
        #                       Select.add_option(label = "Sydney", value = "sydney"),
        #                       Select.add_option(label = "US Central", value = "us_central"),
        #                       Select.add_option(label = "US South", value = "us_south"),
        #                       Select.add_option(label = "US West", value = "us_west"),
        #                       Select.add_option(label = "US East", value = "us_east")
        #                       ]
        #                      ), default = "automatic")

    async def callback(self, interaction: discord.Interaction):
        self.custom_vc[interaction.id] = {}
        self.custom_vc[interaction.id]["flag"] = 0
        self.custom_vc[interaction.id]["channel"] = await interaction.guild.create_voice_channel(name = self.children[0].value, user_limit = int(self.children[1].value), bitrate = int(self.children[2].value)*1000, category = interaction.channel.category, rtc_region = self.children[3].value if self.children[3].value != None else None)
        embed = discord.Embed( title="Channel Created!", colour=int(hex(int("2f3136", 16)), 0))
        embed.add_field(name="Channel Name", value=self.custom_vc[interaction.id]["channel"].mention, inline = False)
        embed.add_field(name="User Limit", value=f'`{self.custom_vc[interaction.id]["channel"].user_limit}` user')
        embed.add_field(name="Bitrate", value=f'`{int(self.custom_vc[interaction.id]["channel"].bitrate/1000)}` kbps')
        embed.add_field(name="Channel ID", value=f'`{self.custom_vc[interaction.id]["channel"].id}`', inline = False)
        embed.add_field(name="Position", value=f'`{self.custom_vc[interaction.id]["channel"].position}` of `{len(interaction.guild.channels)}`')
        embed.add_field(name="Region", value="`automatic`" if self.custom_vc[interaction.id]["channel"].rtc_region == None else self.custom_vc[interaction.id]["channel"].rtc_region)
        await interaction.response.send_message(embed=embed)
        await sleep(300)
        if len(self.custom_vc[interaction.id]["channel"].members) == 0:
            await self.custom_vc[interaction.id]["channel"].delete()
        else:
            self.custom_vc[interaction.id]["flag"] = 1
            
class Tools(Cog):
    def __init__(self, bot):
        self.bot = bot
        
    #on_guild_join prefix set up
    @Cog.listener()
    async def on_guild_join(self, guild):
        db.servers_con['servers']['server'].insert_one(
            {'server_id' : guild.id,
            'name' : guild.name,
            'owner': guild.owner_id,
            'prefix' : '>>',
            'presensi_channel' : None,
            'shalat_channel' : {'id' : None,
                                'kota' : 'Jakarta',
                                'negara' : 'Indonesia',
                                'metode' : 3,},
            'quran_channel' : {'id' : None,
                               'tranlation' : 'id.indonesian'},
            'birthday_channel' : None,
            'logging_channel' : None}
        )
        
    @slash_command(name="register-guild",description="Memasukkan data server dalam database")
    async def registerGuild(
        self,
        ctx,
        prefix: Option(str, "Bot prefix's for your channel (max. 5 char.)", required=False, default='>>'),
        presensi: Option(discord.TextChannel, "Channel presensi", required=False, default=None),
        shalat: Option(discord.TextChannel, "Channel shalat", required=False, default=None),
        quran: Option(discord.TextChannel, "Channel Qur'an", required=False, default=None),
        birthday: Option(discord.TextChannel, "Channel birthday", required=False, default=None),
        logging: Option(discord.TextChannel, "Channel logging message", required=False, default=None),
        ):
        try:
            if ctx.guild.id in [i['server_id'] for i in db.servers_con['servers']['server'].find({'server_id' : ctx.guild.id})]:
                if prefix != None and len(prefix) <= 5:
                    db.servers_con['servers']['server'].update_one({'server_id': ctx.guild.id },{ "$set": {'prefix': prefix}})
                if presensi != None:
                    db.servers_con['servers']['server'].update_one({'server_id': ctx.guild.id },{ "$set": {'presensi_channel': presensi.id}})
                if shalat != None:
                    db.servers_con['servers']['server'].update_one({'server_id': ctx.guild.id },{ "$set": {'shalat_channel.id' : shalat.id}})
                if quran != None:
                    db.servers_con['servers']['server'].update_one({'server_id': ctx.guild.id },{ "$set": {'quran_channel.id' : quran.id}})
                if birthday != None:
                    db.servers_con['servers']['server'].update_one({'server_id': ctx.guild.id },{ "$set": {'birthday_channel': birthday.id}})
                if logging != None:
                    db.servers_con['servers']['server'].update_one({'server_id': ctx.guild.id },{ "$set": {'logging_channel': logging.id}})
                await ctx.respond('Command successfully executed!')
            else:
                db.servers_con['servers']['server'].insert_one(
                    {'server_id' : ctx.guild.id,
                    'name' : ctx.guild.name,
                    'owner': ctx.guild.owner_id,
                    'prefix' : prefix,
                    'presensi_channel' : presensi.id if presensi != None else None,
                    'shalat_channel' : {'id' : shalat.id if shalat != None else None,
                                        'kota' : 'Jakarta',
                                        'negara' : 'Indonesia',
                                        'metode' : 3,},
                    'quran_channel' : {'id' : quran.id if quran != None else None,
                                       'tranlation' : 'id.indonesian'},
                    'birthday_channel' : birthday.id if birthday != None else None,
                    'logging_channel' : logging.id if logging != None else None}
                )
                await ctx.respond('Command successfully executed!')
        except:
            db.servers_con['servers']['server'].insert_one(
                {'server_id' : ctx.guild.id,
                 'name' : ctx.guild.name,
                 'owner': ctx.guild.owner_id,
                 'prefix' : prefix,
                 'presensi_channel' : presensi.id if presensi != None else None,
                 'shalat_channel' : {'id' : shalat.id if shalat != None else None,
                                     'kota' : 'Jakarta',
                                     'negara' : 'Indonesia',
                                     'metode' : 3,},
                'quran_channel' : {'id' : quran.id if quran != None else None,
                                   'tranlation' : 'id.indonesian'},
                 'birthday_channel' : birthday.id if birthday != None else None,
                 'logging_channel' : logging.id if logging != None else None}
            )
            await ctx.respond('Command successfully executed!')
            
    @slash_command(name="interact",description="Interaksi dengan bot")
    async def interact_first(self, ctx):
        user = self.bot.get_user(ctx.author.id)
        await user.send('This is an interaction from this bot')
        await ctx.respond(content='Thank u!', ephemeral=True)
        
    def restart_bot(self): 
        os.execv(sys.executable, ['python'] + sys.argv)
        
    @command(name='restart')
    async def restart(self, ctx):
        if ctx.author.id == 616950344747974656:
            await ctx.send("Restarting bot...")
            self.restart_bot()
            
    @command(name='fetch_members')
    async def fetch_mmbrs(self, ctx):
        if ctx.author.id == 616950344747974656:
            async for member in ctx.guild.fetch_members():
                print(member.name, member.id)

    @slash_command(name="modaltest", guild_ids=db.guild_list)
    async def modal_slash(self, ctx):
        """Shows an example of a modal dialog being invoked from a slash command."""
        modal = MyModal(title="Slash Command Modal")
        await ctx.interaction.response.send_modal(modal)

    @command()
    async def modaltest(self, ctx):
        """Shows an example of modals being invoked from an interaction component (e.g. a button or select menu)"""

        class MyView(discord.ui.View):
            @discord.ui.button(label="Modal Test", style=discord.ButtonStyle.primary)
            async def button_callback(self, button, interaction):
                modal = MyModal(title="Modal Triggered from Button")
                await interaction.response.send_modal(modal)

            @discord.ui.select(
                placeholder="Pick Your Modal",
                min_values=1,
                max_values=1,
                options=[
                    discord.SelectOption(label="First Modal", description="Shows the first modal"),
                    discord.SelectOption(label="Second Modal", description="Shows the second modal"),
                ],
            )
            async def select_callback(self, select, interaction):
                modal = MyModal(title="Temporary Title")
                modal.title = select.values[0]
                await interaction.response.send_modal(modal)

        view = MyView()
        await ctx.send("Click Button, Receive Modal", view=view)
     
    @slash_command(name="custom-voice-channel", guild_ids=db.guild_list)
    @cooldown(1, 300, BucketType.user)
    async def modal_vcc(self, ctx):
        """Shows an example of a modal dialog being invoked from a slash command."""
        modal = createVC(title="Create Custom Voice Channel")
        await ctx.interaction.response.send_modal(modal)
    
    @command(name='bangunin_orang')    
    async def bangun(self, ctx, member : discord.Member, kali):
        if ctx.author.id == 616950344747974656:
            init = member.voice.channel
            await ctx.send("on progress")
            for i in range(0, int(kali)):
                await member.edit(voice_channel=random.choice(ctx.guild.voice_channels))
            await member.edit(voice_channel=init)
            
    @command(name='random')    
    async def randomm(self, ctx, *cat):
        data = [x for x in cat]
        await ctx.send(f'**{random.choice(data)}**')
        
    @command(name='sequence')    
    async def seq_orang(self, ctx, channel : discord.VoiceChannel):
        data = [x for x in channel.members]
        not_join = [x for x in ctx.guild.members if x not in data]
        data = random.sample(data, len(data)) if len(data) >= 1 else data
        str_orang = '\n'.join([f'{index + 1}. {member.mention}' for index, member in enumerate(data)])
        str_not_joined = ', '.join([f'{member.mention}' for member in not_join])
        await ctx.reply(f'**Urutan Membaca: **\n{str_orang}\n\nDimohon kepada:\n{str_not_joined}\nuntuk segera bergabung ke channel {channel.mention}!')

    @command(name='plot-function')   
    async def createPlotFunction(self, ctx, function, start = '0', end = '100', step = '1000', title = '', xLabel = 'x', yLabel = 'y'):    
        func = string2func(function)
        # x = np.linspace(start, end, step)

        # plt.plot(x, func(x))
        # plt.xlim(start, end)
        # plt.show()
        
        # x = np.linspace(start, end, step)
        x = linspace(string2func(start)(1), string2func(end)(1), string2func(step)(1))

        # draw the graph
        sns.set(rc={'figure.figsize':(20, 15)})
        sns.set_style('darkgrid')
        fig, ax= plt.subplots()
        ax = sns.lineplot(x=x, y=func(x))
        ax.set_title(f'Generated plot from function f(x) = {function}' if title == '' else title)
        ax.set_xlabel(xLabel)
        ax.set_ylabel(yLabel)
        name = int(time.time())
        plt.savefig(f'{name}.png')
        file = discord.File(f"{name}.png", filename=f"{name}.png")
        
        embed = discord.Embed(title=f"Function Plotting", colour=ctx.author.colour)
        embed.set_image(url=f"attachment://{name}.jpg")
        
        await ctx.send(file=file, embed=embed)
            
    @slash_command(name="cari-data-siswa", guild_ids=db.guild_list)
    async def cari_siswa(self, ctx, query):
        if ctx.channel.category_id == 898167597160341554:
            try:
                await ctx.respond('wait...', ephemeral=True)
                df = pd.DataFrame(list(db.siswa_con['siswa']['data'].find()))
                del df['_id']
                df['nama'] = df['nama'].str.upper()
                df['nis'] = df['nis'].astype(str)
                
                query = query.upper()
                res = df.query('nis.str.contains(@query) or nama.str.contains(@query) or kelas.str.contains(@query) or kelamin.str.contains(@query) or agama.str.contains(@query) or lm.str.contains(@query)', engine='python')
                data = res.values.tolist()
                name = res.columns.values.tolist()
                await ctx.send(f"**Data Siswa** contents:\n\n**{name}**")
                
                lst = [str(n) for n in data]
                per_page = 10 # 10 members per page
                pages = math.ceil(len(lst) / per_page)
                cur_page = 1
                chunk = lst[:per_page]
                linebreak = "\n"
                message = await ctx.send(f"{linebreak.join(chunk)}\nPage `{cur_page}` / `{pages}`")
                await message.add_reaction("◀️")
                await message.add_reaction("▶️")
                active = True
                
                def check(reaction, user):
                    return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"] # or you can use unicodes, respectively: "\u25c0" or "\u25b6"
                    
                while active:
                    try:
                        reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)
                                                
                        if str(reaction.emoji) == "▶️" and cur_page != pages:
                            cur_page += 1
                            if cur_page != pages:
                                chunk = lst[(cur_page-1)*per_page:cur_page*per_page]
                            else:
                                chunk = lst[(cur_page-1)*per_page:]
                            await message.edit(content=f"{linebreak.join(chunk)}\nPage `{cur_page}` / `{pages}`")
                            await message.remove_reaction(reaction, user)
                            
                        elif str(reaction.emoji) == "◀️" and cur_page > 1:
                            cur_page -= 1
                            chunk = lst[(cur_page-1)*per_page:cur_page*per_page]
                            await message.edit(content=f"{linebreak.join(chunk)}\nPage `{cur_page}` / `{pages}`")
                            await message.remove_reaction(reaction, user)
                    except asyncio.TimeoutError:
                        await message.delete()
                        active = False
                
            except Exception as e:
                await ctx.respond(f"Exception: {e}")
        else:
            await ctx.respond(f"Not permitted!")
    
def setup(bot):
    bot.add_cog(Tools(bot))