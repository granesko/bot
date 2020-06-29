from telethon import TelegramClient, events, sync
from telethon import utils
import argparse
import sys
from telethon.tl.types import PeerUser, PeerChat, PeerChannel

if __name__ == '__main__':

    api_id = *
    api_hash = '*'
    client = TelegramClient('session_name', api_id, api_hash)
    client.start()
    """
    my_name = utils.get_display_name(client.get_me())
    msg = 'test'
    id_client = 1220038
    id_client1 = client.get_entity(386520922)
    client.send_message(id_client1, msg)
    """

    users = client.get_participants('t.me/joinchat/*')
    print(users[0],'\n')
    print(users[1],'\n')
    print(users[2],'\n')
    """
    for user in users:
        if user.username is not None:
            print(user.username,user.first_name,'\n')
    """
    my_name = utils.get_display_name(client.get_me())
    msg = 'test'
    id_client = 386520922
    client.send_message(id_client, msg)
