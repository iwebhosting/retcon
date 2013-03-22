import json
import threading
import xmpp
import time
import urllib


def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance


@singleton
class RetconXMPP(threading.Thread):

    def __init__(self, jid, password):
        self.password = password
        threading.Thread.__init__(self)
        self.jid = xmpp.protocol.JID(jid)
        self.client = xmpp.Client(self.jid.getDomain(), debug=[])
        self.status = xmpp.Presence()
        self.connected = False
        self.roster = {}
        self.quit = False
        self.daemon = True

    def run(self):
        while not self.quit:
            if not self.connected:
                self.connect()
            self.client.Process(1)

    def connect(self):
        if not self.client.connect():
            raise ValueError('Unable to connect to server.')
        if not self.client.auth(self.jid.getNode(), self.password,
                                resource=self.jid.getResource()):
            raise ValueError('Cannot authenticate with xmpp server')
        self.client.RegisterHandler('presence', self.handle_presence)
        self.client.RegisterHandler('message', self.handle_message)
        self.client.RegisterDisconnectHandler(self.disconnect)
        self.client.sendInitPresence(requestRoster=1)
        self.connected = True

    def stomp_message(self, msg_raw):
        try:
            msg = json.loads(msg_raw)
            attrs = {}
            m = xmpp.protocol.Message(
                to=msg['destination'],
                body=msg['body'],
                attrs=attrs,
            )
            print msg
            self.client.send(m)
        except Exception, e:
            print e

    def disconnect(self):
        self.connected = False
        self.roster = {}
        self.updater.quit = True

    def handle_presence(self, session, presence):
        jid = presence.getFrom()
        contact, resource = jid.getStripped(), jid.getResource()
        msgtype, show = presence.getType(), presence.getShow()

        if contact not in self.roster:
            self.roster[contact] = set()
        if msgtype is None and show is None:
            # User is available
            self.roster[contact].add(resource)
            return
        if (msgtype and msgtype.lower() == 'unavailable') or show:
            # We're either offline (unavailable), or show is set to something
            # (dnd, away etc)
            self.roster[contact].discard(resource)
            if not self.roster[contact]:
                del self.roster[contact]

    def set_status(self, statusmsg):
        self.status.setStatus(statusmsg)
        self.client.send(self.status)

    def handle_message(self, session, message):
        msgtype = message.getType()
        fromjid = message.getFrom().getStripped()
        body = message.getBody()
        if body:
            body = body.strip()
        else:
            return
        if msgtype not in ['message', 'chat']:
            return
        if body.lower() == 'ping':
            m = xmpp.protocol.Message(
                to=fromjid,
                body='pong',
            )
            self.client.send(m)

    def is_online(self, jid):
        return jid in self.roster

    def send_message(self, msgto, msgbody):
        self.client.send(xmpp.Message(
            msgto,
            msgbody,
        ))


if __name__ == '__main__':
    x = RetconXMPP()
    x.daemon = False
    x.start()
