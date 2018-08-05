from selenium import webdriver
from pyvirtualdisplay import Display
import time
import os
import socket
import numpy as np
import re
import traceback
import sys

# serverHost = '35.228.171.127'
serverHost = sys.argv[1]
serverPort = 8698
serverAddr = (serverHost, serverPort)
serverDomain = 'tang123456.net'

# host = '10.166.0.3'
host = sys.argv[2]
port = 8698

user_dir = '/home/cooperate/quic-cmp/'
os.system('iperf3 -sD')

def get_max(a, b):
	if a > b:
		return a
	else:
		return b

def ping(target='localhost', host=80):
	cmd = 'sudo hping3 -S -p %d -c 3 %s' % (host, target)
	lines = os.popen(cmd).read().split('\n')
	data = []
	for line in lines:
		search = re.search('rtt=([0123456789.]+) ms', line)
		if search:
			data.append(float(search.group(1)))
	return data

if __name__ == '__main__':
	result = open(user_dir + 'new_results.txt', 'w')
	os.system('sudo yum remove -y google-chrome')
	os.system('sudo rpm -ivh google-chrome-stable_current_x86_64_63.0.3239.84.rpm')
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client.bind((host, port))
	client.listen(3)

	ping_result = ping(serverHost, serverPort)
	print('ping result: %s' % ping_result)
	result.write('ping result: %s \n' % ping_result)

	while True:
		clientConn, sAddr = client.accept()
		break

	while 1:
		data = clientConn.recv(1024)
		print data
		if not data.startswith('Server ready:'): continue
		display = Display(visible=0, size=(800,600))
		display.start()
		url = data.split(':')[1].strip()
		driverOptions = webdriver.ChromeOptions()
		driverOptions.add_argument('--load-extension=' + user_dir + 'mypagetest')
		driverOptions.add_argument('--no-proxy-server')
		driverOptions.add_argument('--disable-application-cache')
		driverOptions.add_argument('--aggressive-cache-discard')
		driverOptions.add_argument('--disable-reading-from-canvas')
		driverOptions.add_argument('--enable-aggressive-domstorage-flushing')
		driverOptions.add_argument('--no-sandbox')
		driverOptions.add_argument('--new-window')
		if url.endswith('quic'):
			driverOptions.add_argument('--enable-quic')
			driverOptions.add_argument('--quic-host-whitelist=' + '"' + serverDomain + '"')
			driverOptions.add_argument('--origin-to-force-quic-on=' + serverDomain + ':443')
			driverOptions.add_argument('--quic-version=' + 'QUIC_VERSION_39')
		loadtime_list = []
		test_times = 0
		sum_times = 0
		while sum_times < 10:
			wait_time = 5
			flag = False
			while wait_time < 30:
				if flag: break
				try:
					if os.path.exists('/home/cooperate/Downloads/loadtime.txt'):
						os.remove('/home/cooperate/Downloads/loadtime.txt')
					browser = webdriver.Chrome(user_dir + "chromedriver", chrome_options=driverOptions)
					browser.get("https://" + serverDomain)
					time.sleep(wait_time)
					loadtime_file = open('/home/cooperate/Downloads/loadtime.txt', 'r')
					loadtime_str = loadtime_file.readline().strip(' ')[3:]
					if test_times == 0: conn_time_str = loadtime_str.split(' ')[1]
					loadtime_str = loadtime_str.split(' ')[0]
					loadtime = float(loadtime_str)
					loadtime_list.append(loadtime)
					os.remove('/home/cooperate/Downloads/loadtime.txt')
					browser.quit()
					sync_command = 'sync'
					os.system(sync_command)
					free_m_command = "sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'"
					os.system(free_m_command)
					flag = True
				except Exception as e:
					traceback.print_exc()
					wait_time += 10
					print wait_time
					browser.quit()
					sync_command = 'sync'
					os.system(sync_command)
					free_m_command = "sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'"
					os.system(free_m_command)
					browser = webdriver.Chrome(user_dir + "chromedriver", chrome_options=driverOptions)
			if wait_time < 30: test_times += 1
			if test_times == 5: break
			sum_times += 1
		if test_times == 5:
			temp = ''
			print url
			loadtime_list.sort()
			temp = temp + url + ',' + str(loadtime_list[2]) + ',' + conn_time_str + '\n'
			result.write(temp)
			result.flush()
		print 'client completed!'
		clientConn.send('client completed!')
		browser.quit()
		display.stop()

