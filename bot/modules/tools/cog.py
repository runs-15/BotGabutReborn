from aiohttp import DataQueue
from discord.ext.commands import Cog, slash_command, command, message_command, user_command, cooldown, BucketType
from discord.ui import InputText, Modal, Select, Button
import discord, db, os, sys, random, datetime
from discord.commands import Option
from asyncio import sleep
from discord.utils import get

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
        modal = createVC(title="CreateCustom Voice Channel")
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
    async def bangun(self, ctx, *cat):
        data = [x for x in cat]
        await ctx.send(f'**{random.choice(data)}**')
    
    def syntax(self, command):
        cmd_and_aliases = "|".join([str(command), *command.aliases])
        params = []
        
        for key, value in command.params.items():
            if key not in ("self", "ctx"):
                params.append(f"[{key}]" if "=" in str(value) else f"<{key}>")
        params = " ".join(params)
        return f"```{cmd_and_aliases} {params}```"
            
    async def cmd_help(self, ctx, command):
        embed = discord.Embed(title=f"Bantuan perintah `{command}`", description=self.syntax(command), colour=int(hex(int("2f3136", 16)), 0), timestamp=datetime.datetime.now())
        embed.add_field(name="Deskripsi perintah: ", value=command.help)
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        await ctx.send(embed=embed)
            
    @Cog.listener()
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
                        
            if (command := get(self.bot.commands, name=ctx.message.content.split()[0].lstrip(db.field("SELECT Prefix FROM guilds WHERE GuildID = ?", ctx.guild.id)))):
                await ctx.reply(f"```{str(exc)}```", embed=await self.cmd_help(ctx, command))
    
def setup(bot):
    bot.add_cog(Tools(bot))