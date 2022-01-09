from discord.ext.commands import Cog, command, slash_command
import requests, json, os, random
from discord import Embed
from discord.commands import Option
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import datetime
import db

class Agama(Cog):
    """
    > Get prayer times, scheduling, and qur'an from this module.
    """
    def __init__(self, bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.scheduler.add_job(self.quran_acak, CronTrigger(hour=0, minute=0, timezone="Asia/Jakarta"))
        self.scheduler.start()
        self.scheduler_shalat = AsyncIOScheduler()

    async def jadwal_shalat_rutin(self):
        for i in db.servers_con.servers.server.find():
            try:
                self.channel = self.bot.get_channel(i['shalat_channel']['id'])
                self.data = {"city" : i['shalat_channel']['kota'], "country" : i['shalat_channel']['negara'], "method" : i['shalat_channel']['metode']}
                self.url = requests.get("http://api.aladhan.com/v1/timingsByCity", params=self.data)
                self.waktu_shalat = json.loads(self.url.text)
                self.kota = i['shalat_channel']['kota']
                self.negara = i['shalat_channel']['negara']
                self.metode = self.waktu_shalat['data']['meta']['method']['name']
                self.subuh = self.waktu_shalat['data']['timings']['Fajr']
                self.terbit = self.waktu_shalat['data']['timings']['Sunrise']
                self.dzuhur = self.waktu_shalat['data']['timings']['Dhuhr']
                self.ashar = self.waktu_shalat['data']['timings']['Asr']
                self.maghrib = self.waktu_shalat['data']['timings']['Maghrib']
                self.isya = self.waktu_shalat['data']['timings']['Isha']
                self.timezone = self.waktu_shalat['data']['meta']['timezone']
                self.tanggal = self.waktu_shalat['data']['date']['readable']
                try:
                    async def rangkuman_jadwal():
                        self.channel = self.bot.get_channel(i['shalat_channel']['id'])
                        self.data = {"city" : i['shalat_channel']['kota'], "country" : i['shalat_channel']['negara'], "method" : i['shalat_channel']['metode']}
                        self.url = requests.get("http://api.aladhan.com/v1/timingsByCity", params=self.data)
                        self.waktu_shalat = json.loads(self.url.text)
                        self.kota = i['shalat_channel']['kota']
                        self.negara = i['shalat_channel']['negara']
                        self.metode = self.waktu_shalat['data']['meta']['method']['name']
                        self.subuh = self.waktu_shalat['data']['timings']['Fajr']
                        self.terbit = self.waktu_shalat['data']['timings']['Sunrise']
                        self.dzuhur = self.waktu_shalat['data']['timings']['Dhuhr']
                        self.ashar = self.waktu_shalat['data']['timings']['Asr']
                        self.maghrib = self.waktu_shalat['data']['timings']['Maghrib']
                        self.isya = self.waktu_shalat['data']['timings']['Isha']
                        self.timezone = self.waktu_shalat['data']['meta']['timezone']
                        self.tanggal = self.waktu_shalat['data']['date']['readable']

                        embed = Embed(title='Waktu Shalat Hari Ini!', description=f'Untuk wilayah {self.kota}, {self.negara}.', colour=0xFF2400)
                        fields = [("Subuh", self.subuh, True),
                                ("Terbit", self.terbit, True),
                                ("Dzuhur", self.dzuhur, True),
                                ("Ashar", self.ashar, True),
                                ("Maghrib", self.maghrib, True),
                                ("Isya\'", self.isya, True)]
                        for name, value, inline in fields:
                            embed.add_field(name=name, value=value, inline=inline)
                        embed.set_author(name="Prayer Reminder", icon_url="http://amaliyah.net/wp-content/uploads/2021/03/Shahada-Salat-Calligraphy.png")
                        embed.set_footer(text=f"Method: {self.metode}\nTimezone: {self.timezone}\nDate: {self.tanggal}")
                        await self.channel.send(embed=embed)

                    async def subuh_reminder():
                        embed = Embed(title='Waktu Shalat!', description=f'Untuk wilayah {self.kota}, {self.negara}.', colour=0xFF2400)
                        embed.add_field(name="Subuh", value=self.subuh)
                        embed.set_author(name="Prayer Reminder", icon_url="http://amaliyah.net/wp-content/uploads/2021/03/Shahada-Salat-Calligraphy.png")
                        embed.set_footer(text=f"Timezone: {self.timezone}\nDate: {self.tanggal}")
                        await self.channel.send(content="@everyone", embed=embed, delete_after=3600)
                    
                    async def terbit_reminder():
                        embed = Embed(title='Waktu Terbit!', description=f'Untuk wilayah {self.kota}, {self.negara}.', colour=0xFF2400)
                        embed.add_field(name="Terbit", value=self.terbit)
                        embed.set_author(name="Prayer Reminder", icon_url="http://amaliyah.net/wp-content/uploads/2021/03/Shahada-Salat-Calligraphy.png")
                        embed.set_footer(text=f"Timezone: {self.timezone}\nDate: {self.tanggal}")
                        await self.channel.send(embed=embed, delete_after=3600)

                    async def dzuhur_reminder():
                        embed = Embed(title='Waktu Shalat!', description=f'Untuk wilayah {self.kota}, {self.negara}.', colour=0xFF2400)
                        embed.add_field(name="Dzuhur", value=self.dzuhur)
                        embed.set_author(name="Prayer Reminder", icon_url="http://amaliyah.net/wp-content/uploads/2021/03/Shahada-Salat-Calligraphy.png")
                        embed.set_footer(text=f"Timezone: {self.timezone}\nDate: {self.tanggal}")
                        await self.channel.send(content="@everyone", embed=embed, delete_after=3600)

                    async def ashar_reminder():
                        embed = Embed(title='Waktu Shalat!', description=f'Untuk wilayah {self.kota}, {self.negara}.', colour=0xFF2400)
                        embed.add_field(name="Ashar", value=self.ashar)
                        embed.set_author(name="Prayer Reminder", icon_url="http://amaliyah.net/wp-content/uploads/2021/03/Shahada-Salat-Calligraphy.png")
                        embed.set_footer(text=f"Timezone: {self.timezone}\nDate: {self.tanggal}")
                        await self.channel.send(content="@everyone", embed=embed, delete_after=3600)

                    async def maghrib_reminder():
                        embed = Embed(title='Waktu Shalat!', description=f'Untuk wilayah {self.kota}, {self.negara}.', colour=0xFF2400)
                        embed.add_field(name="Maghrib", value=self.maghrib)
                        embed.set_author(name="Prayer Reminder", icon_url="http://amaliyah.net/wp-content/uploads/2021/03/Shahada-Salat-Calligraphy.png")
                        embed.set_footer(text=f"Timezone: {self.timezone}\nDate: {self.tanggal}")
                        await self.channel.send(content="@everyone", embed=embed, delete_after=3600)

                    async def isya_reminder():
                        embed = Embed(title='Waktu Shalat!', description=f'Untuk wilayah {self.kota}, {self.negara}.', colour=0xFF2400)
                        embed.add_field(name="Isya\'", value=self.isya)
                        embed.set_author(name="Prayer Reminder", icon_url="http://amaliyah.net/wp-content/uploads/2021/03/Shahada-Salat-Calligraphy.png")
                        embed.set_footer(text=f"Timezone: {self.timezone}\nDate: {self.tanggal}")
                        await self.channel.send(content="@everyone", embed=embed, delete_after=3600)

                    self.scheduler_shalat.add_job(rangkuman_jadwal, CronTrigger(hour=0, minute=0, second=5, timezone="Asia/Jakarta"), id="jadwal_utama")
                    self.scheduler_shalat.add_job(subuh_reminder, CronTrigger(hour=int(self.subuh[0:2]), minute=int(self.subuh[3:]), end_date=datetime.datetime.now() + datetime.timedelta(days=1), timezone=self.timezone))
                    self.scheduler_shalat.add_job(terbit_reminder, CronTrigger(hour=int(self.terbit[0:2]), minute=int(self.terbit[3:]), end_date=datetime.datetime.now() + datetime.timedelta(days=1), timezone=self.timezone))
                    self.scheduler_shalat.add_job(dzuhur_reminder, CronTrigger(hour=int(self.dzuhur[0:2]), minute=int(self.dzuhur[3:]), end_date=datetime.datetime.now() + datetime.timedelta(days=1), timezone=self.timezone))
                    self.scheduler_shalat.add_job(ashar_reminder, CronTrigger(hour=int(self.ashar[0:2]), minute=int(self.ashar[3:]), end_date=datetime.datetime.now() + datetime.timedelta(days=1), timezone=self.timezone))
                    self.scheduler_shalat.add_job(maghrib_reminder, CronTrigger(hour=int(self.maghrib[0:2]), minute=int(self.maghrib[3:]), end_date=datetime.datetime.now() + datetime.timedelta(days=1), timezone=self.timezone))
                    self.scheduler_shalat.add_job(isya_reminder, CronTrigger(hour=int(self.isya[0:2]), minute=int(self.isya[3:]), end_date=datetime.datetime.now() + datetime.timedelta(days=1), timezone=self.timezone))
                    self.scheduler_shalat.start()
                except Exception as e:
                    print(e)
            except Exception as e:
                print(e)
                

    @slash_command(name="shalat-coroutine-settings", description="Mengatur parameter untuk jadwal shalat rutin dalam channel yang telah ditentukan", guild_ids=db.guild_list)
    async def _shalatsettings(
        self,
        ctx,
        kota : Option(str, "Kota, contoh : Yogyakarta", required=True), 
        negara : Option(str, "Negara, contoh : Indonesia atau 2 karakter Alpha ISO 1366 : ID", required=True),
        metode : Option(int, "Metode penentuan waktu, default = 3", required=False, default=3)
        ):
        if ctx.author.guild_permissions.administrator:
            try:
                db.servers_con.servers.server.find_one_and_update({'server_id' : ctx.guild.id}, {'$set' : {'shalat_channel.kota' : kota, 'shalat_channel.negara' : negara, 'shalat_channel.metode' : metode}})
                embed = Embed(title="Preferensi Jadwal Waktu Shalat!", description="Preferensi lengkap terkait penentuan waktu shalat di channel ini", colour=0xFF2400)
                data = {"city" : kota, "country" : negara, "method" : metode}
                url = requests.get("http://api.aladhan.com/v1/timingsByCity", params=data)
                waktu_shalat = json.loads(url.text)
                offset = waktu_shalat['data']['meta']['offset']
                zona_waktu = waktu_shalat['data']['meta']['timezone']
                metode = waktu_shalat['data']['meta']['method']['name']
                embed.add_field(name="Daerah", value=f"{kota}, {negara}", inline=False)
                embed.add_field(name="Metode", value=f"{metode}", inline=False)
                embed.add_field(name="Zona Waktu", value=zona_waktu, inline=False)
                embed.set_author(name="Prayer Reminder", icon_url="http://amaliyah.net/wp-content/uploads/2021/03/Shahada-Salat-Calligraphy.png")
                await ctx.respond(embed=embed)
            except Exception as e:
                await ctx.respond(content=e, ephemeral=True)

    @slash_command(name="shalat-jadwal",description="Memberikan jadwal shalat hari ini",guild_ids=db.guild_list)
    async def _shalat(
        self,
        ctx,
        kota : Option(str, "Kota, contoh : Yogyakarta", required=True), 
        negara : Option(str, "Negara, contoh : Indonesia atau 2 karakter Alpha ISO 1366 : ID", required=True),
        metode : Option(int, "Metode penentuan waktu, default = 3", required=False, default=3)
        ):
        """Memberitahu jadwal shalat hari ini dengan bantuan 3rd party API"""
        self.kota = kota
        self.negara = negara
        data = {"city" : kota, "country" : negara, "method" : metode, "tune" : "-9,-9,0,0,0,0,0,5"}
        self.url = requests.get("http://api.aladhan.com/v1/timingsByCity", params=data)
        self.waktu_shalat = json.loads(self.url.text)
        self.subuh = self.waktu_shalat['data']['timings']['Fajr']
        self.terbit = self.waktu_shalat['data']['timings']['Sunrise']
        self.dzuhur = self.waktu_shalat['data']['timings']['Dhuhr']
        self.ashar = self.waktu_shalat['data']['timings']['Asr']
        self.maghrib = self.waktu_shalat['data']['timings']['Maghrib']
        self.isya = self.waktu_shalat['data']['timings']['Isha']
        self.timezone = self.waktu_shalat['data']['meta']['timezone']
        self.metode = self.waktu_shalat['data']['meta']['method']['name']
        self.tanggal = self.waktu_shalat['data']['date']['readable']

        embed = Embed(title='Waktu Shalat!', description=f'Untuk wilayah {self.kota}, {self.negara}.', colour=0xFF2400)
        fields = [("Subuh", self.subuh, True),
                ("Terbit", self.terbit, True),
                ("Dzuhur", self.dzuhur, True),
                ("Ashar", self.ashar, True),
                ("Maghrib", self.maghrib, True),
                ("Isya\'", self.isya, True)]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        embed.set_author(name="Prayer Reminder", icon_url="http://amaliyah.net/wp-content/uploads/2021/03/Shahada-Salat-Calligraphy.png")
        embed.set_footer(text=f"Method: {self.metode}\nTimezone: {self.timezone}\nDate: {self.tanggal}")
        await ctx.respond(embed=embed)

    @command(name="shalat.jadwal", aliases=["shalat", "jadwalShalat"])
    async def jadwal_shalat(self, ctx, kota="Yogyakarta", negara="Indonesia", metode=3):
        """Memberitahu jadwal shalat hari ini dengan bantuan 3rd party API"""
        self.kota = kota
        self.negara = negara
        self.url = requests.request("GET",f"http://api.aladhan.com/v1/timingsByCity?city={kota}&country={negara}&method={metode}")
        self.waktu_shalat = json.loads(self.url.text)
        self.subuh = self.waktu_shalat['data']['timings']['Fajr']
        self.terbit = self.waktu_shalat['data']['timings']['Sunrise']
        self.dzuhur = self.waktu_shalat['data']['timings']['Dhuhr']
        self.ashar = self.waktu_shalat['data']['timings']['Asr']
        self.maghrib = self.waktu_shalat['data']['timings']['Maghrib']
        self.isya = self.waktu_shalat['data']['timings']['Isha']
        self.timezone = self.waktu_shalat['data']['meta']['timezone']
        self.tanggal = self.waktu_shalat['data']['date']['readable']

        embed = Embed(title='Waktu Shalat!', description=f'Untuk wilayah {self.kota}, {self.negara}.', colour=0xFF2400)
        fields = [("Subuh", self.subuh, True),
                ("Terbit", self.terbit, True),
                ("Dzuhur", self.dzuhur, True),
                ("Ashar", self.ashar, True),
                ("Maghrib", self.maghrib, True),
                ("Isya\'", self.isya, True)]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        embed.set_author(name="Prayer Reminder", icon_url="http://amaliyah.net/wp-content/uploads/2021/03/Shahada-Salat-Calligraphy.png")
        embed.set_footer(text=f"Timezone: {self.timezone}\nDate: {self.tanggal}")
        await ctx.send(embed=embed)

    @command(name="shalat.jadwalkan", aliases=["jadwalkanShalat"])
    async def jadwalkan_shalat(self, ctx, kota="Yogyakarta", negara="Indonesia", metode=3, lama=7):
        """Memberitahu jadwal shalat secara rutin selama jangka waktu tertentu"""
        self.kota = kota
        self.negara = negara
        self.url = requests.request("GET",f"http://api.aladhan.com/v1/timingsByCity?city={kota}&country={negara}&method={metode}")
        self.waktu_shalat = json.loads(self.url.text)
        self.subuh = self.waktu_shalat['data']['timings']['Fajr']
        self.terbit = self.waktu_shalat['data']['timings']['Sunrise']
        self.dzuhur = self.waktu_shalat['data']['timings']['Dhuhr']
        self.ashar = self.waktu_shalat['data']['timings']['Asr']
        self.maghrib = self.waktu_shalat['data']['timings']['Maghrib']
        self.isya = self.waktu_shalat['data']['timings']['Isha']
        self.timezone = self.waktu_shalat['data']['meta']['timezone']
        self.tanggal = self.waktu_shalat['data']['date']['readable']
        self.scheduler = AsyncIOScheduler()

        async def subuh_reminder():
            embed = Embed(title='Waktu Shalat!', description=f'Untuk wilayah {self.kota}, {self.negara}.', colour=0xFF2400)
            embed.add_field(name="Subuh", value=self.subuh)
            embed.set_author(name="Prayer Reminder", icon_url="http://amaliyah.net/wp-content/uploads/2021/03/Shahada-Salat-Calligraphy.png")
            embed.set_footer(text=f"Timezone: {self.timezone}\nDate: {self.tanggal}")
            await ctx.send(embed=embed)
        
        async def terbit_reminder():
            embed = Embed(title='Waktu Shalat!', description=f'Untuk wilayah {self.kota}, {self.negara}.', colour=0xFF2400)
            embed.add_field(name="Terbit", value=self.terbit)
            embed.set_author(name="Prayer Reminder", icon_url="http://amaliyah.net/wp-content/uploads/2021/03/Shahada-Salat-Calligraphy.png")
            embed.set_footer(text=f"Timezone: {self.timezone}\nDate: {self.tanggal}")
            await ctx.send(embed=embed)

        async def dzuhur_reminder():
            embed = Embed(title='Waktu Shalat!', description=f'Untuk wilayah {self.kota}, {self.negara}.', colour=0xFF2400)
            embed.add_field(name="Dzuhur", value=self.dzuhur)
            embed.set_author(name="Prayer Reminder", icon_url="http://amaliyah.net/wp-content/uploads/2021/03/Shahada-Salat-Calligraphy.png")
            embed.set_footer(text=f"Timezone: {self.timezone}\nDate: {self.tanggal}")
            await ctx.send(embed=embed)

        async def ashar_reminder():
            embed = Embed(title='Waktu Shalat!', description=f'Untuk wilayah {self.kota}, {self.negara}.', colour=0xFF2400)
            embed.add_field(name="Ashar", value=self.ashar)
            embed.set_author(name="Prayer Reminder", icon_url="http://amaliyah.net/wp-content/uploads/2021/03/Shahada-Salat-Calligraphy.png")
            embed.set_footer(text=f"Timezone: {self.timezone}\nDate: {self.tanggal}")
            await ctx.send(embed=embed)

        async def maghrib_reminder():
            embed = Embed(title='Waktu Shalat!', description=f'Untuk wilayah {self.kota}, {self.negara}.', colour=0xFF2400)
            embed.add_field(name="Maghrib", value=self.maghrib)
            embed.set_author(name="Prayer Reminder", icon_url="http://amaliyah.net/wp-content/uploads/2021/03/Shahada-Salat-Calligraphy.png")
            embed.set_footer(text=f"Timezone: {self.timezone}\nDate: {self.tanggal}")
            await ctx.send(embed=embed)

        async def isya_reminder():
            embed = Embed(title='Waktu Shalat!', description=f'Untuk wilayah {self.kota}, {self.negara}.', colour=0xFF2400)
            embed.add_field(name="Isya\'", value=self.isya)
            embed.set_author(name="Prayer Reminder", icon_url="http://amaliyah.net/wp-content/uploads/2021/03/Shahada-Salat-Calligraphy.png")
            embed.set_footer(text=f"Timezone: {self.timezone}\nDate: {self.tanggal}")
            await ctx.send(embed=embed)

        self.scheduler.add_job(subuh_reminder, CronTrigger(hour=int(self.subuh[0:2]), minute=int(self.subuh[3:]), end_date=datetime.datetime.now() + datetime.timedelta(days=lama), timezone=self.timezone), id="jadwal_subuh")
        self.scheduler.add_job(terbit_reminder, CronTrigger(hour=int(self.terbit[0:2]), minute=int(self.terbit[3:]), end_date=datetime.datetime.now() + datetime.timedelta(days=lama), timezone=self.timezone), id="jadwal_terbit")
        self.scheduler.add_job(dzuhur_reminder, CronTrigger(hour=int(self.dzuhur[0:2]), minute=int(self.dzuhur[3:]), end_date=datetime.datetime.now() + datetime.timedelta(days=lama), timezone=self.timezone), id="jadwal_dzuhur")
        self.scheduler.add_job(ashar_reminder, CronTrigger(hour=int(self.ashar[0:2]), minute=int(self.ashar[3:]), end_date=datetime.datetime.now() + datetime.timedelta(days=lama), timezone=self.timezone), id="jadwal_ashar")
        self.scheduler.add_job(maghrib_reminder, CronTrigger(hour=int(self.maghrib[0:2]), minute=int(self.maghrib[3:]), end_date=datetime.datetime.now() + datetime.timedelta(days=lama), timezone=self.timezone), id="jadwal_maghrib")
        self.scheduler.add_job(isya_reminder, CronTrigger(hour=int(self.isya[0:2]), minute=int(self.isya[3:]), end_date=datetime.datetime.now() + datetime.timedelta(days=lama), timezone=self.timezone), id="jadwal_isya")
        self.scheduler.start()
        await ctx.send("Shalat sudah terjadwalkan!")

    @command(name="quran")
    async def cari_quran(self, ctx, ayat):
        self.url1 = requests.get(f"http://api.alquran.cloud/v1/ayah/{ayat}")
        self.url2 = requests.get(f"http://api.alquran.cloud/v1/ayah/{ayat}/id.indonesian")
        self.parse1 = json.loads(self.url1.text)
        self.parse2 = json.loads(self.url2.text)
        self.arab = self.parse1['data']['text']
        self.terjemah = self.parse2['data']['text']
        self.surat = self.parse2['data']['surah']['englishName']
        self.nomorAyat = self.parse2['data']['numberInSurah']
        self.juz = self.parse2['data']['juz']
        self.halaman = self.parse2['data']['page']

        embed = Embed(title="Pencarian Qur'an!", colour=ctx.author.colour)
        embed.add_field(name="Allah berfirman:", value=self.arab, inline=False)
        embed.add_field(name="Artinya:", value=self.terjemah, inline=False)
        embed.set_author(name="Al-Qur'an Al-Karim", icon_url="https://i.pinimg.com/originals/e8/be/31/e8be31140445890de831cc2a3a6e590b.jpg")
        embed.set_footer(text=f"Surah: {self.surat}:{self.nomorAyat}\nJuz: {self.juz} | Halaman: {self.halaman}")
        await ctx.send(embed=embed)


    @slash_command(name="quran-cari", description="Mengembalikan output berupa ayat dan terjemahan dari surat", guild_ids=db.guild_list)
    async def cari_ayat(
        self, 
        ctx, 
        ayat : Option(str, 'Surat dan ayat yang ingin dicari, format : (surat:ayat)')
        ):
        self.url1 = requests.get(f"http://api.alquran.cloud/v1/ayah/{ayat}")
        self.url2 = requests.get(f"http://api.alquran.cloud/v1/ayah/{ayat}/id.indonesian")
        self.parse1 = json.loads(self.url1.text)
        self.parse2 = json.loads(self.url2.text)
        self.arab = self.parse1['data']['text']
        self.terjemah = self.parse2['data']['text']
        self.surat = self.parse2['data']['surah']['englishName']
        self.nomorAyat = self.parse2['data']['numberInSurah']
        self.juz = self.parse2['data']['juz']
        self.halaman = self.parse2['data']['page']

        embed = Embed(title="Pencarian Qur'an!", colour=ctx.author.colour)
        embed.add_field(name="Allah berfirman:", value=self.arab, inline=False)
        embed.add_field(name="Artinya:", value=self.terjemah, inline=False)
        embed.set_author(name="Al-Qur'an Al-Karim", icon_url="https://i.pinimg.com/originals/e8/be/31/e8be31140445890de831cc2a3a6e590b.jpg")
        embed.set_footer(text=f"Surah: {self.surat}:{self.nomorAyat}\nJuz: {self.juz} | Halaman: {self.halaman}")
        await ctx.send(embed=embed)

    async def quran_acak(self):
        randomizer = random.randint(1, 6236)
        self.url1 = requests.get(f"http://api.alquran.cloud/v1/ayah/{randomizer}")
        self.url2 = requests.get(f"http://api.alquran.cloud/v1/ayah/{randomizer}/id.indonesian")
        self.parse1 = json.loads(self.url1.text)
        self.parse2 = json.loads(self.url2.text)
        self.arab = self.parse1['data']['text']
        self.terjemah = self.parse2['data']['text']
        self.surat = self.parse2['data']['surah']['englishName']
        self.nomorAyat = self.parse2['data']['numberInSurah']
        self.juz = self.parse2['data']['juz']
        self.halaman = self.parse2['data']['page']

        embed = Embed(title="Qur'an of the Day!", colour=0xFF2400)
        embed.add_field(name="Allah berfirman:", value=self.arab, inline=False)
        embed.add_field(name="Artinya:", value=self.terjemah, inline=False)
        embed.set_author(name="Al-Qur'an Al-Karim", icon_url="https://i.pinimg.com/originals/e8/be/31/e8be31140445890de831cc2a3a6e590b.jpg")
        embed.set_footer(text=f"Surah: {self.surat}:{self.nomorAyat}\nJuz: {self.juz} | Halaman: {self.halaman}")
        for j in db.servers_con.servers.server.find():
            try:
                channel = self.bot.get_channel(j['quran_channel']['id'])
                await channel.send(embed=embed)
            except Exception as e:
                print(e)
                
    @Cog.listener()
    async def on_ready(self):
        await self.jadwal_shalat_rutin()

def setup(bot):
    bot.add_cog(Agama(bot))