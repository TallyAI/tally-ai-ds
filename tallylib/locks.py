## tallylib/locks.py
from datetime import datetime


class LockYelpScraper():
    def __init__(self):
        self.list = dict()

    def lockBusinessID(self, business_id, 
                             timeout=1200): # seconds
        self.list[business_id] = {'timestamp':datetime.now(), 
                                  'timeout':timeout}

    def unlockBusinessID(self, business_id):
        try:
            del self.list[business_id]
        except:
            pass

    def isLocked(self, business_id):
        try: 
            if (datetime.now() - self.list[business_id]['timestamp']).seconds < self.list[business_id]['timeout']:
                return True
            else:
                return False
        except:
            return False


# this object runs in a thread inside the application process
lock_yelpscraper = LockYelpScraper()
