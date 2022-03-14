from ast import Raise
import discord, time, math, db, traceback
import pandas as pd
from asyncio import sleep
from discord.ext import tasks
from discord.ext.commands import Cog, command, slash_command, cooldown, BucketType
from discord import Embed, Status, File
from datetime import datetime
from PIL import Image, ImageDraw
from discord.utils import get
import numpy as np

class Exp(Cog):
    """Module yang mengatur terkait voice atau chat levelling serta violence control
    """
    def __init__(self, bot):
        self.bot = bot
        self.user = {}
        self.exp = {}

    @Cog.listener()
    async def on_ready(self):
        self.voice_data = []
        self.text_data = []
        self.levelling_channel = self.bot.get_channel(855810493397729300)
        self.text_levelling_channel = self.bot.get_channel(856069554387943427)
        self.temp_join = 0
        if not self.voice_update.is_running():
            self.voice_update.start()
        if not self.voice_submit.is_running():  
            self.voice_submit.start()
        # self.online_counter.start()
        # self.voice_check_update.start()
        # self.reset_vc_user.start()
        
    def factor(self, level):
        return int(60 * level + ((level ** 3.8) * (1 - (0.99 ** level))))
    
    def cur_exp(self, xp):
        level = 0
        exp = xp
        while exp > self.factor(level):
            level += 1
            exp -= self.factor(level)
        return int(exp)

    def number_format(self, num):
        num = float('{:.3g}'.format(num))
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
        return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T', 'P'][magnitude])
            
    @tasks.loop(seconds=15)   
    async def voice_update(self):
        checker = []
        guild = self.bot.get_guild(836835374696628244)
        channel_object = [c for c in guild.channels if c.type==discord.ChannelType.voice and c != guild.afk_channel]
        for channel in channel_object:
            checker.append(channel.members)
            members = channel.members
            if len(members) == 1:
                for member in members:
                    del self.user[member.id]
            else:
                for member in members:
                    if member.id not in self.user and not member.bot:
                        self.user[member.id] = {}
                        self.user[member.id]["time"] = int(time.time())
                        self.user[member.id]["channel"] = channel.id
        if len(checker) == 0:
            self.user = {}
        if len(self.user) != 0 and len(self.user) != self.temp_join:
            print(f"\tVoice updated with {self.temp_join} people!")
        self.temp_join = len(self.user)

    @tasks.loop(seconds=60)
    async def voice_submit(self):
        for i in self.user:
            try:
                total_time = int(time.time()) - self.user[i]["time"]
                if db.servers_con['servers']['social_credit'].find({'discord_id' : i}) != None:
                    voice_time = db.servers_con['servers']['social_credit'].find({'discord_id' : i})[0]['v_time'] + total_time
                    current_level = db.servers_con['servers']['social_credit'].find({'discord_id' : i})[0]['v_level']
                    db.servers_con['servers']['social_credit'].update_one({'discord_id' : i}, {"$set": {'v_time': voice_time}})
                else:
                    current_level = 0
                    db.servers_con['servers']['social_credit'].insert_one({'discord_id' : i,
                                                                           'v_exp'      : 0, 
                                                                           'v_time'     : 0,
                                                                           'v_level'    : 0,
                                                                           't_exp'      : 0,
                                                                           't_time'     : 0,
                                                                           't_level'    : 0,
                                                                           'v_violation': 0,
                                                                           't_violation': 0,
                                                                           'n_violation': 0})

                level = 0
                temp = voice_time
                while temp > self.factor(level):
                    level += 1
                    temp -= (self.factor(level + 1) - self.factor(level))
                    
                if current_level < level:
                    db.servers_con['servers']['social_credit'].update_one({'discord_id' : i}, {"$set": {'v_level': level}})
                
                    # res = 0
                    # for j in range(level + 1):
                    #     res += self.factor(j)
                    
                    # db.servers_con['servers']['social_credit'].update_one({'discord_id' : i}, {"$set": {'v_exp': res + voice_time}})
                    
                    # await self.levelling_channel.send(f"Selamat <@{i}>! Anda telah mencapai level **`{level}`** dalam *voice chat*!")
                    print(f"Selamat <@{i}>! Anda telah mencapai level **`{level}`** dalam *voice chat*!")
                    
                elif level < current_level:
                    db.servers_con['servers']['social_credit'].update_one({'discord_id' : i}, {"$set": {'v_level': level}})
                    
                    # res = 0
                    # for j in range(level + 1):
                    #     res += self.factor(j)
                    
                    # db.servers_con['servers']['social_credit'].update_one({'discord_id' : i}, {"$set": {'v_exp': res + voice_time}})
                    
                    # await self.levelling_channel.send(f"Selamat <@{i}>! Anda telah diturunkan ke level **`{level}`** dalam *voice chat*!")
                    print(f"Selamat <@{i}>! Anda telah diturunkan ke level **`{level}`** dalam *voice chat*!")
                
                # for j in range(current_level, 9999):
                #     pembanding_bawah = 60*(j-1) + (((j-1) ** 3.8) * (1 - (0.99 ** (j-1))))
                #     level            = 60*(j+0) + (((j+0) ** 3.8) * (1 - (0.99 ** (j+0))))
                #     pembanding_atas  = 60*(j+1) + (((j+1) ** 3.8) * (1 - (0.99 ** (j+1))))
                #     if level > voice_time >= pembanding_bawah:
                #         continue
                #     elif level <= voice_time < pembanding_atas:
                #         if current_level != j:
                #             sum_of_exp = int(sum([60*(x+0) + (((x+0) ** 3.8) * (1 - (0.99 ** (x+0)))) for x in range(1, j + 1)]))
                #             if j >= 10:
                #                 await self.levelling_channel.send(f"Selamat <@{i}>! Anda telah mencapai level **`{j}`** dalam *voice chat*!")
                #             db.servers_con['servers']['social_credit'].update_one({'discord_id' : i}, {"$set": {'v_exp': sum_of_exp}})
                #             db.servers_con['servers']['social_credit'].update_one({'discord_id' : i}, {"$set": {'v_level': j}})
                #             break
                #         else:
                #             break
                #     else:
                #         continue
                
                self.user[i]["time"] = int(time.time())
            except Exception:
                print(traceback.format_exc())

    @command(name="user.initialize", hidden = True)
    async def reset_user(self, ctx):
        if ctx.author.id == 616950344747974656:
            for member in [m for m in ctx.guild.members if not m.bot]:
                db.servers_con['servers']['social_credit'].insert_one({ 'discord_id' : member.id,
                                                                        'v_exp'      : 0, 
                                                                        'v_time'     : 0,
                                                                        'v_level'    : 0,
                                                                        't_exp'      : 0,
                                                                        't_time'     : 0,
                                                                        't_level'    : 0,
                                                                        'v_violation': 0,
                                                                        't_violation': 0,
                                                                        'n_violation': 0})
            await ctx.send("Command Executed!")

    @command(name="vc.reset")
    async def reset_vc(self, ctx):
        if ctx.author.id == 616950344747974656:
            self.user = []

    # async def masa_hukuman(self, user : discord.Member, role : discord.Role, role2 : discord.Role, hukuman):
    #     print(user, role, role2, hukuman)
    #     await user.remove_roles(role)
    #     await user.add_roles(role2)
    #     await sleep(hukuman)
    #     await user.add_roles(role)
    #     await user.remove_roles(role2)
    #     await user.edit(nick=f"{user.name}")
    
    # def round_half_up(self, n, decimals=0):
    #     multiplier = 10 ** decimals
    #     return math.floor(n*multiplier + 0.5) / multiplier

    # @cog_ext.cog_slash(name="profanity", description="turn on or off", options=[create_option(name="switch",description="ON or OFF",option_type=3,required=True,choices=[
    #                         create_choice(
    #                             name="ON",
    #                             value="1"
    #                         ),
    #                         create_choice(
    #                             name="OFF",
    #                             value="0"
    #                         )])], guild_ids=[x[0] for x in db.records("SELECT GuildID FROM guilds")])
    # async def profanity_switcher(self, ctx : SlashContext, switch):
    #     if ctx.author.id == 616950344747974656:
    #         if switch == "1":
    #             self.profanity_status = 1
    #             embed = Embed(title="Profanity Filter is ON!")
    #             await ctx.send(embed=embed)
    #         else:
    #             self.profanity_status = 0
    #             embed = Embed(title="Profanity Filter is OFF!")
    #             await ctx.send(embed=embed)
    #     else:
    #         embed = Embed(title="🤪")
    #         await ctx.send(embed=embed)

    # @commands.Cog.listener()
    # async def on_guild_join(self, guild):
    #     db.execute("INSERT OR REPLACE INTO guilds VALUES (?, ?)", guild.id, ">>")

    # @tasks.loop(seconds=15)
    # async def voice_check_update(self):
    #     db.execute("DELETE FROM userDetails WHERE pelanggaran_name IS NULL")
    #     await self.voice_update()

    # @tasks.loop(seconds=300)
    # async def reset_vc_user(self):
    #     self.user = []
    
    # @tasks.loop(seconds=30)
    # async def online_counter(self):
    #     server = self.bot.get_guild(836835374696628244)
    #     count_online = self.bot.get_channel(854957153055146004)
    #     await count_online.edit(name=f"⌘「🟢」》Online : {sum(member.status!=Status.offline and not member.bot for member in server.members)}")
    #     count_all = self.bot.get_channel(854517820112896001)
    #     count_bot = self.bot.get_channel(854517801937797130)
    #     count_member = self.bot.get_channel(854517752734416926)
    #     await count_all.edit(name=f"⌘「👤」》Total : {len(server.members)}")
    #     await count_bot.edit(name=f"⌘「🤖」》Bots : {len([m for m in server.members if m.bot])}")
    #     await count_member.edit(name=f"⌘「🧐」》Devs : {len([m for m in server.members if not m.bot])}")

    # @commands.Cog.listener()
    # async def on_member_join(self, member):
    #     if member.guild.id == 836835374696628244:
    #         db.execute("INSERT INTO userDetails VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", member.id, 0, 0, 0, 0, 0, 0, 0, 0)
    #         clear_roleN = discord.utils.get(member.guild.roles, name="Clear(N)")
    #         clear_roleT = discord.utils.get(member.guild.roles, name="Clear(T)") 
    #         clear_roleV = discord.utils.get(member.guild.roles, name="Clear(V)") 
    #         await member.add_roles(clear_roleN)
    #         await member.add_roles(clear_roleT)
    #         await member.add_roles(clear_roleV)
    #         count_all = self.bot.get_channel(854517820112896001)
    #         count_bot = self.bot.get_channel(854517801937797130)
    #         count_member = self.bot.get_channel(854517752734416926)
    #         await count_all.edit(name=f"⌘「👤」》Total : {len(member.guild.members)}")
    #         await count_bot.edit(name=f"⌘「🤖」》Bots : {len([m for m in member.guild.members if m.bot])}")
    #         await count_member.edit(name=f"⌘「🧐」》Devs : {len([m for m in member.guild.members if not m.bot])}")
    #         welcome_channel = self.bot.get_channel(852854935175168000)
    #         await welcome_channel.send(f"Haloo {member.mention}👋! Selamat datang di server **`Developer Gabut`**, feel free and enjoy your day!")

    # @commands.Cog.listener()
    # async def on_member_remove(self, member):
    #     if member.guild.id == 836835374696628244:
    #         count_all = self.bot.get_channel(854517820112896001)
    #         count_bot = self.bot.get_channel(854517801937797130)
    #         count_member = self.bot.get_channel(854517752734416926)
    #         await count_all.edit(name=f"⌘「👤」》Total : {len(member.guild.members)}")
    #         await count_bot.edit(name=f"⌘「🤖」》Bots : {len([m for m in member.guild.members if m.bot])}")
    #         await count_member.edit(name=f"⌘「🧐」》Devs : {len([m for m in member.guild.members if not m.bot])}")
    #         await self.log_channel.send(f"{member.name}#{member.discriminator} meninggalkan server")

    # @commands.Cog.listener()
    # async def on_user_update(self, before, after):
    #     if before.avatar_url != after.avatar_url:
    #         user = await self.bot.fetch_user(before.id)
    #         embed = Embed(title="Member Update", description=f"Avatar Change ({user.display_name} {before.id})", colour=after.colour, timestamp=datetime.utcnow())
    #         embed.set_author(name=f'{before.name}#{before.discriminator}', icon_url=after.avatar_url)
    #         embed.set_thumbnail(url=before.avatar_url)
    #         embed.set_image(url=after.avatar_url)
    #         await self.log_channel.send(embed=embed)

    # @commands.Cog.listener()
    # async def on_member_update(self, before, after):
    #     if before.display_name != after.display_name:
    #         embed = Embed(title="Member Update", description="Nickname Change", colour=after.colour, timestamp=datetime.utcnow())
    #         # check profanity
    #         if after.guild.id == 836835374696628244 and self.profanity_status == 1:
    #             tanpa_pemotongan = []
    #             dipotong = []
    #             for i in after.display_name.lower().split():
    #                 dipotong.append("".join(dict.fromkeys(i)))
    #                 tanpa_pemotongan.append(i)
    #             for kotor in self.profanity:
    #                 if (kotor.lower() in tanpa_pemotongan) or (kotor.lower() in dipotong):
    #                     if db.field("SELECT pelanggaran_name from userDetails WHERE userID = ?", after.id) != None:
    #                         jumlah = db.field("SELECT pelanggaran_name from userDetails WHERE userID = ?", after.id) + 1
    #                         db.execute("UPDATE userDetails SET pelanggaran_name = ? WHERE userID = ?", jumlah, after.id)
    #                     else:
    #                         if db.field("SELECT userID from userDetails WHERE userID = ?", after.id) != None:
    #                             db.execute("INSERT INTO userDetails (pelanggaran_name) VALUES (?)", 1)
    #                             jumlah = db.field("SELECT pelanggaran_name from userDetails WHERE userID = ?", after.id)
    #                         else:
    #                             db.execute("INSERT INTO userDetails VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", after.id, 1, 0, 0, 0, 0, 0, 0, 0)
    #                             jumlah = db.field("SELECT pelanggaran_name from userDetails WHERE userID = ?", after.id)
    #                     embed.add_field(name="Peringatan", value=f"**Profanity Detected!**\n{after.display_name} ({kotor})", inline=False)
    #                     sedang_dihukum = discord.utils.get(after.guild.roles, name="Sedang Dihukum")
    #                     clarity = discord.utils.get(after.guild.roles, name="Clear(N)")
    #                     hukuman = 60 + ((jumlah ** 3) * (1 - (0.99 ** jumlah)))

    #                     hari = math.floor(hukuman / (60 * 60 * 24))
    #                     jam = math.floor((hukuman % (60 * 60 * 24)) / (60 * 60))
    #                     menit = math.floor((hukuman % (60 * 60)) / 60)
    #                     detik = math.floor(hukuman % (60))

    #                     msg = await self.profanity_channel.send(f"**Peringatan!**\n{after.name}#{after.discriminator} ({after.mention}) telah **terdeteksi** mengganti username yang **tidak pantas** dan akan dihukum sementara!\nMasa berlaku hukuman: ||{str(hari) + ' hari ' if hari != 0 else ''}{str(jam) + ' jam ' if jam != 0 else ''}{str(menit) + ' menit ' if menit != 0 else ''}{str(detik) + ' detik ' if detik != 0 else ''}||.")
    #                     await after.edit(nick=f"Inappropriate Name ({jumlah})x!")

    #                     await self.masa_hukuman(after, clarity, sedang_dihukum, hukuman)
    #                     await msg.delete()
    #                     break
    #                 else:
    #                     pass
    #         embed.set_author(name=f'{before.name}#{before.discriminator}', icon_url=before.avatar_url)
    #         embed.add_field(name="Sebelum:", value=before.display_name, inline=False)
    #         embed.add_field(name="Saat ini:", value=after.display_name, inline=False)
    #         embed.add_field(name="User ID:", value=before.id, inline=False)
    #         await self.log_channel.send(embed=embed)

    # @commands.Cog.listener()
    # async def on_message_edit(self, before, after):
    #     if not after.author.bot:
    #         editembed = Embed(
    #             title="Message Edit!",
    #             timestamp=after.created_at,
    #             description = f"<@!{before.author.id}> telah mengubah pesan di <#{before.channel.id}>.",
    #             colour = after.author.colour
    #             ) 
    #         editembed.set_author(name=f'{before.author.name}#{before.author.discriminator}', icon_url=before.author.avatar_url)
    #         editembed.set_footer(text=f"• Author ID:{before.author.id}\n• Message ID: {before.id}\n ")
    #         editembed.add_field(name='Sebelum:', value=before.content, inline=False)
    #         editembed.add_field(name="Saat ini:", value=after.content, inline=False)
    #         await self.log_channel.send(embed=editembed)

    # @commands.Cog.listener()
    # async def on_message_delete(self, message):
    #     if not message.author.bot:
    #         editembed = Embed(
    #                 title="Message Deletion!",
    #                 timestamp=message.created_at,
    #                 description = f"<@!{message.author.id}> telah menghapus pesan di <#{message.channel.id}>.",
    #                 colour = message.author.colour
    #                 ) 
    #         editembed.set_author(name=f'{message.author.name}#{message.author.discriminator}', icon_url=message.author.avatar_url)
    #         editembed.set_footer(text=f"• Author ID:{message.author.id}\n• Message ID: {message.id}\n ")
    #         editembed.add_field(name='Pesan yang dihapus:', value=message.content, inline=False)
    #         await self.log_channel.send(embed=editembed)

    @Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        try:
            if member.guild.id == 836835374696628244 and not member.bot:
                if before.channel == None and after.channel != None and after.afk != True:
                    self.user[member.id] = {}
                    self.user[member.id]["time"] = int(time.time())
                    self.user[member.id]["channel"] = after.channel.id
                if after.channel == None and before.channel != None:
                    await self.voice_submit()
                    del self.user[member.id]
            if after.afk == True and member.id in self.user:
                del self.user[member.id]
        except Exception as e:
            print(e)

    # @Cog.listener("on_message")
    # async def message_xp(self, message):
    #     if message.author != self.bot.user and len(message.content) > 2 and message.guild.id == 836835374696628244:
    #         db.execute("UPDATE userDetails SET total_chat = ? WHERE userID = ?", (db.field("SELECT total_chat from userDetails WHERE userID = ?", message.author.id) + 1) if db.field("SELECT total_chat from userDetails WHERE userID = ?", message.author.id) != None else 1, message.author.id)
    #         if self.profanity_status == 1:
    #             tanpa_pemotongan = []
    #             dipotong = []
    #             for i in message.content.lower().split():
    #                 dipotong.append("".join(dict.fromkeys(i)))
    #                 tanpa_pemotongan.append(i)
    #             for kotor in self.profanity:
    #                 if (kotor.lower() in tanpa_pemotongan) or (kotor.lower() in dipotong):
    #                     await message.delete()
    #                     jumlah = db.field("SELECT pelanggaran_text from userDetails WHERE userID = ?", message.author.id) + 1
    #                     db.execute("UPDATE userDetails SET pelanggaran_text = ? WHERE userID = ?", jumlah, message.author.id)
    #                     db.execute("UPDATE userDetails SET experience_total = ? WHERE userID = ?", db.field("SELECT experience_total from userDetails WHERE userID = ?", message.author.id) - (10 * jumlah), message.author.id)
    #                     sedang_dihukum = discord.utils.get(message.guild.roles, name="Sedang Dihukum")
    #                     text_clarity = discord.utils.get(message.guild.roles, name="Clear(T)")
    #                     hukuman = 60 + ((jumlah ** 3) * (1 - (0.99 ** jumlah)))

    #                     hari = math.floor(hukuman / (60 * 60 * 24))
    #                     jam = math.floor((hukuman % (60 * 60 * 24)) / (60 * 60))
    #                     menit = math.floor((hukuman % (60 * 60)) / 60)
    #                     detik = math.floor(hukuman % (60))

    #                     msg = await message.channel.send(f"**Peringatan!**\n{message.author.name}#{message.author.discriminator} ({message.author.mention}) telah **terdeteksi** menulis kata yang **tidak pantas** (||{kotor.lower()}||) dan akan dihukum sementara!\nMasa berlaku hukuman: ||{str(hari) + ' hari ' if hari != 0 else ''}{str(jam) + ' jam ' if jam != 0 else ''}{str(menit) + ' menit ' if menit != 0 else ''}{str(detik) + ' detik ' if detik != 0 else ''} dan pengurangan exp sebanyak **`{jumlah*10}`**||.")
    #                     await message.author.edit(nick=f"Inappropriate Text ({jumlah})x!")

    #                     await self.masa_hukuman(message.author, text_clarity, sedang_dihukum, hukuman)
    #                     await msg.delete()
    #                     break
    #         xp_factor = 5
    #         if message.author.id not in [x[0] for x in self.exp]:
    #             self.exp.append([message.author.id, time.time()])
    #             print(self.exp)
    #         count = 0
    #         for i in self.exp:
    #             count += 1
    #             if message.author.id == i[0] and time.time() > i[1]:
    #                 current_xp = db.field("SELECT experience_total from userDetails WHERE userID = ?", message.author.id) + xp_factor
    #                 current_level = db.field("SELECT experience_level from userDetails WHERE userID = ?", message.author.id)
    #                 db.execute("UPDATE userDetails SET experience_total = ? WHERE userID = ?", current_xp, message.author.id)
    #                 print(current_xp, message.author.id)
    #                 self.exp[count-1][1] = time.time() + 20

    #                 for i in range(1, 101):
    #                     pembanding_bawah = 10*(i-1) + self.round_half_up(int(((i-1) ** 3.2) * (1 - (0.99 ** (i-1)))), -1)
    #                     level            = 10*(i+0) + self.round_half_up(int(((i+0) ** 3.2) * (1 - (0.99 ** (i+0)))), -1)
    #                     pembanding_atas  = 10*(i+1) + self.round_half_up(int(((i+1) ** 3.2) * (1 - (0.99 ** (i+1)))), -1)
    #                     if level > current_xp >= pembanding_bawah:
    #                         continue
    #                     elif level <= current_xp < pembanding_atas:
    #                         if current_level != i:
    #                             await self.text_levelling_channel.send(f"Selamat {message.author.mention}! Anda telah mencapai level **`{i}`** dalam *text chat!*")
    #                             db.execute("UPDATE userDetails SET experience_level = ? WHERE userID = ?", i, message.author.id)
    #                             print(level, current_xp, pembanding_atas)
    #                             break
    #                         else:
    #                             #await self.log_channel.send(f"{message.author.mention} memerlukan {int(level-current_xp)} detik untuk ke level {i+1}")
    #                             break
    #                     else:
    #                         continue
    
    def round_half_up(self, n, decimals=0):
        multiplier = 10 ** decimals
        return math.floor(n*multiplier + 0.5) / multiplier

    def drawProgressBar(self, d, x, y, w, h, progress, bg="white", fg="red"):
        # draw background
        #d.ellipse((x+w, y, x+h+w, y+h), fill=bg)
        #d.ellipse((x, y, x+h, y+h), fill=bg)
        #d.rectangle((x+(h/2), y, x+w+(h/2), y+h), fill=bg)
        d.rectangle((x, y+h, x+w+h, y), fill=bg)

        # draw progress bar
        w *= progress
        #d.ellipse((x+w, y, x+h+w, y+h),fill=fg)
        #d.ellipse((x, y, x+h, y+h),fill=fg)
        #d.rectangle((x+(h/2), y, x+w+(h/2), y+h),fill=fg)
        d.rectangle((x, y+h, x+w, y),fill=fg)

        return d
    
    @command(name="vc.leaderboard", aliases=["vc.rank"])
    async def vc_rank(self, ctx):
        daftar = db.servers_con['servers']['social_credit'].find()
        data = list(daftar)
        df = pd.DataFrame(data, index=[x['discord_id'] for x in data], columns=['discord_id', 'v_exp', 'v_time', 'v_level', 't_exp', 't_time', 't_level', 'v_violence', 't_violence', 'n_violence'])
        df = df.sort_values(['v_time', 'discord_id'], ascending=[False, True], ignore_index=True)
        
        cnt = 1
        embed = Embed(title=f"Voice Level Leaderboard", colour=ctx.author.colour)
        for index, row in df.iterrows():
            user = get(self.bot.get_all_members(), id=row['discord_id'])
            if cnt < 16:
                embed.add_field(name=f"Rank : {cnt}", value=f'{user.mention}\n> Level: **{int(row["v_level"])}**', inline=True)
                cnt += 1
        embed.set_thumbnail(url=ctx.guild.icon.url)
        await ctx.send(embed=embed)
        
    @command(name="vc.stats", aliases=["voice.stats"])
    @cooldown(1, 15, BucketType.user)
    async def vc_level(self, ctx, user : discord.Member = None):
        """
        > Display your voice activity stats. Exp based on joined vc seconds. Cooldowns 15s / user

        **Params:**
        >    **`user`** (Optional[`discord.Member`]) → target member. Defaults to `{None}`

        **Returns:**
        >    **`Embed`** → with statistics and progress bar image

        **Example:**
        > ```<prefix>vc.stats @someone```
        """
        if user != None:
            if db.servers_con['servers']['social_credit'].find({'discord_id' : user.id})[0]['v_time'] != None:
                #color = choice([":blue_square:", ":brown_square:", ":green_square:", ":orange_square:", ":purple_square:", ":red_square:", ":yellow_square:"])
                voice_time = db.servers_con['servers']['social_credit'].find({'discord_id' : user.id})[0]['v_time']
                current_level = db.servers_con['servers']['social_credit'].find({'discord_id' : user.id})[0]['v_level']
                
                current_exp = self.cur_exp(voice_time)
                batas_atas = self.factor(current_level + 1) - self.factor(current_level)

                #boxes = int((atas/bawah) * 20)
                #boxes = int((voice_time/(((current_level+9) ** 3.7) * (1 - (0.995 ** (current_level+9)))))*20)

                tahun = math.floor((voice_time / (60 * 60 * 24 * 365)))
                pekan = math.floor((voice_time % (60 * 60 * 24 * 365)) / (60 * 60 * 24 * 7))
                hari = math.floor((voice_time % (60 * 60 * 24 * 7)) / (60 * 60 * 24))
                jam = math.floor((voice_time % (60 * 60 * 24)) / (60 * 60))
                menit = math.floor((voice_time % (60 * 60)) / 60)
                detik = math.floor(voice_time % (60))

                exp_value = f"{self.number_format(current_exp)}/{self.number_format(batas_atas)}"

                # create image or load your existing image with out=Image.open(path)
                out = Image.new("RGB", (720, 25), (255, 255, 255))
                d = ImageDraw.Draw(out)

                # draw the progress bar to given location, width, progress and color
                #choice(["lime", "orange", "purple", "pink", "yellow"])
                d = self.drawProgressBar(d, 0, 0, 720, 25, (current_exp/batas_atas), bg="white", fg=tuple(int(str(user.colour).replace("#", "")[i:i+2], 16) for i in (0, 2, 4)))
                out.save(f"{user.id}.jpg")

                daftar = db.servers_con['servers']['social_credit'].find()
                data = list(daftar)
                df = pd.DataFrame(data, index=[x['discord_id'] for x in data], columns=['v_exp', 'v_time', 'v_level', 't_exp', 't_time', 't_level', 'v_violence', 't_violence', 'n_violence'])
                df['rank'] = df['v_time'].rank(ascending=False)
                ranking = df.loc[user.id]['rank']

                file = File(f"{user.id}.jpg", filename=f"{user.id}.jpg")

                embed = Embed(title=f"{user.name}'s Voice Level Stats", colour=user.colour)
                embed.add_field(name="Name", value=user.mention, inline=True)
                embed.add_field(name="Level", value=current_level, inline=True)
                embed.add_field(name="EXP", value=exp_value, inline=True)
                try:
                    embed.add_field(name="Time Spent in Voice Chat", value=f"{str(tahun) + 'y ' if tahun != 0 else ''}{str(pekan) + 'w ' if pekan != 0 else ''}{str(hari) + 'd ' if hari != 0 else ''}{str(jam) + 'h ' if jam != 0 else ''}{str(menit) + 'm ' if menit != 0 else ''}{str(detik) + 's ' if detik != 0 else ''}", inline=True)
                except Exception as e:
                    embed.add_field(name="Time Spent in Voice Chat", value=e, inline=True)
                embed.add_field(name="Rank", value=f"**{int(ranking)}**{'st' if str(int(ranking))[-1] == '1' else ('nd' if str(int(ranking))[-1] == '2' else ('rd' if str(int(ranking))[-1] == '3' else 'th'))} of {len([m for m in ctx.guild.members if not m.bot])}", inline=True)
                #embed.add_field(name="Progress Bar", value=boxes * color + (20-boxes) * ":white_large_square:", inline=False)
                embed.set_image(url=f"attachment://{user.id}.jpg")
                embed.set_thumbnail(url=user.avatar.url)
                await ctx.send(file=file, embed=embed)
            else:
                await ctx.send("User ini belum bergabung dalam voice chat!")
        else:
            if db.servers_con['servers']['social_credit'].find({'discord_id' : ctx.author.id})[0]['v_time'] != None:
                #color = choice([":blue_square:", ":brown_square:", ":green_square:", ":orange_square:", ":purple_square:", ":red_square:", ":yellow_square:"])
                voice_time = db.servers_con['servers']['social_credit'].find({'discord_id' : ctx.author.id})[0]['v_time']
                current_level = db.servers_con['servers']['social_credit'].find({'discord_id' : ctx.author.id})[0]['v_level']

                current_exp = self.cur_exp(voice_time)
                batas_atas = self.factor(current_level + 1) - self.factor(current_level)

                #boxes = int((atas/bawah) * 20)
                #boxes = int((voice_time/(((current_level+9) ** 3.7) * (1 - (0.995 ** (current_level+9)))))*20)

                tahun = math.floor((voice_time / (60 * 60 * 24 * 365)))
                pekan = math.floor((voice_time % (60 * 60 * 24 * 365)) / (60 * 60 * 24 * 7))
                hari = math.floor((voice_time % (60 * 60 * 24 * 7)) / (60 * 60 * 24))
                jam = math.floor((voice_time % (60 * 60 * 24)) / (60 * 60))
                menit = math.floor((voice_time % (60 * 60)) / 60)
                detik = math.floor(voice_time % (60))

                print(hari, jam, menit, detik)
                exp_value = f"{self.number_format(current_exp)}/{self.number_format(batas_atas)}"

                # create image or load your existing image with out=Image.open(path)
                out = Image.new("RGB", (720, 25), (255, 255, 255))
                d = ImageDraw.Draw(out)

                print(int(str(ctx.author.colour).replace("#", ""), 16))

                # draw the progress bar to given location, width, progress and color
                #choice(["lime", "orange", "purple", "pink", "yellow"])
                d = self.drawProgressBar(d, 0, 0, 720, 25, (current_exp/batas_atas), bg="white", fg=tuple(int(str(ctx.author.colour).replace("#", "")[i:i+2], 16) for i in (0, 2, 4)))
                out.save(f"{ctx.author.id}.jpg")

                daftar = db.servers_con['servers']['social_credit'].find()
                data = list(daftar)
                df = pd.DataFrame(data, index=[x['discord_id'] for x in data], columns=['v_exp', 'v_time', 'v_level', 't_exp', 't_time', 't_level', 'v_violence', 't_violence', 'n_violence'])
                df['rank'] = df['v_time'].rank(ascending=False)
                ranking = df.loc[ctx.author.id]['rank']

                file = File(f"{ctx.author.id}.jpg", filename=f"{ctx.author.id}.jpg")

                embed = Embed(title=f"{ctx.author.name}'s Voice Level Stats", colour=ctx.author.colour)
                embed.add_field(name="Name", value=ctx.author.mention, inline=True)
                embed.add_field(name="Level", value=current_level, inline=True)
                embed.add_field(name="EXP", value=exp_value, inline=True)
                
                try:
                    embed.add_field(name="Time Spent in Voice Chat", value=f"{str(tahun) + 'y ' if tahun != 0 else ''}{str(pekan) + 'w ' if pekan != 0 else ''}{str(hari) + 'd ' if hari != 0 else ''}{str(jam) + 'h ' if jam != 0 else ''}{str(menit) + 'm ' if menit != 0 else ''}{str(detik) + 's ' if detik != 0 else ''}", inline=True)
                except Exception as e:
                    embed.add_field(name="Time Spent in Voice Chat", value=e, inline=True)
                embed.add_field(name="Rank", value=f"**{int(ranking)}**{'st' if str(int(ranking))[-1] == '1' else ('nd' if str(int(ranking))[-1] == '2' else ('rd' if str(int(ranking))[-1] == '3' else 'th'))} of {len([m for m in ctx.guild.members if not m.bot])}", inline=True)
                #embed.add_field(name="Progress Bar", value=boxes * color + (20-boxes) * ":white_large_square:", inline=False)
                embed.set_image(url=f"attachment://{ctx.author.id}.jpg")
                embed.set_thumbnail(url=ctx.author.avatar.url)
                await ctx.send(file=file, embed=embed)
            else:
                await ctx.send("Bergabunglah dalam channel voice chat terlebih dahulu!")
    
    @command(name="vc.free-pull")
    @cooldown(1, 10800, BucketType.user)
    async def vc_freepull(self, ctx):
        """
        > Free gacha attemp for increasing / decreasing your exp. Cooldowns 3h / user. [Chances of exp decrease are higher]

        **Params:**
        >    takes no parameter

        **Returns:**
        >    **`str`** → gacha result

        **Example:**
        > ```<prefix>vc.gacha```
        """
        current_level = db.servers_con['servers']['social_credit'].find({'discord_id' : ctx.author.id})[0]['v_level']
        voice_time = db.servers_con['servers']['social_credit'].find({'discord_id' : ctx.author.id})[0]['v_time']

        xp_sekarang = self.cur_exp(voice_time)
        batas_atas = self.factor(current_level + 1) - self.factor(current_level)
        
        good                        = ['needed_xp', 'current_xp', 'current_level_xp_range']
        good_needed_xp              = { 100 : 0.0001,
                                        50  : 0.0039,
                                        10  : 0.006,
                                        5   : 0.02,
                                        3   : 0.07,
                                        2   : 0.2,
                                        1   : 0.4,
                                        0.8 : 0.2,
                                        0.5 : 0.05,
                                        0.3 : 0.05}
        good_current_xp             = good_needed_xp 
        good_current_level_xp_range = good_needed_xp

        bad                         = ['needed_xp', 'current_xp', 'current_level_xp_range']
        bad_needed_xp               = { -100 : 0.0001,
                                        -50  : 0.0039,
                                        -10  : 0.006,
                                        -5   : 0.02,
                                        -3   : 0.07,
                                        -2   : 0.2,
                                        -1   : 0.4,
                                        -0.8 : 0.2,
                                        -0.5 : 0.05,
                                        -0.3 : 0.05}
        bad_current_xp              = bad_needed_xp
        bad_current_level_xp_range  = bad_needed_xp

        determiner = np.random.choice(['good', 'bad'], 1, p=[0.3, 0.7])

        if determiner == 'good':
            good = ['needed_xp', 'current_xp', 'current_level_xp_range']
            good_determiner = np.random.choice(good, 1, p=[0.5, 0.3, 0.2])
            
            if good_determiner == 'needed_xp':
                result = np.random.choice(list(good_needed_xp.keys()), 1, p=list(good_needed_xp.values()))
                res = int((batas_atas - xp_sekarang) * (result[0] / 100))
                txt = f'Giving **`{result[0]}%`** of remaining xp to next level worth of **`{res}`** seconds [`{(0.3 * 0.5 * good_needed_xp[result[0]] * 100):.2f}%` chance]'
                
            elif good_determiner == 'current_xp':
                result = np.random.choice(list(good_current_xp.keys()), 1, p=list(good_current_xp.values()))
                res = int(xp_sekarang * (result[0] / 100))
                txt = f'Giving **`{result[0]}%`** of current xp this level worth of **`{res}`** seconds [`{(0.3 * 0.3 * good_current_xp[result[0]] * 100):.2f}%` chance]'
                
            else:
                result = np.random.choice(list(good_current_level_xp_range.keys()), 1, p=list(good_current_level_xp_range.values()))
                res = int(batas_atas * (result[0] / 100))
                txt = f'Giving **`{result[0]}%`** of xp range this level worth of **`{res}`** seconds [`{(0.3 * 0.2 * good_current_level_xp_range[result[0]] * 100):.2f}%` chance]'
                
        else:
            bad = ['needed_xp', 'current_xp', 'current_level_xp_range']
            bad_determiner = np.random.choice(bad, 1, p=[0.5, 0.3, 0.2])
            
            if bad_determiner == 'needed_xp':
                result = np.random.choice(list(bad_needed_xp.keys()), 1, p=list(bad_needed_xp.values()))
                res = int((batas_atas - xp_sekarang) * (result[0] / 100))
                txt = f'Giving **`{result[0]}%`** of remaining xp to next level worth of **`{res}`** seconds [`{(0.7 * 0.5 * bad_needed_xp[result[0]] * 100):.2f}%` chance]'
                
            elif bad_determiner == 'current_xp':
                result = np.random.choice(list(bad_current_xp.keys()), 1, p=list(bad_current_xp.values()))
                res = int(xp_sekarang * (result[0] / 100))
                txt = f'Giving **`{result[0]}%`** of current xp this level worth of **`{res}`** seconds [`{(0.7 * 0.3 * bad_current_xp[result[0]] * 100):.2f}%` chance]'
                
            else:
                result = np.random.choice(list(bad_current_level_xp_range.keys()), 1, p=list(bad_current_level_xp_range.values()))
                res = int(batas_atas * (result[0] / 100))
                txt = f'Giving **`{result[0]}%`** of xp range this level worth of **`{res}`** seconds [`{(0.7 * 0.2 * bad_current_level_xp_range[result[0]] * 100):.2f}%` chance]'
        
        voice_time += res
        
        level = 0
        level_txt = None
        temp = voice_time
        while temp > self.factor(level):
            level += 1
            temp -= self.factor(level + 1) - self.factor(level)
            
        if current_level < level:
            db.servers_con['servers']['social_credit'].update_one({'discord_id' : ctx.author.id}, {"$set": {'v_level': level}})
            
            # res = 0
            # for i in range(level + 1):
            #     res += self.factor(i)
                
            # db.servers_con['servers']['social_credit'].update_one({'discord_id' : i}, {"$set": {'v_exp': res + voice_time}})
            level_txt = f'```your level was increased to {level}```'
            
        elif level < current_level:
            db.servers_con['servers']['social_credit'].update_one({'discord_id' : ctx.author.id}, {"$set": {'v_level': level}})
            
            # res = 0
            # for i in range(level + 1):
            #     res += self.factor(i)
            
            # db.servers_con['servers']['social_credit'].update_one({'discord_id' : i}, {"$set": {'v_exp': res + voice_time}})
            level_txt = f'```your level was decreased to {level}```'
                
        db.servers_con['servers']['social_credit'].update_one({'discord_id' : ctx.author.id}, {"$set": {'v_time': voice_time}})
        await ctx.reply(f'{txt} {level_txt if level_txt != None else None}')
                    
    @command(name="vc.single-pull")
    @cooldown(3, 3600, BucketType.user)
    async def vc_singlepull(self, ctx):
        """
        > Non-free gacha attemp for increasing / decreasing your exp. Cooldowns 3 command / h / user with cost of 1% current exp + 1% base level exp. [Chances of exp decrease are higher]

        **Params:**
        >    takes no parameter

        **Returns:**
        >    **`str`** → gacha result

        **Example:**
        > ```<prefix>vc.single-pull```
        """
        current_level = db.servers_con['servers']['social_credit'].find({'discord_id' : ctx.author.id})[0]['v_level']
        voice_time = db.servers_con['servers']['social_credit'].find({'discord_id' : ctx.author.id})[0]['v_time']

        xp_sekarang = self.cur_exp(voice_time)
        batas_atas = self.factor(current_level + 1) - self.factor(current_level)
        
        cost =int(((1 / 100) * xp_sekarang) + ((1 / 100) * batas_atas))
        
        good                        = ['needed_xp', 'current_xp', 'current_level_xp_range']
        good_needed_xp              = { 100 : 0.0001,
                                        50  : 0.0039,
                                        30  : 0.006,
                                        25  : 0.02,
                                        10  : 0.07,
                                        5   : 0.2,
                                        3   : 0.4,
                                        4   : 0.2,
                                        6   : 0.05,
                                        7   : 0.05}
        good_current_xp             = good_needed_xp 
        good_current_level_xp_range = good_needed_xp

        bad                         = ['needed_xp', 'current_xp', 'current_level_xp_range']
        bad_needed_xp               = { -100 : 0.0001,
                                        -50  : 0.0039,
                                        -10  : 0.006,
                                        -5   : 0.02,
                                        -3   : 0.07,
                                        -2   : 0.2,
                                        -1   : 0.4,
                                        -0.8 : 0.2,
                                        -0.5 : 0.05,
                                        -0.3 : 0.05}
        bad_current_xp              = bad_needed_xp
        bad_current_level_xp_range  = bad_needed_xp

        determiner = np.random.choice(['good', 'bad'], 1, p=[0.4, 0.6])

        if determiner == 'good':
            good = ['needed_xp', 'current_xp', 'current_level_xp_range']
            good_determiner = np.random.choice(good, 1, p=[0.5, 0.3, 0.2])
            
            if good_determiner == 'needed_xp':
                result = np.random.choice(list(good_needed_xp.keys()), 1, p=list(good_needed_xp.values()))
                res = int((batas_atas - xp_sekarang) * (result[0] / 100))
                
                txt = f'Giving **`{result[0]}%`** of remaining xp to next level with cost `{cost}` seconds worth of **`{res - cost}`** seconds [`{(0.4 * 0.5 * good_needed_xp[result[0]] * 100):.2f}%` chance]'
                
            elif good_determiner == 'current_xp':
                result = np.random.choice(list(good_current_xp.keys()), 1, p=list(good_current_xp.values()))
                res = int(xp_sekarang * (result[0] / 100))
                    
                txt = f'Giving **`{result[0]}%`** of current xp this level with cost `{cost}` seconds worth of **`{res - cost}`** seconds [`{(0.4 * 0.3 * good_current_xp[result[0]] * 100):.2f}%` chance]'
                
            else:
                result = np.random.choice(list(good_current_level_xp_range.keys()), 1, p=list(good_current_level_xp_range.values()))
                res = int(batas_atas * (result[0] / 100))
                    
                txt = f'Giving **`{result[0]}%`** of xp range this level with cost `{cost}` seconds worth of **`{res - cost}`** seconds [`{(0.4 * 0.2 * good_current_level_xp_range[result[0]] * 100):.2f}%` chance]'
                
        else:
            bad = ['needed_xp', 'current_xp', 'current_level_xp_range']
            bad_determiner = np.random.choice(bad, 1, p=[0.5, 0.3, 0.2])
            
            if bad_determiner == 'needed_xp':
                result = np.random.choice(list(bad_needed_xp.keys()), 1, p=list(bad_needed_xp.values()))
                res = int((batas_atas - xp_sekarang) * (result[0] / 100))
                txt = f'Giving **`{result[0]}%`** of remaining xp to next level worth of **`{res - cost}`** seconds [`{(0.6 * 0.5 * bad_needed_xp[result[0]] * 100):.2f}%` chance]'
                
            elif bad_determiner == 'current_xp':
                result = np.random.choice(list(bad_current_xp.keys()), 1, p=list(bad_current_xp.values()))
                res = int(xp_sekarang * (result[0] / 100))
                txt = f'Giving **`{result[0]}%`** of current xp this level worth of **`{res - cost}`** seconds [`{(0.6 * 0.3 * bad_current_xp[result[0]] * 100):.2f}%` chance]'
                
            else:
                result = np.random.choice(list(bad_current_level_xp_range.keys()), 1, p=list(bad_current_level_xp_range.values()))
                res = int(batas_atas * (result[0] / 100))
                txt = f'Giving **`{result[0]}%`** of xp range this level worth of **`{res - cost}`** seconds [`{(0.6 * 0.2 * bad_current_level_xp_range[result[0]] * 100):.2f}%` chance]'
        
        voice_time += (res - cost)
        
        level = 0
        level_txt = None
        temp = voice_time
        while temp > self.factor(level):
            level += 1
            temp -= self.factor(level + 1) - self.factor(level)
            
        if current_level < level:
            db.servers_con['servers']['social_credit'].update_one({'discord_id' : ctx.author.id}, {"$set": {'v_level': level}})
            
            # res = 0
            # for i in range(level + 1):
            #     res += self.factor(i)
                
            # db.servers_con['servers']['social_credit'].update_one({'discord_id' : i}, {"$set": {'v_exp': res + voice_time}})
            level_txt = f'```your level was increased to {level}```'
            
        elif level < current_level:
            db.servers_con['servers']['social_credit'].update_one({'discord_id' : ctx.author.id}, {"$set": {'v_level': level}})
            
            # res = 0
            # for i in range(level + 1):
            #     res += self.factor(i)
            
            # db.servers_con['servers']['social_credit'].update_one({'discord_id' : i}, {"$set": {'v_exp': res + voice_time}})
            level_txt = f'```your level was decreased to {level}```'
        
        try:
            pity = db.servers_con['servers']['others'].find({'discord_id' : ctx.author.id})[0]['v_pity']
            db.servers_con['servers']['others'].update_one({'discord_id' : ctx.author.id}, {"$set": {'v_pity': pity + 1}})
        except:
            db.servers_con['servers']['others'].insert_one({'discord_id' : ctx.author.id, 'v_pity': 1})
            
        if result == 100:
            db.servers_con['servers']['others'].update_one({'discord_id' : ctx.author.id}, {"$set": {'v_pity': 0}})
            
        db.servers_con['servers']['social_credit'].update_one({'discord_id' : ctx.author.id}, {"$set": {'v_time': voice_time}})
        
        await ctx.reply(f'{txt} {level_txt if level_txt != None else None}')
        
    @command(name="vc.unlimited-pull")
    @cooldown(1, 60, BucketType.user)
    async def vc_unlimitedpull(self, ctx, times = 1):
        """
        > Non-free gacha attemp for increasing / decreasing your exp. 60s cooldown, but starts with 1% chance that increasing by 1% for each pull. Cost 50% of (1% base level exp + 1% current exp) that recalculated after each pull.

        **Params:**
        >    **`times`** (Optional[`int`]) → times of pull. Defaults to `{1}`, maximum to `{10}`

        **Returns:**
        >    **`str`** → gacha result

        **Example:**
        > ```<prefix>vc.unlimited-pull 5```
        """
        times = int(times)
        
        if times > 10:
            raise Exception('times should not exceed 10')
            ctx.command.reset_cooldown(ctx) 
        
        good                        = ['needed_xp', 'current_xp', 'current_level_xp_range']
        good_needed_xp              = { 1000 : 0.05,
                                        500 : 0.15,
                                        300  : 0.8}
        good_current_xp             = good_needed_xp 
        good_current_level_xp_range = good_needed_xp

        bad                         = ['needed_xp', 'current_xp', 'current_level_xp_range']
        bad_needed_xp               = { -100 : 0.0001,
                                        -75  : 0.0039,
                                        -50  : 0.006,
                                        -20   : 0.02,
                                        -10   : 0.07,
                                        -9   : 0.2,
                                        -8   : 0.4,
                                        -7 : 0.2,
                                        -6 : 0.05,
                                        -5 : 0.05}
        bad_current_xp              = bad_needed_xp
        bad_current_level_xp_range  = bad_needed_xp
        
        summary = 0
        for i in range(times):
            try:
                chance = db.servers_con['servers']['others'].find({'discord_id' : ctx.author.id})[0]['v_chance']
            except:
                chance = 0.01
                db.servers_con['servers']['others'].insert_one({'discord_id' : ctx.author.id, 'v_chance': chance})
                
            current_level = db.servers_con['servers']['social_credit'].find({'discord_id' : ctx.author.id})[0]['v_level']
            voice_time = db.servers_con['servers']['social_credit'].find({'discord_id' : ctx.author.id})[0]['v_time']

            xp_sekarang = self.cur_exp(voice_time)
            batas_atas = self.factor(current_level + 1) - self.factor(current_level)
            
            cost =int(5/10 * (((1 / 100) * xp_sekarang) + ((1 / 100) * batas_atas)))

            determiner = np.random.choice(['good', 'bad'], 1, p=[chance, 1 - chance])

            if determiner == 'good':
                good = ['needed_xp', 'current_xp', 'current_level_xp_range']
                good_determiner = np.random.choice(good, 1, p=[0.5, 0.3, 0.2])
                
                if good_determiner == 'needed_xp':
                    result = np.random.choice(list(good_needed_xp.keys()), 1, p=list(good_needed_xp.values()))
                    res = int((batas_atas - xp_sekarang) * (result[0] / 100))
                    
                    chance = 0
                    db.servers_con['servers']['others'].update_one({'discord_id' : ctx.author.id}, {"$set": {'v_chance': chance}})
                    txt = f'Giving **`{result[0]}%`** of remaining xp to next level with cost `{cost}` seconds worth of **`{res - cost}`** seconds [`{(chance * 0.5 * good_needed_xp[result[0]] * 100):.2f}%` chance]'
                    
                elif good_determiner == 'current_xp':
                    result = np.random.choice(list(good_current_xp.keys()), 1, p=list(good_current_xp.values()))
                    res = int(xp_sekarang * (result[0] / 100))
                    
                    chance = 0
                    db.servers_con['servers']['others'].update_one({'discord_id' : ctx.author.id}, {"$set": {'v_chance': chance}})    
                    txt = f'Giving **`{result[0]}%`** of current xp this level with cost `{cost}` seconds worth of **`{res - cost}`** seconds [`{(chance * 0.3 * good_current_xp[result[0]] * 100):.2f}%` chance]'
                    
                else:
                    result = np.random.choice(list(good_current_level_xp_range.keys()), 1, p=list(good_current_level_xp_range.values()))
                    res = int(batas_atas * (result[0] / 100))
                    
                    chance = 0
                    db.servers_con['servers']['others'].update_one({'discord_id' : ctx.author.id}, {"$set": {'v_chance': chance}})    
                    txt = f'Giving **`{result[0]}%`** of xp range this level with cost `{cost}` seconds worth of **`{res - cost}`** seconds [`{(chance * 0.2 * good_current_level_xp_range[result[0]] * 100):.2f}%` chance]'
                    
            else:
                bad = ['needed_xp', 'current_xp', 'current_level_xp_range']
                bad_determiner = np.random.choice(bad, 1, p=[0.5, 0.3, 0.2])
                
                if bad_determiner == 'needed_xp':
                    result = np.random.choice(list(bad_needed_xp.keys()), 1, p=list(bad_needed_xp.values()))
                    res = int((batas_atas - xp_sekarang) * (result[0] / 100))
                    txt = f'Giving **`{result[0]}%`** of remaining xp to next level worth of **`{res - cost}`** seconds [`{((1 - chance) * 0.5 * bad_needed_xp[result[0]] * 100):.2f}%` chance]'
                    
                elif bad_determiner == 'current_xp':
                    result = np.random.choice(list(bad_current_xp.keys()), 1, p=list(bad_current_xp.values()))
                    res = int(xp_sekarang * (result[0] / 100))
                    txt = f'Giving **`{result[0]}%`** of current xp this level worth of **`{res - cost}`** seconds [`{((1 - chance) * 0.3 * bad_current_xp[result[0]] * 100):.2f}%` chance]'
                    
                else:
                    result = np.random.choice(list(bad_current_level_xp_range.keys()), 1, p=list(bad_current_level_xp_range.values()))
                    res = int(batas_atas * (result[0] / 100))
                    txt = f'Giving **`{result[0]}%`** of xp range this level worth of **`{res - cost}`** seconds [`{((1 - chance) * 0.2 * bad_current_level_xp_range[result[0]] * 100):.2f}%` chance]'
            
            summary += (res - cost)
            voice_time += (res - cost)
            
            level = 0
            level_txt = None
            temp = voice_time
            while temp > self.factor(level):
                level += 1
                temp -= self.factor(level + 1) - self.factor(level)
                
            if current_level < level:
                db.servers_con['servers']['social_credit'].update_one({'discord_id' : ctx.author.id}, {"$set": {'v_level': level}})
                
                # res = 0
                # for i in range(level + 1):
                #     res += self.factor(i)
                    
                # db.servers_con['servers']['social_credit'].update_one({'discord_id' : i}, {"$set": {'v_exp': res + voice_time}})
                level_txt = f'```your level was increased to {level}```'
                
            elif level < current_level:
                db.servers_con['servers']['social_credit'].update_one({'discord_id' : ctx.author.id}, {"$set": {'v_level': level}})
                
                # res = 0
                # for i in range(level + 1):
                #     res += self.factor(i)
                
                # db.servers_con['servers']['social_credit'].update_one({'discord_id' : i}, {"$set": {'v_exp': res + voice_time}})
                level_txt = f'```your level was decreased to {level}```'
                
            db.servers_con['servers']['social_credit'].update_one({'discord_id' : ctx.author.id}, {"$set": {'v_time': voice_time}})
            db.servers_con['servers']['others'].update_one({'discord_id' : ctx.author.id}, {"$set": {'v_chance': chance + 0.01}})
            
            await ctx.reply(f'{txt}\n```Current chance : {((chance + 0.02) * 100):.2f}%```{level_txt if level_txt != None else None}')
            await sleep(1)
        await ctx.reply(embed = Embed(title = 'Pull Summary', description = f'The result of {str(times) + " pulls are :" if times > 1 else " pull is :"}\n> **`{summary}` exp earned**\n> Current chance **`{((chance + 0.02) * 100):.2f}%`**'))
            
def setup(bot):
    bot.add_cog(Exp(bot))