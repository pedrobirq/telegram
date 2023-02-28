#!/bin/env python3
from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerUser
from telethon.errors.rpcerrorlist import PeerFloodError
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel
import configparser
import os, sys
import csv
import random
import time

re="\033[1;31m"
gr="\033[1;32m"
cy="\033[1;36m"
SLEEP_TIME = int(input("Введите интервал в секундах между сообщениями "))

class main():

    def banner():
        
        print("ОТПРАВКА СООБЩЕНИЙ")

    def send_sms():
        try:
            cpass = configparser.RawConfigParser()
            cpass.read('config.data')
            api_id = cpass['cred']['id']
            api_hash = cpass['cred']['hash']
            phone = cpass['cred']['phone']
        except KeyError:
            os.system('clear')
            main.banner()
            print(re+"[!] run python3 setup.py first !!\n")
            sys.exit(1)

        client = TelegramClient(phone, api_id, api_hash)
         
        client.connect()
        if not client.is_user_authorized():
            client.send_code_request(phone)
            os.system('clear')
            main.banner()
            client.sign_in(phone, input(gr+'[+] Enter the code: '+re))
        
        os.system('clear')
        main.banner()
        input_file = sys.argv[1]
        users = []
        with open(input_file, encoding='UTF-8') as f:
            rows = csv.reader(f,delimiter=",",lineterminator="\n")
            next(rows, None)
            for row in rows:
                user = {}
                user['username'] = row[0]
                user['id'] = int(row[1])
                user['access_hash'] = int(row[2])
                user['name'] = row[3]
                users.append(user)
        #print(gr+"[1] send sms by user ID\n[2] send sms by username ")
        mode = 1
         
        #message = input(gr+"[+] Enter Your Message : "+re)

        offset_id = 0
        limit = 100
        all_messages = []
        total_messages = 0
        total_count_limit = 0

        while True:
            history = client(GetHistoryRequest(
                peer='me',
                offset_id=offset_id,
                offset_date=None,
                add_offset=0,
                limit=limit,
                max_id=0,
                min_id=0,
                hash=0
            ))
            if not history.messages:
                break
            messages = history.messages
            for message in messages:
                all_messages.append(message.message)
            offset_id = messages[len(messages) - 1].id
            if total_count_limit != 0 and total_messages >= total_count_limit:
                break
        message = ''
        for mesag in all_messages:
            message += str(mesag)
         
        for user in users:
            if mode == 2:
                if user['username'] == "":
                    continue
                receiver = client.get_input_entity(user['username'])
            elif mode == 1:
                receiver = InputPeerUser(user['id'],user['access_hash'])
            else:
                print(re+"[!] Invalid Mode. Exiting.")
                client.disconnect()
                sys.exit()
            try:
                print(gr+"[+] Sending Message to:", user['name'])
                client.send_message(receiver, message.format(user['name']))
                print(gr+"[+] Waiting {} seconds".format(SLEEP_TIME))
                time.sleep(SLEEP_TIME)
            except PeerFloodError:
                print(re+"[!] Getting Flood Error from telegram. \n[!] Script is stopping now. \n[!] Please try again after some time.")
                client.disconnect()
                sys.exit()
            except Exception as e:
                print(re+"[!] Error:", e)
                print(re+"[!] Trying to continue...")
                continue
        client.disconnect()
        print("Done. Message sent to all users.")



main.send_sms()
