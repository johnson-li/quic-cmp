from selenium import webdriver
from pyvirtualdisplay import Display
import time
import os
import socket
import numpy as np
import re
import traceback
import sys
import collections
from selenium.webdriver.common.keys import Keys
import textwrap

# serverHost = '35.228.171.127'
serverHost = sys.argv[1]
serverPort = 8698
serverAddr = (serverHost, serverPort)
serverDomain = sys.argv[3]

# host = '10.166.0.3'
host = sys.argv[2]
port = 8698

user_dir = '/home/cooperate/quic-cmp/'
os.system('iperf3 -sD')

class PageLoadTimer:
    def __init__(self, driver):
        """
            takes:
                'driver': webdriver instance from selenium.
        """
        self.driver = driver

        self.jscript = textwrap.dedent("""
            var performance = window.performance || {};
            var timings = performance.timing || {};
            return timings;
            """)
        self.flushscript = textwrap.dedent("""
            chrome.send('flushSocketPools');
        """)

    def inject_timing_js(self):
        timings = self.driver.execute_script(self.jscript)
        return timings

    def inject_socket_flush_js(self):
        self.driver.execute_script(self.flushscript)

    def get_event_times(self):
        timings = self.inject_timing_js()
        # the W3C Navigation Timing spec guarantees a monotonic clock:
        #  "The difference between any two chronologically recorded timing
        #   attributes must never be negative. For all navigations, including
        #   subdocument navigations, the user agent must record the system
        #   clock at the beginning of the root document navigation and define
        #   subsequent timing attributes in terms of a monotonic clock
        #   measuring time elapsed from the beginning of the navigation."
        # However, some navigation events produce a value of 0 when unable to
        # retrieve a timestamp.  We filter those out here:
        good_values = [epoch for epoch in timings.values() if epoch != 0]
        # rather than time since epoch, we care about elapsed time since first
        # sample was reported until event time.  Since the dict we received was
        # inherently unordered, we order things here, according to W3C spec
        # fields.
        ordered_events = ('navigationStart', 'redirectStart', 'fetchStart', 'domainLookupStart',
                          'domainLookupEnd', 'connectStart', 'connectEnd',
                          'secureConnectionStart', 'requestStart',
                          'responseStart', 'responseEnd', 'domLoading',
                          'domInteractive', 'domContentLoadedEventStart',
                          'domContentLoadedEventEnd', 'domComplete',
                          'loadEventStart', 'loadEventEnd'
                          )
        event_times = collections.OrderedDict()
        for event in ordered_events:
            if event in timings:
                if timings[event] == 0:
                    event_times[event] = 0
                else:
                    event_times[event] = timings[event] - min(good_values)
        return event_times

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
		driverOptions.add_argument('--no-proxy-server')
		driverOptions.add_argument('--disable-application-cache')
		driverOptions.add_argument('--aggressive-cache-discard')
		driverOptions.add_argument('--disable-reading-from-canvas')
		driverOptions.add_argument('--enable-aggressive-domstorage-flushing')
		driverOptions.add_argument('--no-sandbox')
		driverOptions.add_argument('--new-window')
		driverOptions.add_experimental_option("prefs", {'profile.managed_default_content_settings.javascript': 2})

		if url.endswith('quic'):
			driverOptions.add_argument('--enable-quic')
			driverOptions.add_argument('--quic-host-whitelist=' + '"' + serverDomain + '"')
			driverOptions.add_argument('--origin-to-force-quic-on=' + serverDomain + ':443')
			driverOptions.add_argument('--quic-version=' + 'QUIC_VERSION_39')
		loadtime_list = []
		test_times = 0
		sum_times = 0
		result.write(url + '\n')
		while sum_times < 10:
			flag = False
			try:
				flush_url = 'chrome://net-internals/#sockets'
				browser = webdriver.Chrome(user_dir + "chromedriver", chrome_options=driverOptions)
				browser.get(flush_url)
				time.sleep(3)
				driver.find_element_by_id('sockets-view-close-idle-button').send_keys(Keys.ENTER)
				driver.find_element_by_id('sockets-view-close-idle-button').send_keys(Keys.ENTER)
				driver.find_element_by_id('sockets-view-flush-button').send_keys(Keys.ENTER)
				driver.find_element_by_id('sockets-view-flush-button').send_keys(Keys.ENTER)
				browser.get("https://" + serverDomain)
				timer = PageLoadTimer(driver)
    			time_dict = timer.get_event_times()
    			if time_dict['redirectStart'] == 0:
				 	start = time_dict['fetchStart']
				else:
					start = time_dict['redirectStart']
				plt = time_dict['loadEventEnd'] - start
				browser.quit()
				sync_command = 'sync'
				os.system(sync_command)
				free_m_command = "sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'"
				os.system(free_m_command)
				flag = True
				result.write(str(plt) + '\n')
				result.write(str(time_dict))
				result.write('\n')
			except Exception as e:
				traceback.print_exc()
				browser.quit()
				sync_command = 'sync'
				os.system(sync_command)
				free_m_command = "sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'"
				os.system(free_m_command)
			if flag: test_times += 1
			sum_times += 1
		if test_times == 5:
			result.write('success! \n')
		result.flush()
		print 'client completed!'
		clientConn.send('client completed!')
		display.stop()

