from pyclbr import Function
from pymongo import MongoClient
import os
#mongoDB server connection
SERVER_PASSWORD = os.getenv('SERVER_PASSWORD')
CONNECTION_STRING_SISWA = f"mongodb+srv://runs:{SERVER_PASSWORD}@botgabutcluster.14awb.mongodb.net/siswa?retryWrites=true&w=majority"
siswa_con = MongoClient(CONNECTION_STRING_SISWA)
CONNECTION_STRING_SERVERS = f"mongodb+srv://runs:{SERVER_PASSWORD}@botgabutcluster.14awb.mongodb.net/servers?retryWrites=true&w=majority"
servers_con = MongoClient(CONNECTION_STRING_SERVERS)
CONNECTION_STRING_OTHERS = f"mongodb+srv://runs:{SERVER_PASSWORD}@botgabutcluster.14awb.mongodb.net/others?retryWrites=true&w=majority"
others_con = MongoClient(CONNECTION_STRING_OTHERS)
version = 'v2.3.8'

guild_list = [i['server_id'] for i in servers_con['servers']['server'].find()]

# --------------
#  EXP FUNCTION
# --------------

def exp_factor(level):
    return int(60 * level + ((level ** 3.8) * (1 - (0.99 ** level))))

def cur_exp(xp):
    level = 0
    exp = xp
    while exp > (exp_factor(level + 1) - exp_factor(level)):
        level += 1
        exp -= (exp_factor(level + 1) - exp_factor(level))
    return (int(exp), level)

def number_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T', 'P'][magnitude])

def add_exp(discord_id, exp):
    if servers_con['servers']['social_credit'].find({'discord_id' : discord_id}) != None:
        current_exp = servers_con['servers']['social_credit'].find({'discord_id' : discord_id})[0]['u_exp'] + exp
        current_level = servers_con['servers']['social_credit'].find({'discord_id' : discord_id})[0]['u_level']
        servers_con['servers']['social_credit'].update_one({'discord_id' : discord_id}, {"$set": {'u_exp': current_exp}})
    else:
        current_level = 0
        current_exp = exp
        servers_con['servers']['social_credit'].insert_one({'discord_id' : discord_id,
                                                                'v_exp'      : 0, 
                                                                'v_time'     : 0,
                                                                'v_level'    : 0,
                                                                't_exp'      : 0,
                                                                't_time'     : 0,
                                                                't_level'    : 0,
                                                                'v_violation': 0,
                                                                't_violation': 0,
                                                                'n_violation': 0})

    
    level = cur_exp(current_exp)[1]
        
    if current_level < level:
        servers_con['servers']['social_credit'].update_one({'discord_id' : discord_id}, {"$set": {'u_level': level}})
        
    elif level < current_level:
        servers_con['servers']['social_credit'].update_one({'discord_id' : discord_id}, {"$set": {'u_level': level}})
        
def number_format(self, num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T', 'P'][magnitude])