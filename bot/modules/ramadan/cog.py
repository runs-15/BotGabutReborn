from discord.ext.commands import Cog, slash_command, command, message_command, user_command, cooldown, BucketType
from discord.ui import InputText, Modal, Select, Button
import discord, db, os, sys, random, datetime, math, asyncio
import pandas as pd
from discord.commands import Option, OptionChoice
from asyncio import sleep
from discord.utils import get
from discord.ext import tasks
import re, time, random
import seaborn as sns
import matplotlib.pyplot as plt
    
class Ramadan(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = {}
        self.channel_data = None
        self.perizinan = {}
        self.alasan = {}
        self.member_data = {}
        
    @command(name="ramadan.initialize", hidden = True)
    async def ramadan_user(self, ctx):
        if ctx.author.id == 616950344747974656:
            for member in [m for m in ctx.guild.members if not m.bot]:
                db.servers_con['ramadan']['jumlah_kehadiran'].insert_one({'discord_id' : member.id,
                                                                           'kehadiran' : 0,
                                                                           'ketidakhadiran' : { 'beralasan' : 0,
                                                                                                'tidak_beralasan' : 0,
                                                                                                'streak' : 0}
                                                                           })
            await ctx.send("Command Executed!")
        
    @slash_command(name="sequence", guild_ids=[960081979754283058], description = 'sequence over the channel members.')    
    async def seq_orang(self, ctx, channel : Option(discord.VoiceChannel, 'channel for applying sequence', required = True)):
        self.channel_data = channel
        data = [x for x in channel.members]
        not_join = [x for x in ctx.guild.members if x not in data and not x.bot]
        if len(data) >= 1:
            data_end = random.sample(data, len(data))
        else:
            data_end = data
        str_orang = '\n'.join([f'{index + 1}. {member.mention}' for index, member in enumerate(data_end)])
        str_not_joined = ', '.join([f'{member.mention}' for member in not_join])
        self.data = dict(zip([x.id for x in ctx.guild.members if not x.bot], [0 for i in range(len(ctx.guild.members) - len([x for x in ctx.guild.members if not x.bot]))]))
        self.perizinan = dict(zip([x.id for x in ctx.guild.members if not x.bot], [0 for i in range(len(ctx.guild.members) - len([x for x in ctx.guild.members if not x.bot]))]))
        if ctx.author.id == 616950344747974656:
            self.records_presence.start(ctx)
        await ctx.respond(f'**Urutan Membaca: **\n{str_orang}\n\nDimohon kepada:\n{str_not_joined} untuk segera bergabung ke channel {channel.mention}!\nBagi yang berhalangan hadir diharapkan untuk segera izin **sebelum sesi berakhir!**\n\nFormat perizinan: ```!izin <alasan> | contoh: \n!izin tadarus di masjid```')
    
    @command(name='izin')
    async def izin(self, ctx, *alasan):
        self.alasan[ctx.author.id] = (ctx.message.id, ' '.join(alasan), 0)
        report = self.bot.get_channel(961632363996127364)
        await report.send(f'{ctx.author.mention} tidak bisa hadir karena {" ".join(alasan)}')
        
    @slash_command(name="accept", guild_ids=[960081979754283058])
    async def accept(self, ctx, message_id: Option(str, "message id", required=True), decider: Option(int, "accept or not", choices=[-1, 0, 1, 2])):
        if ctx.author.id == 616950344747974656:
            msg = await ctx.fetch_message(int(message_id))
            if decider != -1:
                self.perizinan[msg.author.id] = decider
                await ctx.respond('accepted.' if decider == 1 else 'declined.', ephemeral = True)
                await msg.author.send('reason accepted.' if decider == 1 else 'reason declined.')
            else:
                member = msg.author
                await ctx.respond(f'{msg.author.mention} will be kicked.', ephemeral = True)
                await member.send('Maaf, Anda telah dikeluarkan dari server karena alasan yang sama sekali tidak dapat diterima.')
                await member.kick(reason='severe unappealed reason.')
    
    @tasks.loop(seconds = 60, count = 90)
    async def records_presence(self, ctx):
        print('recording presence')
        if ctx.author.id == 616950344747974656:
            self.member_data = dict(zip([x.id for x in ctx.guild.members if not x.bot], [x for x in ctx.guild.members if not x.bot]))
            for member in ctx.guild.members:
                if member.id not in self.perizinan.keys():
                    self.perizinan[member.id] = 0
                if member in self.channel_data.members and member.id in self.data.keys():
                    self.data[member.id] += 1
                elif member in self.channel_data.members and member.id not in self.data.keys():
                    self.data[member.id] = 1
                else:
                    self.data[member.id] = 0

    @records_presence.after_loop
    async def after_records_presence(self):
        print('finished recording', self.data, self.perizinan)
        hadir = []
        tidak_hadir_beralasan = []
        tidak_hadir_tidak_beralasan = []
        tidak_hadir_abai = []
        for key, value in self.data.items():
            if list(db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})) == []:
                db.servers_con['ramadan']['jumlah_kehadiran'].insert_one({'discord_id' : key,
                                                                           'kehadiran' : 0,
                                                                           'ketidakhadiran' : { 'beralasan' : 0,
                                                                                                'tidak_beralasan' : 0,
                                                                                                'streak' : 0}
                                                                           })
            try:
                member = self.member_data[key]
                print(key, value, self.perizinan[key])
            except:
                pass
            try:
                if value >= 7:
                    kehadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['kehadiran']
                    db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'kehadiran': kehadiran + 1}})
                    hadir.append(key)
                elif self.perizinan[key] == 1:
                    ketidakhadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['beralasan']
                    db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.beralasan': ketidakhadiran + 1}})
                    tidak_hadir_beralasan.append(key)
                elif self.perizinan[key] == 2:
                    print(self.perizinan[key])
                    ketidakhadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['tidak_beralasan']
                    streak = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['streak']
                    if streak + 1 >= 3:
                        db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.streak': 0}})
                        await member.send('Maaf, Anda dikeluarkan dari server karena 3 kali ketidakhadiran dan atau tanpa alasan yang diterima')
                        await member.kick(reason='not attending meet for 3 times or declined reason for 3 times')
                    db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.tidak_beralasan': ketidakhadiran + 1}})
                    db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.streak': streak + 1}})
                    tidak_hadir_abai.append(key)
                elif member.status != 'offline' and self.perizinan[key] == 0:
                    print(member.status, self.perizinan[key])
                    ketidakhadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['tidak_beralasan']
                    streak = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['streak']
                    if streak + 1 >= 3:
                        db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.streak': 0}})
                        await member.send('Maaf, Anda dikeluarkan dari server karena 3 kali ketidakhadiran dan atau tanpa alasan yang diterima')
                        await member.kick(reason='not attending meet for 3 times or declined reason for 3 times')
                    db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.tidak_beralasan': ketidakhadiran + 1}})
                    db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.streak': streak + 1}})
                    tidak_hadir_abai.append(key)
                else:
                    ketidakhadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['tidak_beralasan']
                    db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.tidak_beralasan': ketidakhadiran + 1}})
                    tidak_hadir_tidak_beralasan.append(key)
            except:
                if value >= 5:
                    kehadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['kehadiran']
                    db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'kehadiran': kehadiran + 1}})
                    hadir.append(key)
                elif self.perizinan[key] == 1:
                    ketidakhadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['beralasan']
                    db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.beralasan': ketidakhadiran + 1}})
                    tidak_hadir_beralasan.append(key)
                elif self.perizinan[key] == 2:
                    print(self.perizinan[key])
                    ketidakhadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['tidak_beralasan']
                    streak = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['streak']
                    if streak + 1 >= 3:
                        db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.streak': 0}})
                        await member.send('Maaf, Anda dikeluarkan dari server karena 3 kali ketidakhadiran dan atau tanpa alasan yang diterima')
                        await member.kick(reason='not attending meet for 3 times or declined reason for 3 times')
                    db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.tidak_beralasan': ketidakhadiran + 1}})
                    db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.streak': streak + 1}})
                    tidak_hadir_abai.append(key)
                else:
                    ketidakhadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['tidak_beralasan']
                    db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.tidak_beralasan': ketidakhadiran + 1}})
                    tidak_hadir_tidak_beralasan.append(key)
                
        timestamp = str(datetime.datetime.now())
        db.servers_con['ramadan']['presensi'].insert_one({'date' : timestamp,
                                                          'peserta' : hadir if len(hadir) >= 1 else 'None',
                                                          'ketidakhadiran' : {
                                                                                'beralasan' : tidak_hadir_beralasan if len(tidak_hadir_beralasan) >= 1 else 'None',
                                                                                'tidak_beralasan' : tidak_hadir_tidak_beralasan if len(tidak_hadir_tidak_beralasan) >= 1 else 'None',
                                                                                'abai' : tidak_hadir_abai if len(tidak_hadir_abai) >= 1 else 'None'
                                                                                }
                                                          })
        print(hadir, tidak_hadir_beralasan, tidak_hadir_tidak_beralasan, tidak_hadir_abai)
        
        hadir_report = ', '.join([m.mention for m in [x for x in self.member_data.values() if x.id in hadir]])
        tidak_hadir_beralasan_report = ', '.join([m.mention for m in [x for x in self.member_data.values() if x.id in tidak_hadir_beralasan]])
        tidak_hadir_tidak_beralasan_report = ', '.join([m.mention for m in [x for x in self.member_data.values() if x.id in tidak_hadir_tidak_beralasan]])
        tidak_hadir_abai_report = ', '.join([m.mention for m in [x for x in self.member_data.values() if x.id in tidak_hadir_abai]])
        
        report = self.bot.get_channel(961632363996127364)
        embed = discord.Embed(title=f'[{timestamp}] GENERATED REPORT', timestamp=datetime.datetime.now())
        embed.add_field(name='Hadir', value=hadir_report, inline=False)
        embed.add_field(name='Tidak Hadir w/ reason', value=tidak_hadir_beralasan_report, inline=False)
        embed.add_field(name='Tidak Hadir w/o reason', value=tidak_hadir_tidak_beralasan_report, inline=False)
        embed.add_field(name='Tidak Hadir w/ self online status or declined reason', value=tidak_hadir_abai_report, inline=False)
        await report.send(embed = embed)
        
        self.data = {}
        self.channel_data = None
        self.perizinan = {}
        self.member_data = {}
        
        
        
    # @command(name='record.manual')
    # async def manual_records_presence(self, ctx):
    #     data = {915388147100176414: 90, 851354954392141859: 0, 757473573227987035: 90, 616950344747974656: 90, 599510213225218059: 0, 588495359094030336: 90, 465103196176777236: 90, 405311684903698443: 6, 342600543107284993: 84, 438230172437577729: 0, 462606134218588161: 0, 462825721916686337: 0, 486171419256815636: 0, 522307766421946372: 0, 529934718968528899: 63, 562472211005440011: 0, 627138670234828810: 0, 770341184458719252: 0, 794591789763133470: 0, 798938840252678145: 0, 888246772424650842: 0, 897317879341543494: 0}
    #     perizinan = {915388147100176414: 0, 851354954392141859: 0, 757473573227987035: 0, 616950344747974656: 0, 599510213225218059: 2, 588495359094030336: 0, 465103196176777236: 0, 405311684903698443: 0, 342600543107284993: 0, 438230172437577729: 1, 462606134218588161: 1, 462825721916686337: 1, 486171419256815636: 2, 522307766421946372: 1, 529934718968528899: 1, 562472211005440011: 1, 627138670234828810: 0, 770341184458719252: 0, 794591789763133470: 0, 798938840252678145: 0, 888246772424650842: 0, 897317879341543494: 0}
    #     member_data = dict(zip([x.id for x in ctx.guild.members if not x.bot], [x for x in ctx.guild.members if not x.bot]))
    #     hadir = []
    #     tidak_hadir_beralasan = []
    #     tidak_hadir_tidak_beralasan = []
    #     tidak_hadir_abai = []
    #     for key, value in data.items():
    #         if list(db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})) == []:
    #             db.servers_con['ramadan']['jumlah_kehadiran'].insert_one({'discord_id' : key,
    #                                                                        'kehadiran' : 0,
    #                                                                        'ketidakhadiran' : { 'beralasan' : 0,
    #                                                                                             'tidak_beralasan' : 0,
    #                                                                                             'streak' : 0}
    #                                                                        })
    #         try:
    #             member = member_data[key]
    #             print(key, value, perizinan[key])
    #         except:
    #             pass
    #         try:
    #             if value >= 5:
    #                 kehadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['kehadiran']
    #                 db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'kehadiran': kehadiran + 1}})
    #                 hadir.append(key)
    #             elif perizinan[key] == 1:
    #                 ketidakhadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['beralasan']
    #                 db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.beralasan': ketidakhadiran + 1}})
    #                 tidak_hadir_beralasan.append(key)
    #             elif perizinan[key] == 2:
    #                 print(perizinan[key])
    #                 ketidakhadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['tidak_beralasan']
    #                 streak = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['streak']
    #                 if streak + 1 >= 3:
    #                     db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.streak': 0}})
    #                     await member.send('Maaf, Anda dikeluarkan dari server karena ketidakhadiran 3 kali tanpa alasan yang diterima')
    #                     await member.kick(reason='unappealed reason for not attending daily tilawah more than 3 times while online.')
    #                 db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.tidak_beralasan': ketidakhadiran + 1}})
    #                 db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.streak': streak + 1}})
    #                 tidak_hadir_abai.append(key)
    #             # elif member.status != 'offline' and perizinan[key] == 0:
    #             #     print(member.status, perizinan[key])
    #             #     ketidakhadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['tidak_beralasan']
    #             #     streak = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['streak']
    #             #     if streak + 1 >= 3:
    #             #         db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.streak': 0}})
    #             #         await member.send('Maaf, Anda dikeluarkan dari server karena ketidakhadiran 3 kali tanpa alasan yang diterima')
    #             #         await member.kick(reason='unappealed reason for not attending daily tilawah more than 3 times while online.')
    #             #     db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.tidak_beralasan': ketidakhadiran + 1}})
    #             #     db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.streak': streak + 1}})
    #             #     tidak_hadir_abai.append(key)
    #             else:
    #                 ketidakhadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['tidak_beralasan']
    #                 db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.tidak_beralasan': ketidakhadiran + 1}})
    #                 tidak_hadir_tidak_beralasan.append(key)
    #         except:
    #             if value >= 7:
    #                 kehadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['kehadiran']
    #                 db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'kehadiran': kehadiran + 1}})
    #                 hadir.append(key)
    #             elif perizinan[key] == 1:
    #                 ketidakhadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['beralasan']
    #                 db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.beralasan': ketidakhadiran + 1}})
    #                 tidak_hadir_beralasan.append(key)
    #             elif perizinan[key] == 2:
    #                 print(perizinan[key])
    #                 ketidakhadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['tidak_beralasan']
    #                 streak = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['streak']
    #                 if streak + 1 >= 3:
    #                     db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.streak': 0}})
    #                     await member.send('Maaf, Anda dikeluarkan dari server karena ketidakhadiran 3 kali tanpa alasan yang diterima')
    #                     await member.kick(reason='unappealed reason for not attending daily tilawah more than 3 times while online.')
    #                 db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.tidak_beralasan': ketidakhadiran + 1}})
    #                 db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.streak': streak + 1}})
    #                 tidak_hadir_abai.append(key)
    #             else:
    #                 ketidakhadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['tidak_beralasan']
    #                 db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.tidak_beralasan': ketidakhadiran + 1}})
    #                 tidak_hadir_tidak_beralasan.append(key)
                
    #     timestamp = str(datetime.datetime.now())
    #     db.servers_con['ramadan']['presensi'].insert_one({'date' : timestamp,
    #                                                       'peserta' : hadir if len(hadir) >= 1 else 'None',
    #                                                       'ketidakhadiran' : {
    #                                                                             'beralasan' : tidak_hadir_beralasan if len(tidak_hadir_beralasan) >= 1 else 'None',
    #                                                                             'tidak_beralasan' : tidak_hadir_tidak_beralasan if len(tidak_hadir_tidak_beralasan) >= 1 else 'None',
    #                                                                             'abai' : tidak_hadir_abai if len(tidak_hadir_abai) >= 1 else 'None'
    #                                                                             }
    #                                                       })
    #     print(hadir, tidak_hadir_beralasan, tidak_hadir_tidak_beralasan, tidak_hadir_abai)
        
    #     hadir_report = ', '.join([m.mention for m in [x for x in member_data.values() if x.id in hadir]])
    #     tidak_hadir_beralasan_report = ', '.join([m.mention for m in [x for x in member_data.values() if x.id in tidak_hadir_beralasan]])
    #     tidak_hadir_tidak_beralasan_report = ', '.join([m.mention for m in [x for x in member_data.values() if x.id in tidak_hadir_tidak_beralasan]])
    #     tidak_hadir_abai_report = ', '.join([m.mention for m in [x for x in member_data.values() if x.id in tidak_hadir_abai]])
        
    #     report = self.bot.get_channel(961632363996127364)
    #     embed = discord.Embed(title=f'[{timestamp}] GENERATED REPORT', timestamp=datetime.datetime.now())
    #     embed.add_field(name='Hadir', value=hadir_report, inline=False)
    #     embed.add_field(name='Tidak Hadir w/ reason', value=tidak_hadir_beralasan_report, inline=False)
    #     embed.add_field(name='Tidak Hadir w/o reason', value=tidak_hadir_tidak_beralasan_report, inline=False)
    #     embed.add_field(name='Tidak Hadir w/ self online status or declined reason', value=tidak_hadir_abai_report, inline=False)
    #     await report.send(embed = embed)
        
def setup(bot):
    bot.add_cog(Ramadan(bot))