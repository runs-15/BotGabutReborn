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
        self.live_report = None
        self.count = 0
        
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
        self.perizinan = dict(zip([x.id for x in ctx.guild.members if not x.bot], [[0, 0] for i in range(len(ctx.guild.members) - len([x for x in ctx.guild.members if not x.bot]))]))
        msg = self.bot.get_channel(961632363996127364)
        self.live_report = await msg.send('live report')
        
        if ctx.author.id in [616950344747974656, 462825721916686337, 405311684903698443]:
            self.records_presence.start(ctx)
        await ctx.respond(f'**Urutan Membaca: **\n{str_orang}\n\nDimohon kepada:\n{str_not_joined} untuk segera bergabung ke channel {channel.mention}!\nBagi yang berhalangan hadir diharapkan untuk segera izin **sebelum sesi berakhir!**\n\nFormat perizinan: ```!izin <alasan> | contoh: \n!izin tadarus di masjid```')
        for member in not_join:
            try: 
                await member.send(f'dimohon untuk segera bergabung ke channel {channel.mention} atau **izin** terlebih dahulu.')
            except:
                pass
    
    @command(name='izin')
    async def izin(self, ctx, *alasan):
        self.alasan[ctx.author.id] = (ctx.message.id, ' '.join(alasan), 0)
        report = self.bot.get_channel(961632363996127364)
        await report.send(f'{ctx.author.mention} tidak bisa hadir karena {" ".join(alasan)}')
        
    @slash_command(name="accept", guild_ids=[960081979754283058])
    async def accept(self, ctx, message_id: Option(str, "message id", required=True), decider: Option(int, "accept or not", choices=[-1, 0, 1, 2])):
        if ctx.author.id == 616950344747974656:
            msg = await ctx.fetch_message(int(message_id))
            report = self.bot.get_channel(961632363996127364)
            if decider != -1:
                self.perizinan[msg.author.id][0] = decider
                await ctx.respond('accepted.' if decider == 1 else 'declined.', ephemeral = True)
                await report.send(f'reason for {msg.author.mention} was **accepted**.' if decider == 1 else f'reason for {msg.author.mention} was **declined**.')
                await msg.author.send('reason accepted.' if decider == 1 else 'reason declined.')
            else:
                member = msg.author
                await ctx.respond(f'{msg.author.mention} will be kicked.', ephemeral = True)
                await report.send(f'{msg.author.mention} akan ditendang karena alasan yang tidak bisa diterima')
                await member.send('Maaf, Anda telah dikeluarkan dari server karena alasan yang sama sekali tidak dapat diterima.')
                await member.kick(reason='severe unappealed reason.')
                
    @slash_command(name="late-accept", guild_ids=[960081979754283058])
    async def late_accept(self, ctx, message_id: Option(str, "message id", required=True), decider: Option(str, "cases", choices=['!hadir && status == online', '!hadir && status != online', 'decline'])):
        if ctx.author.id == 616950344747974656:
            msg = await ctx.fetch_message(int(message_id))
            report = self.bot.get_channel(961632363996127364)
            if decider == '!hadir && status == online':
                ketidakhadiran_alpha = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : msg.author.id})[0]['ketidakhadiran']['tidak_beralasan']
                streak = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : msg.author.id})[0]['ketidakhadiran']['streak']
                ketidakhadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : msg.author.id})[0]['ketidakhadiran']['beralasan']
                
                db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : msg.author.id}, {"$set": {'ketidakhadiran.tidak_beralasan': ketidakhadiran_alpha - 1}})
                db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : msg.author.id}, {"$set": {'ketidakhadiran.streak': streak - 1}})
                db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : msg.author.id}, {"$set": {'ketidakhadiran.beralasan': ketidakhadiran + 1}})
                    
                await ctx.respond('accepted.', ephemeral = True)
                await report.send(f'reason for {msg.author.mention} was **accepted**.')
                await msg.author.send('reason accepted.')
                
            elif decider == '!hadir && status != online':
                ketidakhadiran_alpha = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : msg.author.id})[0]['ketidakhadiran']['tidak_beralasan']
                ketidakhadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : msg.author.id})[0]['ketidakhadiran']['beralasan']
                
                db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : msg.author.id}, {"$set": {'ketidakhadiran.tidak_beralasan': ketidakhadiran_alpha - 1}})
                db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : msg.author.id}, {"$set": {'ketidakhadiran.beralasan': ketidakhadiran + 1}})
                    
                await ctx.respond('accepted.', ephemeral = True)
                await report.send(f'reason for {msg.author.mention} was **accepted**.')
                await msg.author.send('reason accepted.')
            else:
                await ctx.respond('declined.', ephemeral = True)
                await report.send(f'reason for {msg.author.mention} was **declined**.')
                await msg.author.send('reason declined.')
    
    @tasks.loop(seconds = 60, count = 60)
    async def records_presence(self, ctx):
        print('recording presence')
        if ctx.author.id in [616950344747974656, 462825721916686337, 405311684903698443]:
            self.member_data = dict(zip([x.id for x in ctx.guild.members if not x.bot], [x for x in ctx.guild.members if not x.bot]))
            for member in ctx.guild.members:
                if member.id not in self.perizinan.keys():
                    self.perizinan[member.id] = [0,0]
                if member.raw_status != 'offline':
                    self.perizinan[member.id][1] = 1
                if member in self.channel_data.members and member.id in self.data.keys():
                    self.data[member.id] += 1
                elif member in self.channel_data.members and member.id not in self.data.keys():
                    self.data[member.id] = 1
                elif member not in self.channel_data.members and member.id in self.data.keys():
                    continue
                else:
                    self.data[member.id] = 0
                    
            try:
                if self.count > 0:        
                    live_rep = 'discord_id          time    izin  online  name'
                              # 915388147100176xxx  12 min  0     1       runs
                    for x, y in self.data.items():
                        try:
                            live_rep += f'\n{x}  {y:<2} min  {self.perizinan[x][0]}     {self.perizinan[x][1]}       {self.member_data[x].name}'
                        except Exception as e:
                            print(e)
                    
                    await self.live_report.edit(embed=discord.Embed(title = datetime.datetime.now(), description = f'```live report:\n{live_rep}```\n\ndata:\n```{self.data}```\n\nperizinan:\n```{self.perizinan}```'))
            except Exception as e:
                print(e)
                
            self.count += 1

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
                elif self.perizinan[key][0] == 1:
                    ketidakhadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['beralasan']
                    db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.beralasan': ketidakhadiran + 1}})
                    tidak_hadir_beralasan.append(key)
                elif self.perizinan[key][0] == 2:
                    print(self.perizinan[key])
                    ketidakhadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['tidak_beralasan']
                    streak = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['streak']
                    if streak + 1 >= 3:
                        report = self.bot.get_channel(961632363996127364)
                        db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.streak': streak + 1}})
                        await report.send(f'{member.mention} has been **kicked** from the server.')
                        await member.send('Maaf, Anda dikeluarkan dari server karena 3 kali ketidakhadiran dan atau tanpa alasan yang diterima')
                        await member.kick(reason='not attending meet for 3 times or declined reason for 3 times')
                    db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.tidak_beralasan': ketidakhadiran + 1}})
                    db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.streak': streak + 1}})
                    tidak_hadir_abai.append(key)
                elif self.perizinan[key][1] == 1 and self.perizinan[key][0] == 0:
                    print(member.raw_status, self.perizinan[key])
                    ketidakhadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['tidak_beralasan']
                    streak = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['streak']
                    if streak + 1 >= 3:
                        report = self.bot.get_channel(961632363996127364)
                        db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.streak': streak + 1}})
                        await report.send(f'{member.mention} has been **kicked** from the server.')
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
                if value >= 7:
                    kehadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['kehadiran']
                    db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'kehadiran': kehadiran + 1}})
                    hadir.append(key)
                elif self.perizinan[key][0] == 1:
                    ketidakhadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['beralasan']
                    db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.beralasan': ketidakhadiran + 1}})
                    tidak_hadir_beralasan.append(key)
                elif self.perizinan[key][0] == 2:
                    print(self.perizinan[key])
                    ketidakhadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['tidak_beralasan']
                    streak = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['streak']
                    if streak + 1 >= 3:
                        report = self.bot.get_channel(961632363996127364)
                        db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.streak': streak + 1}})
                        await report.send(f'{member.mention} has been **kicked** from the server.')
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
        embed.add_field(name='Hadir', value=hadir_report if hadir_report != '' else 'none', inline=False)
        embed.add_field(name='Tidak Hadir w/ accepted reason', value=tidak_hadir_beralasan_report if tidak_hadir_beralasan_report != '' else 'none', inline=False)
        embed.add_field(name='Tidak Hadir w/o reason but offline state', value=tidak_hadir_tidak_beralasan_report if tidak_hadir_tidak_beralasan_report != '' else 'none', inline=False)
        embed.add_field(name='Tidak Hadir w/o reason while discord status == online or declined reason', value=tidak_hadir_abai_report if tidak_hadir_abai_report != '' else 'none', inline=False)
        await report.send(embed = embed)
        
        self.data = {}
        self.channel_data = None
        self.perizinan = {}
        self.member_data = {}
        
    @command(name='records.backup')
    async def backup_records(self, ctx):
        if ctx.author.id == 616950344747974656:
            await ctx.send(embed=discord.Embed(title = 'records backup', description = f'data:\n```{self.data}```\n\nchannel data:\n```{self.channel_data}```\n\nperizinan:\n```{self.perizinan}```\n\nalasan:\n```{self.alasan}```'))
            
    @command(name='records.presensi')
    async def presensi_records(self, ctx):
        if ctx.author.id == 616950344747974656:
            final = 'discord_id          h  i  a  pelanggaran berat'
            records = db.servers_con['ramadan']['jumlah_kehadiran'].find()
            for record in records:
                final += f"\n{record['discord_id']}  {record['kehadiran']}  {record['ketidakhadiran']['beralasan']}  {record['ketidakhadiran']['tidak_beralasan']}  {record['ketidakhadiran']['streak']} (toleransi : {3 - record['ketidakhadiran']['streak']})"
            await ctx.send(embed=discord.Embed(title = 'rekap presensi', description = f'```{final}```'))
            
    @command(name='records.execute')
    async def execute_records(self, ctx, data, izin):
        await ctx.send('executing...')
        data = eval(data)
        perizinan = eval(izin)
        member_data = dict(zip([x.id for x in ctx.guild.members if not x.bot], [x for x in ctx.guild.members if not x.bot]))
        hadir = []
        tidak_hadir_beralasan = []
        tidak_hadir_tidak_beralasan = []
        tidak_hadir_abai = []
        for key, value in data.items():
            if list(db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})) == []:
                db.servers_con['ramadan']['jumlah_kehadiran'].insert_one({'discord_id' : key,
                                                                           'kehadiran' : 0,
                                                                           'ketidakhadiran' : { 'beralasan' : 0,
                                                                                                'tidak_beralasan' : 0,
                                                                                                'streak' : 0}
                                                                           })
            try:
                member = member_data[key]
                print(key, value, perizinan[key])
            except:
                pass
            try:
                if value >= 7:
                    kehadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['kehadiran']
                    db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'kehadiran': kehadiran + 1}})
                    hadir.append(key)
                elif perizinan[key][0] == 1:
                    ketidakhadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['beralasan']
                    db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.beralasan': ketidakhadiran + 1}})
                    tidak_hadir_beralasan.append(key)
                elif perizinan[key][0] == 2:
                    print(perizinan[key])
                    ketidakhadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['tidak_beralasan']
                    streak = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['streak']
                    if streak + 1 >= 3:
                        report = self.bot.get_channel(961632363996127364)
                        db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.streak': streak + 1}})
                        await report.send(f'{member.mention} has been **kicked** from the server.')
                        await member.send('Maaf, Anda dikeluarkan dari server karena 3 kali ketidakhadiran dan atau tanpa alasan yang diterima')
                        await member.kick(reason='not attending meet for 3 times or declined reason for 3 times')
                    db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.tidak_beralasan': ketidakhadiran + 1}})
                    db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.streak': streak + 1}})
                    tidak_hadir_abai.append(key)
                elif perizinan[key][1] == 1 and perizinan[key][0] == 0:
                    print(member.raw_status, perizinan[key])
                    ketidakhadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['tidak_beralasan']
                    streak = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['streak']
                    if streak + 1 >= 3:
                        report = self.bot.get_channel(961632363996127364)
                        db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.streak': streak + 1}})
                        await report.send(f'{member.mention} has been **kicked** from the server.')
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
                if value >= 7:
                    kehadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['kehadiran']
                    db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'kehadiran': kehadiran + 1}})
                    hadir.append(key)
                elif perizinan[key][0] == 1:
                    ketidakhadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['beralasan']
                    db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.beralasan': ketidakhadiran + 1}})
                    tidak_hadir_beralasan.append(key)
                elif perizinan[key][0] == 2:
                    print(perizinan[key])
                    ketidakhadiran = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['tidak_beralasan']
                    streak = db.servers_con['ramadan']['jumlah_kehadiran'].find({'discord_id' : key})[0]['ketidakhadiran']['streak']
                    if streak + 1 >= 3:
                        report = self.bot.get_channel(961632363996127364)
                        db.servers_con['ramadan']['jumlah_kehadiran'].update_one({'discord_id' : key}, {"$set": {'ketidakhadiran.streak': streak + 1}})
                        await report.send(f'{member.mention} has been **kicked** from the server.')
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
        
        hadir_report = ', '.join([m.mention for m in [x for x in member_data.values() if x.id in hadir]])
        tidak_hadir_beralasan_report = ', '.join([m.mention for m in [x for x in member_data.values() if x.id in tidak_hadir_beralasan]])
        tidak_hadir_tidak_beralasan_report = ', '.join([m.mention for m in [x for x in member_data.values() if x.id in tidak_hadir_tidak_beralasan]])
        tidak_hadir_abai_report = ', '.join([m.mention for m in [x for x in member_data.values() if x.id in tidak_hadir_abai]])
        
        report = self.bot.get_channel(961632363996127364)
        embed = discord.Embed(title=f'[{timestamp}] GENERATED REPORT', timestamp=datetime.datetime.now())
        embed.add_field(name='Hadir', value=hadir_report if hadir_report != '' else 'none', inline=False)
        embed.add_field(name='Tidak Hadir w/ accepted reason', value=tidak_hadir_beralasan_report if tidak_hadir_beralasan_report != '' else 'none', inline=False)
        embed.add_field(name='Tidak Hadir w/o reason but offline state', value=tidak_hadir_tidak_beralasan_report if tidak_hadir_tidak_beralasan_report != '' else 'none', inline=False)
        embed.add_field(name='Tidak Hadir w/o reason while discord status == online or declined reason', value=tidak_hadir_abai_report if tidak_hadir_abai_report != '' else 'none', inline=False)
        await report.send(embed = embed)
        
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
    #             # elif member.raw_status != 'offline' and perizinan[key] == 0:
    #             #     print(member.raw_status, perizinan[key])
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
    #     embed.add_field(name='Hadir', value=hadir_report if hadir_report != '' else 'none', inline=False)
    #     embed.add_field(name='Tidak Hadir w/ accepted reason', value=tidak_hadir_beralasan_report if tidak_hadir_beralasan_report != '' else 'none', inline=False)
    #     embed.add_field(name='Tidak Hadir w/o reason but offline state', value=tidak_hadir_tidak_beralasan_report if tidak_hadir_tidak_beralasan_report != '' else 'none', inline=False)
    #     embed.add_field(name='Tidak Hadir w/o reason while discord status == online or declined reason', value=tidak_hadir_abai_report if tidak_hadir_abai_report != '' else 'none', inline=False)
    #     await report.send(embed = embed)
        
def setup(bot):
    bot.add_cog(Ramadan(bot))