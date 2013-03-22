#!/usr/bin/env python
import time
import urllib
import json
import threading
from .xmpp import RetconXMPP
from flask import current_app

config = current_app.config

ALL = 0
WARNING = 1
CRITICAL = 2

def pluralise(seq):
    if len(seq) == 1:
        return ''
    return 's'

class BaseNotification(object):

    description = 'BaseNotification'
    notify_threshold = ALL

    def __init__(self):
        self.last_sent_time = None
        self.sent_count = 0

    def sent(self):
        self.last_sent_time = time.time()
        self.sent_count += 1

    def handle_issue_change(self, issues):
        raise NotImplementedError

    def send_message(self, message):
        raise NotImplementedError


class Kapow(BaseNotification):

    description = 'Kapow SMS'
    notify_threshold = CRITICAL

    def __init__(self, number):
        BaseNotification.__init__(self)
        self.number = number

    def send_message(self, message):
        urllib.urlopen(
        'https://www.kapow.co.uk/scripts/sendsms.php',
        urllib.urlencode({
            'username' : config['KAPOW_USERNAME'],
            'password' : config['KAPOW_PASSWORD'],
            'mobile' : self.number,
            'sms' : message
        }))
        self.sent()

    def handle_issue_change(self, issues):
        if len(issues):
            msg = 'Alert: %d issue%s' % (len(issues), pluralise(issues))
            self.send_message(msg)


class Prowl(BaseNotification):

    description = 'Prowl'
    notify_threshold = CRITICAL

    def __init__(self, apikey):
        BaseNotification.__init__(self)
        self.apikey = apikey

    def send_message(self, message, description=None, priority=2):
        urllib.urlopen(
        'https://prowl.weks.net/publicapi/add',
        urllib.urlencode({
            'apikey' : self.apikey,
            'application' : 'Retcon',
            'event' : message,
            'priority' : priority,
            'description' : description or 'Follow up at %s' % config['RETCON_URL'],
        }))
        self.sent()

    def handle_issue_change(self, issues):
        msg = 'Alert: %d issue%s' % (len(issues), pluralise(issues))
        self.send_message(msg, None, len(issues) and 2 or -2)


class XMPP(BaseNotification):

    description = 'XMPP Message'

    def __init__(self, xmppid):
        BaseNotification.__init__(self)
        self.xmppid = xmppid
        self.conn = RetconXMPP()
        if not self.conn.is_alive():
            self.conn.start()

    def __del__(self):
        if self.conn: self.conn.quit = True

    def send_message(self, message):
        if not self.conn.is_online(self.xmppid):
            raise ValueError('%s does not appear to be online and available' % self.xmppid)
        self.conn.send_message(
            self.xmppid,
            message,
        )
        self.sent()

    def handle_issue_change(self, issues):
        msg = 'Alert: %d issue%s' % (len(issues), pluralise(issues))
        msg += '\n please respond at %s' % config['RETCON_URL']
        self.send_message(msg)

def deal_with_status_change(issues):
    for contact, c in config['CONTACTS'].items():
        for m in c.get('methods'):
            try:
                print 'Contacting %s via %s, issue count: %d' % (contact, m.description, len(issues))
                m.handle_issue_change(issues)
                print 'Succesfully notified %s via %s' % (contact, m.description)
                break
            except Exception, err:
                print 'Error sending notification to %s via %s, exception was:\n%s' % (contact, m.description, err)
                continue

def load_json(url):
    url = urllib.urlopen(url)
    return json.loads(url.read())

class IssuePoller(threading.Thread):

    def run(self):
        issues = {}
        while True:
            print 'Current issues: %s' % issues
            newissues = load_json(config['RETCON_URL'] + config['RETCON_CRIT_API'])['critical']
            print 'New issues: %s' % newissues
            count = len(newissues)
            if (count == len(issues)): #TODO: find a better way to compare these
                print 'Issues unchanged, sleeping...'
                time.sleep(config['POLL_INTERVAL'])
                continue
            print 'Alerting...'
            deal_with_status_change(newissues)
            issues = newissues

def poll_for_changes():
    t = IssuePoller()
    t.start()

if __name__ == '__main__':
    poll_for_changes()
