from discord.ext.commands import Cog, slash_command, command, message_command, user_command
from discord.ui import InputText, Modal
import discord, db, os, sys
from discord.commands import Option

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

    @message_command(name="messagemodal", guild_ids=db.guild_list)
    async def modal_message(self, ctx, message):
        """Shows an example of a modal dialog being invoked from a message command."""
        modal = MyModal(title="Message Command Modal")
        modal.title = f"Modal for Message ID: {message.id}"
        await ctx.interaction.response.send_modal(modal)

    @user_command(name="usermodal", guild_ids=db.guild_list)
    async def modal_user(self, ctx, member):
        """Shows an example of a modal dialog being invoked from a user command."""
        modal = MyModal(title="User Command Modal")
        modal.title = f"Modal for User: {member.display_name}"
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
    
def setup(bot):
    bot.add_cog(Tools(bot))