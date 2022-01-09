from pymongo import MongoClient
import os
#mongoDB server connection
SERVER_PASSWORD = os.getenv('SERVER_PASSWORD')
CONNECTION_STRING_SISWA = f"mongodb+srv://runs:{SERVER_PASSWORD}@botgabutcluster.14awb.mongodb.net/siswa?retryWrites=true&w=majority"
siswa_con = MongoClient(CONNECTION_STRING_SISWA)
CONNECTION_STRING_SERVERS = f"mongodb+srv://runs:{SERVER_PASSWORD}@botgabutcluster.14awb.mongodb.net/servers?retryWrites=true&w=majority"
servers_con = MongoClient(CONNECTION_STRING_SERVERS)

guild_list = [i['server_id'] for i in servers_con['servers']['server'].find()]