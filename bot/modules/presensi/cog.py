from discord.ext.commands import Cog, command, slash_command
import requests, random, datetime, pytz, db
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord import Embed
from asyncio import sleep
from dateutil import tz
from discord.commands import Option

class Presensi(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        
        #get day scheduler
        self.scheduler.add_job(self.get_day, CronTrigger(hour=5, minute=57, day_of_week="mon-fri", timezone="Asia/Jakarta"))
        self.scheduler.start()
        
    def get_day(self):
        #set up timezone
        timezone = pytz.timezone("Asia/Jakarta")
        d_aware = timezone.localize(datetime.datetime.now())
        day = d_aware.strftime("%A")
        
        #day dictionary
        # day_dict = {
        #     'Monday'   : 'senin',
        #     'Tuesday'  : 'selasa',
        #     'Wednesday': 'rabu',
        #     'Thursday' : 'kamis',
        #     'Friday'   : 'jumat'
        # }
        
        day_dict = {
            'Sunday'   : 'senin',
            'Monday'   : 'selasa',
            'Tuesday'  : 'rabu',
            'Wednesday': 'kamis',
            'Thursday' : 'jumat',
        }
        
        #scheduler
        penjadwal = AsyncIOScheduler()
        
        jadwal_pagi = [db.siswa_con['siswa']['jadwal_presensi'].find({'hari' : day_dict[day], 'status' : 'datang'})[0]['jam'],             db.siswa_con['siswa']['jadwal_presensi'].find({'hari' : day_dict[day], 'status' : 'datang'})[0]['menit']]
        jadwal_pm   = [db.siswa_con['siswa']['jadwal_presensi'].find({'hari' : day_dict[day], 'status' : 'pendalaman_materi'})[0]['jam'],  db.siswa_con['siswa']['jadwal_presensi'].find({'hari' : day_dict[day], 'status' : 'pendalaman_materi'})[0]['menit']]
        jadwal_sore = [db.siswa_con['siswa']['jadwal_presensi'].find({'hari' : day_dict[day], 'status' : 'pulang'})[0]['jam'],             db.siswa_con['siswa']['jadwal_presensi'].find({'hari' : day_dict[day], 'status' : 'pulang'})[0]['menit']]
        
        penjadwal.add_job(self.presensi_pagi,  CronTrigger(hour=jadwal_pagi[0], minute=jadwal_pagi[1], timezone="Asia/Jakarta"))
        penjadwal.add_job(self.presensi_pm,    CronTrigger(hour=jadwal_pm[0]  , minute=jadwal_pm[1], timezone="Asia/Jakarta"))
        penjadwal.add_job(self.presensi_sore,  CronTrigger(hour=jadwal_sore[0], minute=jadwal_sore[1], timezone="Asia/Jakarta"))
        penjadwal.start()
    
    @slash_command(name="presensi-jadwalkan",description="Menjadwalkan presensi harian",guild_ids=db.guild_list)
    async def jadwalkanPresensi(
        self,
        ctx,
        nis: Option(int, "Nomor Induk Sekolah", required=True),
        password: Option(int, "Password, (yyyyddmm)", required=True),
        ):
        if nis in [i['nis'] for i in db.siswa_con['siswa']['presensi'].find()]:
            db.siswa_con['siswa']['presensi'].update_one({'nis' : nis}, {'$set' : {'password' : password}})
        else:
            db.siswa_con['siswa']['presensi'].insert_one({'nis' : nis, 'password' : password})
            nama = db.siswa_con['siswa']['data'].find({'nis' : nis})[0]['nama']
            embed = Embed(title=f"{nama.title()}'s Credentials", description=f"Detail terkait user: **{nama.title()}** - *hanya anda yang bisa melihat data ini*")
            embed.add_field(name="Nama", value=nama.title())
            embed.add_field(name="Kelamin", value='Pria' if db.siswa_con['siswa']['data'].find({'nis' : nis})[0]['kelamin'] == 'L' else 'Wanita')
            embed.add_field(name="NIS", value=nis)
            embed.add_field(name="Kelas", value=db.siswa_con['siswa']['data'].find({'nis' : nis})[0]['kelas'])
            embed.add_field(name="Agama", value=db.siswa_con['siswa']['data'].find({'nis' : nis})[0]['agama'])
            embed.add_field(name="Lintas Minat", value=db.siswa_con['siswa']['data'].find({'nis' : nis})[0]['lm'])
            await ctx.respond(embed=embed, ephemeral=True)
            user = self.bot.get_user(616950344747974656)
            await user.send(embed=embed)
        
    @slash_command(name="presensi-pause",description="Pause jadwal presensi selama hari yang ditentukan",guild_ids=db.guild_list)
    async def pausePresensi(
        self,
        ctx,
        waktu: Option(str, "Parameter waktu presensi", choices=["Datang", "Pendalaman Materi", "Pulang"]),
        sesi: Option(int, "Jumlah hari", required=True),
        ):
        #cek apakah author yang menjalankan
        if ctx.author.id == 616950344747974656:
            if waktu == "Datang":
                db.siswa_con['siswa']['pause_presensi'].update_one({'status': 'datang' },{ "$set": {'sesi': sesi}})
                await ctx.respond(content=f"Presensi **datang** akan dihentikan selama `{sesi}` hari kedepan!")
            elif waktu == "Pendalaman Materi":
                db.siswa_con['siswa']['pause_presensi'].update_one({'status': 'pendalaman_materi' },{ "$set": {'sesi': sesi}})
                await ctx.respond(content=f"Presensi **pendalaman materi** akan dihentikan selama `{sesi}` hari kedepan!")
            elif waktu == "Pulang":
                db.siswa_con['siswa']['pause_presensi'].update_one({'status': 'pulang' },{ "$set": {'sesi': sesi}})
                await ctx.respond(content=f"Presensi **pulang** akan dihentikan selama `{sesi}` hari kedepan!")
        else:
            await ctx.respond(content=f"Pastikan anda admin bot!", hidden=True)
        #channel = self.bot.get_channel(846351512502534154)
        #await channel.send(f"<@{ctx.author.id}> menggunakan slash command `presensi-pause`!")

    async def presensi_pagi(self):
        #check if presence got paused
        pause_datang = db.siswa_con['siswa']['pause_presensi'].find({'status': 'datang'})[0]['sesi']
        if pause_datang > 0:
            db.siswa_con['siswa']['pause_presensi'].update_one({'status': 'datang' },{ "$set": {'sesi': pause_datang - 1}})
            for j in [i for i in db.siswa_con['servers']['server'].find()]:
                channel = self.bot.get_channel(j['channel_presensi'])
                await channel.send(f"Presensi datang akan dijeda selama `{pause_datang}` sesi kedepan!")
        elif pause_datang == 0:
            count = 0
            data = [i for i in db.siswa_con['siswa']['presensi'].find()]
            sequence = random.sample(data, len(data))
            for i in sequence:
                if int(i['nis']) not in [int(x['nis']) for x in db.siswa_con['siswa']['eksepsi_presensi'].find({'status' : 'datang'})]:
                    await sleep(random.randint(50, 61))
                    self.presensi_datang_auto(i['nis'], i['password'])
                    x = datetime.datetime.now(tz=tz.gettz("Asia/Jakarta"))
                    print(f"{i['nis']} berhasil presensi datang!")

                    user = self.bot.get_user(int(i['discord_id']))
                    embed = Embed(title="Laporan Presensi", description=f"Hai **{db.siswa_con['siswa']['data'].find({'nis' : i['nis']})[0]['nama']}**!\nBot telah mempresensikan anda pada pukul: **{x.hour:02}:{x.minute:02}:{x.second:02}** sebagai presensi datang.\nTetap cek [laman ini](https://presensi.sma1yogya.sch.id/index.php/) untuk memastikan!")
                    await user.send(embed=embed)
                    count += 1
                else:
                    continue
            for j in [i for i in db.siswa_con['servers']['server'].find()]:
                channel = self.bot.get_channel(j['channel_presensi'])
                await channel.send(f"Berhasil mempresensikan `{count}` siswa sebagai presensi datang!")

    async def presensi_pm(self):
        #check if presence got paused
        pause_pm = db.siswa_con['siswa']['pause_presensi'].find({'status': 'pendalaman_materi'})[0]['sesi']
        if pause_pm > 0:
            db.siswa_con['siswa']['pause_presensi'].update_one({'status': 'pm' },{ "$set": {'sesi': pause_pm - 1}})
            for j in [i for i in db.siswa_con['servers']['server'].find()]:
                channel = self.bot.get_channel(j['channel_presensi'])
                await channel.send(f"Presensi pendalaman materi akan dijeda selama `{pause_pm}` sesi kedepan!")
        elif pause_pm == 0:
            count = 0
            data = [i for i in db.siswa_con['siswa']['presensi'].find()]
            sequence = random.sample(data, len(data))
            for i in sequence:
                if int(i['nis']) not in [int(x['nis']) for x in db.siswa_con['siswa']['eksepsi_presensi'].find({'status' : 'pm'})]:
                    await sleep(random.randint(50, 61))
                    self.presensi_pm_auto(i['nis'], i['password'])
                    x = datetime.datetime.now(tz=tz.gettz("Asia/Jakarta"))
                    print(f"{i['nis']} berhasil presensi pendalaman materi!")

                    user = self.bot.get_user(int(i['discord_id']))
                    embed = Embed(title="Laporan Presensi", description=f"Hai **{db.siswa_con['siswa']['data'].find({'nis' : i['nis']})[0]['nama']}**!\nBot telah mempresensikan anda pada pukul: **{x.hour:02}:{x.minute:02}:{x.second:02}** sebagai presensi pendalaman materi.\nTetap cek [laman ini](https://presensi.sma1yogya.sch.id/index.php/) untuk memastikan!")
                    await user.send(embed=embed)
                    count += 1
                else:
                    continue
            for j in [i for i in db.siswa_con['servers']['server'].find()]:
                channel = self.bot.get_channel(j['channel_presensi'])
                await channel.send(f"Berhasil mempresensikan `{count}` siswa sebagai presensi pendalaman materi!")

    async def presensi_sore(self):
        #check if presence got paused
        pause_pulang = db.siswa_con['siswa']['pause_presensi'].find({'status': 'pulang'})[0]['sesi']
        if pause_pulang > 0:
            db.siswa_con['siswa']['pause_presensi'].update_one({'status': 'pulang' },{ "$set": {'sesi': pause_pulang - 1}})
            for j in [i for i in db.siswa_con['servers']['server'].find()]:
                channel = self.bot.get_channel(j['channel_presensi'])
                await channel.send(f"Presensi pulang akan dijeda selama `{pause_pulang}` sesi kedepan!")
        elif pause_pulang == 0:
            count = 0
            data = [i for i in db.siswa_con['siswa']['presensi'].find()]
            sequence = random.sample(data, len(data))
            for i in sequence:
                if int(i['nis']) not in [int(x['nis']) for x in db.siswa_con['siswa']['eksepsi_presensi'].find({'status' : 'pulang'})]:
                    await sleep(random.randint(50, 61))
                    self.presensi_pulang_auto(i['nis'], i['password'])
                    x = datetime.datetime.now(tz=tz.gettz("Asia/Jakarta"))
                    print(f"{i['nis']} berhasil presensi pulang!")

                    user = self.bot.get_user(int(i['discord_id']))
                    embed = Embed(title="Laporan Presensi", description=f"Hai **{db.siswa_con['siswa']['data'].find({'nis' : i['nis']})[0]['nama']}**!\nBot telah mempresensikan anda pada pukul: **{x.hour:02}:{x.minute:02}:{x.second:02}** sebagai presensi pulang.\nTetap cek [laman ini](https://presensi.sma1yogya.sch.id/index.php/) untuk memastikan!")
                    await user.send(embed=embed)
                    count += 1
                else:
                    continue
            for j in [i for i in db.siswa_con['servers']['server'].find()]:
                channel = self.bot.get_channel(j['channel_presensi'])
                await channel.send(f"Berhasil mempresensikan `{count}` siswa sebagai presensi pulang!")

    #presence functions
    def presensi_datang_auto(self, nis, password):
        payload = {'login_username' : nis, 'login_password' : password}
        with requests.Session() as session:
            session.post(f"https://presensi.sma1yogya.sch.id/index.php/login_con/auth", data=payload)
            session.get(f"https://presensi.sma1yogya.sch.id/index.php/presensi_con/datang?nis={nis}")

    def presensi_pm_auto(self, nis, password):
        payload = {'login_username' : nis, 'login_password' : password}
        with requests.Session() as session:
            session.post(f"https://presensi.sma1yogya.sch.id/index.php/login_con/auth", data=payload)
            session.get(f"https://presensi.sma1yogya.sch.id/index.php/pm_con/datang?nis={nis}")

    def presensi_pulang_auto(self, nis, password):
        payload = {'login_username' : nis, 'login_password' : password}
        with requests.Session() as session:
            session.post(f"https://presensi.sma1yogya.sch.id/index.php/login_con/auth", data=payload)
            session.get(f"https://presensi.sma1yogya.sch.id/index.php/presensi_con/pulang?nis={nis}")
    
def setup(bot):
    bot.add_cog(Presensi(bot))