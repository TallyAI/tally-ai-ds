# tallylib/proxy.py
import os
import time
import random
import requests
from django.conf import settings


# 2020-01-22 https://luminati.io/
# For now it is using data center IPs for lower cost
class ProxyList():
    def __init__(self, num=None, start=0):
        self.url = ""
        self.list = []
        self.getProxyList(num=num)

    def getProxyList(self, num=None, start=0):
        if num:
            if num<0 or num>20000:
                return
        if settings.URL_PROXY_LIST is None \
            or len(settings.URL_PROXY_LIST) == 0:
            return
        self.url = settings.URL_PROXY_LIST
        for _ in range(5): # try 5 times if failed
            try:
                response = requests.get(self.url, timeout=5)
                if response.status_code != 200:
                    time.sleep(1)
                else:
                    txt = response.text
                    self.list = txt.split('\n')
                    # tailor the list to the required part
                    if num:
                        self.list = self.list[start:start+num]
                    # start from random position of the list
                    idx = random.randint(1, len(self.list)-1)
                    self.list = self.list[idx:] + self.list[:idx]
                    print(f"Retrieved {len(self.list)} IPs from the proxy list.")
                    break
            except:
                self.list = []
                print("Failed to retrieve proxy IP list.")
                raise

    def getProxy(self):
        # <host>:<port>:<username>:<password>
        p = self.list[0].split(':')
        # http://<username>:<password>@<host>:<port>
        p = f"http://{p[2]}:{p[3]}@{p[0]}:{p[1]}"
        proxy = dict()
        proxy['http'] = p
        proxy['https'] = p
        # rotate the list
        self.list = self.list[1:] + self.list[:1]

        return proxy

    def removeProxy(self): # Not in use for the data center IP list
        self.list = self.list[:-1]
        

# this object runs in a thread inside the application process
proxylist = ProxyList()
