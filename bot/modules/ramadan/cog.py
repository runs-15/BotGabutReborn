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
        await ctx.respond(f'**Urutan Membaca: **\n{str_orang}\n\nDimohon kepada:\n{str_not_joined} untuk segera bergabung ke channel {channel.mention}!\nBagi yang berhalangan hadir diharapkan untuk segera izin **sebelum sesi berakhir!**\n\nFormat perizinan: ```!izin <alasan> \ncontoh: !izin tadarus di masjid```')
    
    @command(name='izin')
    async def izin(self, ctx, *alasan):
        self.perizinan[ctx.author.id] = (ctx.message.id, ' '.join(alasan))
        user = self.bot.get_user(616950344747974656)
        await user.send(ctx.author.mention, f'tidak bisa hadir karena {" ".join(alasan)}')
        
    @slash_command(name="accept", guild_ids=[960081979754283058])
    async def accept(self, ctx, message_id: Option(int, "message id", required=True), decider: Option(int, "accept or not", choices=[0, 1, 2])):
        if ctx.author.id == 616950344747974656:
            if decider != 2:
                msg = await ctx.fetch_message(message_id)
                self.perizinan[msg.author.id] = decider
                await ctx.respond('appealed' if decider == 1 else 'unappealed', ephemeral = True)
            else:
                member = msg.author
                await ctx.respond(f'{msg.author.mention} will be kicked.', ephemeral = True)
                await member.send('Maaf, Anda dikeluarkan dari server karena alasan yang tidak dapat diterima.')
                await member.kick(reason='severe unappealed reason.')
    
    @tasks.loop(seconds = 60, count = 90)
    async def records_presence(self, ctx):
        print('recording presence', ctx.author.id)
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
            member = self.member_data[key]
            print(key, value, self.perizinan[key])
            try:
                if value >= 15:
                    kehadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['kehadiran']
                    db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'kehadiran': kehadiran + 1}})
                    hadir.append(key)
                elif self.perizinan[key] == 1:
                    ketidakhadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['beralasan']
                    db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.beralasan': ketidakhadiran + 1}})
                    tidak_hadir_beralasan.append(key)
                elif self.perizinan[key] == 0:
                    print(self.perizinan[key])
                    ketidakhadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['tidak_beralasan']
                    streak = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['streak']
                    if streak + 1 >= 3:
                        db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.streak': 0}})
                        await member.send('Maaf, Anda dikeluarkan dari server karena ketidakhadiran 3 kali tanpa alasan yang diterima')
                        await member.kick(reason='unappealed reason for not attending daily tilawah more than 3 times while online.')
                    db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.tidak_beralasan': ketidakhadiran + 1}})
                    db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.streak': streak + 1}})
                    tidak_hadir_abai.append(key)
                elif member.status != 'offline' and self.perizinan[key] == 0:
                    print(member.status, self.perizinan[key])
                    ketidakhadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['tidak_beralasan']
                    streak = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['streak']
                    if streak + 1 >= 3:
                        db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.streak': 0}})
                        await member.send('Maaf, Anda dikeluarkan dari server karena ketidakhadiran 3 kali tanpa alasan yang diterima')
                        await member.kick(reason='unappealed reason for not attending daily tilawah more than 3 times while online.')
                    db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.tidak_beralasan': ketidakhadiran + 1}})
                    db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.streak': streak + 1}})
                    tidak_hadir_abai.append(key)
                else:
                    ketidakhadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['tidak_beralasan']
                    db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.tidak_beralasan': ketidakhadiran + 1}})
                    tidak_hadir_tidak_beralasan.append(key)
            except:
                if value >= 15:
                    kehadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['kehadiran']
                    db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'kehadiran': kehadiran + 1}})
                    hadir.append(key)
                elif self.perizinan[key] == 1:
                    ketidakhadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['beralasan']
                    db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.beralasan': ketidakhadiran + 1}})
                    tidak_hadir_beralasan.append(key)
                elif self.perizinan[key] == 0:
                    print(self.perizinan[key])
                    ketidakhadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['tidak_beralasan']
                    streak = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['streak']
                    if streak + 1 >= 3:
                        db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.streak': 0}})
                        await member.send('Maaf, Anda dikeluarkan dari server karena ketidakhadiran 3 kali tanpa alasan yang diterima')
                        await member.kick(reason='unappealed reason for not attending daily tilawah more than 3 times while online.')
                    db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.tidak_beralasan': ketidakhadiran + 1}})
                    db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.streak': streak + 1}})
                    tidak_hadir_abai.append(key)
                else:
                    ketidakhadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['tidak_beralasan']
                    db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.tidak_beralasan': ketidakhadiran + 1}})
                    tidak_hadir_tidak_beralasan.append(key)
                
        db.servers_con['ramadan']['presensi'].insert_one({'date' : str(datetime.datetime.now()),
                                                          'peserta' : hadir if len(hadir) >= 1 else 'None',
                                                          'ketidakhadiran' : {
                                                                                'beralasan' : tidak_hadir_beralasan if len(tidak_hadir_beralasan) >= 1 else 'None',
                                                                                'tidak_beralasan' : tidak_hadir_tidak_beralasan if len(tidak_hadir_tidak_beralasan) >= 1 else 'None',
                                                                                'abai' : tidak_hadir_abai if len(tidak_hadir_abai) >= 1 else 'None'
                                                                                }
                                                          })
        print(hadir, tidak_hadir_beralasan, tidak_hadir_tidak_beralasan, tidak_hadir_abai)
        self.data = {}
        self.channel_data = None
        self.perizinan = {}
        self.member_data = {}
                
        
def setup(bot):
    bot.add_cog(Ramadan(bot))