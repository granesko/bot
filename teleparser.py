# -*- coding: utf-8 -*-


class TG:
	def __init__(self, app_name, api_id, api_hash, phone_number, proxy, port, username, password):
		import socks
		from telethon import TelegramClient, sync

		try:
			if (proxy is not None) & (port is not None):
				try:
					port = int(port)
				except ValueError:
					print('Wrong port')
					exit()

				self.client = TelegramClient(app_name, api_id, api_hash, proxy={'proxy_type': socks.SOCKS5,
												'addr': proxy, 'port': port,
												'username': username,
												'password': password})
			else:
				self.client = TelegramClient(app_name, api_id, api_hash)
			self.client.connect()
			if not self.client.is_user_authorized():
				self.client.send_code_request(phone_number)
				self.client.sign_in(phone_number, input('Enter code:'))
		except OSError:
			print('Connection error')
			exit()

	def get_group_info(self, group_link):
		from telethon.tl.functions.channels import GetFullChannelRequest

		title = self.client.get_entity(group_link).title
		group = self.client(GetFullChannelRequest(group_link))
		count_users = group.full_chat.participants_count
		about = group.full_chat.about

		return {'g_title': title, 'g_link': group_link, 'g_count': count_users, 'g_about': about}

	def get_user_list(self, group_link, count_users):
		from telethon.tl.functions.channels import GetParticipantsRequest
		from telethon.tl.types import ChannelParticipantsSearch
		from telethon.tl.functions.users import GetFullUserRequest
		import time

		my_offset = 0
		u_list = []
		u_row = {}
		for i in range(count_users // 200 + 1):
			# get part of user list (request limit - 200)
			part = self.client(GetParticipantsRequest(channel=group_link, filter=ChannelParticipantsSearch(''),
													  offset=my_offset, limit=200, hash=0))
			if (count_users - my_offset) - 200 > 0:
				delta = 200
			else:
				delta = count_users - my_offset
			for j in range(delta):
				try:
					u_row['u_id'] = part.users[j].id
				except IndexError:
					continue

				# get name
				u_row['u_firstname'] = ''
				u_row['u_lasname'] = ''
				try:
					u_row['u_firstname'] = part.users[j].first_name
				except TypeError:
					pass
				try:
					u_row['u_lastname'] = part.users[j].last_name
				except TypeError:
					pass

				# get login
				try:
					u_row['u_login'] = '@' + part.users[j].username
				except TypeError:
					u_row['u_login'] = 'None'

				# get status
				try:
					if part.participants[j].admin_rights.add_admins:
						u_row['u_status'] = 'admin'
					else:
						u_row['u_status'] = 'moderator'
				except AttributeError:
					u_row['u_status'] = 'user'

				# get last seen
				if str(part.users[j].status) == 'UserStatusRecently()':
					u_row['u_active'] = 'Last seen recently'
				elif str(part.users[j].status) == 'UserStatusLastWeek()':
					u_row['u_active'] = 'Last seen within a week'
				elif str(part.users[j].status) == 'UserStatusLastMonth()':
					u_row['u_active'] = 'Last seen within a month'
				else:
					u_row['u_active'] = 'None'

				# get user bio
				u_row['u_about'] = self.client(GetFullUserRequest(u_row['u_id'])).about

				# get user photo
				#time.sleep(4)
				#self.client.download_profile_photo(u_row['u_id'], r'images/{0}.jpg'.format(u_row['u_id']))

				u_list.append(u_row)
				u_row = {}
			my_offset += 200

		return u_list


def wr_xlsx(g_info, u_info):
	import xlsxwriter
	import os
	import sys
	import random
	from PIL import Image
	from datetime import date

	wb = xlsxwriter.Workbook('result_{}.xlsx'.format(random.randint(1, 10000000)),options={'strings_to_urls': False,
																							'strings_to_formulas': False})
	ws = wb.add_worksheet()

	ws.write('A1', 'Group title')
	ws.write('A2', g_info['g_title'])
	ws.write('B1', 'Group link')
	ws.write_url('B2', g_info['g_link'])
	ws.write('C1', 'Member count')
	ws.write('C2', g_info['g_count'])
	ws.write('D1', 'About group')
	ws.write('D2', g_info['g_about'])
	ws.write('E1', 'Parsing date')
	ws.write_datetime('E2', date.today())

	ws.write(3, 0, 'Avatar')
	ws.write(3, 1, 'First Name')
	ws.write(3, 2, 'Last Name')
	ws.write(3, 3, 'Profile link')
	ws.write(3, 4, 'Status')
	ws.write(3, 5, 'Bio')
	ws.write(3, 6, 'ID')
	ws.write(3, 7, 'Last seen')

	

	ws.set_column(0, 0, 12)		# just setting column width
	row = 4
	for i in u_info:
		ws.set_row(row, 70)		# just setting row height

	   #

		ws.write(row, 1, i['u_firstname'])
		ws.write(row, 2, i['u_lastname'])
		ws.write(row, 3, i['u_login'])
		ws.write(row, 4, i['u_status'])
		ws.write(row, 5, i['u_about'])
		ws.write(row, 6, i['u_id'])
		ws.write(row, 7, i['u_active'])

		row += 1

	wb.close()

   


def main():
	import sys

	auth = {}
	with open('auth') as file:
		for line in file:
			try:
				print(line)
				key, *value = line.split()
			except ValueError:
				print('Incorrect auth file')
				exit()
			try:
				auth[key] = value[0]
			except IndexError:
				auth[key] = None

	client_session = TG('teleparser', int(auth['app_id']), auth['app_hash'], auth['phone'], auth['proxy'],
						auth['port'], auth['username'], auth['password'])
	g_info = client_session.get_group_info(sys.argv[1])
	u_info = client_session.get_user_list(sys.argv[1], g_info['g_count'])
	wr_xlsx(g_info, u_info)
	client_session.client.disconnect()


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		exit()
