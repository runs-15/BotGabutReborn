from discord.ext.commands import Cog, slash_command
import discord, db
from discord.commands import Option

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
    
def setup(bot):
    bot.add_cog(Tools(bot))