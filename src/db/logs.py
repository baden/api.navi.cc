# -*- coding: utf-8 -*-

#import db
#print "db:logs:import", repr(db)


class Logs(object):
    def __init__(self, db):
        self.col = db.collection("logs")
        self.col.ensure_index([
            ("skey", 1), ("dt", 1)
        ])

    def add(self, log):
        '''
        text = log.get('text')
        if log.get('mtype') == 'alarm':
            if text is None:
                text = u'Нажата тревожная кнопка.'
            alarmmsg = Alarm.add_alarm(log.get('imei', '-'), log.get('fid', 10), db.GeoPt(log.get('lat', 0.0), log.get('lon', 0.0)), log.get('ceng', ''))

        if log.get('mtype') == 'alarm_confirm':
            if text is None:
                text = u'Тревога подтверждена оператором %s' % DBAccounts.get(db.Key(log.get('akey'))).user.nickname()

        if log.get('mtype') == 'alarm_cancel':
            if text is None:
                text = u'Отбой тревоги оператором %s' % DBAccounts.get(db.Key(log.get('akey'))).user.nickname()

        if text != 'ignore me': # Ping
            gpslog = GPSLogs(parent = log['skey'], text = text, label = log.get('label', 0), mtype = log.get('mtype', ''), pos = db.GeoPt(log.get('lat', 0.0), log.get('lon', 0.0)))
            gpslog.put()

            inform(log['skey'], 'addlog', {
                'skey': str(log['skey']),
                #'time': gpslog.date.strftime("%d/%m/%Y %H:%M:%S"),
                'time': datetime.utcnow().strftime("%y%m%d%H%M%S"),
                'text': text,
                'label': log.get('label', 0),
                'mtype': log.get('mtype', ''),
                'key': "%s" % gpslog.key(),
                'data': {
                    'lat': log.get('lat', 0.0),
                    'lon': log.get('lon', 0.0),
                    'fid': log.get('fid', 0),
                    'ceng': log.get('ceng', ''),
                    'dt': datetime.now().strftime("%y%m%d%H%M%S")
                }

            })  # Информировать всех пользователей, у которых открыта страница Отчеты
        '''
        self.col.insert(log)
