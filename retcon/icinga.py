import time
import json
import urllib
try:
    import pymemc
except:
    pass

BACKEND_DESC = 'Icinga'

STATE = {
    0: 'Ok',
    1: 'Warn',
    2: 'Crit',
    3: 'Unknown',
}


def iso_helper(when, how_much=0):
    assert when == 'NOW'
    t = time.time()
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t + how_much))


def load_json(url):
    c = None
    try:
        c = pymemc.Client('localhost')
    except:
        pass
    if c:
        v = c.get(url)
        if v:
            return json.loads(v)
    urll = urllib.urlopen(url + '&jsonoutput=1')
    data = urll.read()
    if c:
        c.set(url, data, 45)
    return json.loads(data)


class Icinga(object):

    def __init__(self, url, user, backend_name):
        self.url = url
        self.user = user
        self.backend_name = backend_name

    def load_data(self):
        data = {}
        host_problems = load_json('%s/status.cgi?hostgroup=all&style=hostdetail&hoststatustypes=4&hostprops=272394' % self.url)
        service_problems = load_json('%s/status.cgi?host=all&servicestatustypes=20&hoststatustypes=3&serviceprops=272394' % self.url)
        flapping_problems = load_json('%s/status.cgi?host=all&servicestatustypes=16&hoststatustypes=3&serviceprops=271370' % self.url)
        print flapping_problems
        criticals = host_problems['status']['host_status']
        for c in criticals:
            c['backend'] = self.backend_name
            c['service'] = u'Host Check'
        issues = []
        for i in service_problems['status']['service_status']:
            i['backend'] = self.backend_name
            if i['status'].upper() == 'CRITICAL':
                criticals.append(i)
            else:
                issues.append(i)
        flapping = []
        for i in flapping_problems['status']['service_status']:
            i['backend'] = self.backend_name
            flapping.append(i)
        data['critical'] = criticals
        data['issues'] = issues
        data['flapping'] = flapping
        return data

    def fetch(self, thing):
        return self.load_data()[thing]

    def ack(self, host, service=None, duration=7200, comment=None):
        """
        Acknowledge an outstanding issue, with optional comment. Returns nothing.
        """
        cmd_typ = service and 56 or 86
        d = dict(
            cmd_typ=cmd_typ,
            cmd_mod=2,
            hostservice='%s^%s' % (host, service),
            com_author=self.user,
            com_data=comment or 'Acked via Retcon',
            start_time=iso_helper('NOW'),
            end_time=iso_helper('NOW', duration),
            fixed=1,
        )
        urllib.urlopen('%s/cmd.cgi' % self.url, urllib.urlencode(d)).read()
