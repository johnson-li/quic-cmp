# -*- coding: utf-8 -*-
import urllib, urllib2
import Cookie
import json
import time
import datetime
from datetime import timedelta
import os
import requests
from bs4 import BeautifulSoup
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import collections
from selenium.webdriver.common.keys import Keys
import textwrap

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
        ordered_events = ('navigationStart', 'fetchStart', 'domainLookupStart',
                          'domainLookupEnd', 'connectStart', 'connectEnd',
                          'secureConnectionStart', 'requestStart',
                          'responseStart', 'responseEnd', 'domLoading',
                          'domInteractive', 'domContentLoadedEventStart',
                          'domContentLoadedEventEnd', 'domComplete',
                          'loadEventStart', 'loadEventEnd'
                          )
        event_times = ((event, timings[event] - min(good_values)) for event
                       in ordered_events if event in timings)
        return collections.OrderedDict(event_times)


if __name__ == '__main__':
    url = 'https://www.jd.com'
    flush_url = 'chrome://net-internals/#sockets'
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {'profile.managed_default_content_settings.javascript': 2})
    driver = webdriver.Chrome('chromedriver', chrome_options=chrome_options)
    driver.get(url)
    time.sleep(3)
    driver.get(flush_url)
    time.sleep(5)
    print driver.find_element_by_id('sockets-view-flush-button').get_attribute("value")
    # driver.find_element_by_id('sockets-view-close-idle-button').click()
    # flush = PageLoadTimer(driver)
    # flush.inject_socket_flush_js()
    driver.find_element_by_id('sockets-view-flush-button').send_keys(Keys.ENTER)
    driver.find_element_by_id('sockets-view-flush-button').send_keys(Keys.ENTER)
    # driver.get(url)
    # timer = PageLoadTimer(driver)
    # print timer.get_event_times()

