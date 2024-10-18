import sqlite3
import os
import sys
import json
import time



# Used to provide key/value results in SQLite queries
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def init_db(otp_dbpath):
    con =  sqlite3.connect(otp_dbpath)
    con.row_factory = dict_factory
    return con

# 
# check_range_sec: forget events after this period 
# ban_for_sec: how long to ban (event_name,username.remote_ip) set
# max_attempts: max attempts in check_range_sec to allow before banning
def checkEvent(event_name, check_range_sec, max_attempts, banfor_sec, username, remote_ip):
    now = int(time.time())
    cur = dbcon.cursor()
    row = cur.execute("SELECT * FROM request_events  WHERE event_name=? and username=? and remote_ip=?", (event_name, username, remote_ip)).fetchall()

    def reportBanUntil(ts):
        dt=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(ts))
        msg=f"You are doing too many unsuccessful requests, banned until {dt}"
        print(msg)
        return msg
        #scghttp.http_error(429, msg)

    def addEvent():
        print(f'No event found for {username},{remote_ip}, adding new')
        sql = "INSERT INTO request_events  (event_name, event_inrange_ts, attempts_inrange, ban_until_ts, username, remote_ip) VALUES (?,?,?,?,?,?)"
        try:
            cur.execute(sql, (event_name, now, 0, 0, username, remote_ip))
            dbcon.commit()
        except Exception as e:
            msg = f'simpleban:add event_name:{event_name}, remote_ip:{remote_ip}, error: {e}'
            #scghttp.http_error(500, msg)
            print('error:',msg)

    def banUntil(ban_until_ts):
        print(f'Ban until for {username},{remote_ip}, ban until {ban_until_ts}')
        sql = "UPDATE request_events  set ban_until_ts = ? WHERE event_name=? and username=? and remote_ip=?"
        try:
            cur.execute(sql, (ban_until_ts, event_name, username, remote_ip))
            dbcon.commit()
        except Exception as e:
            msg = 'simpleban:banuntil username:%s, remote_ip:%s, error: %s'%(username,remote_ip,e)
            #scghttp.http_error(500, msg)
            print('error:',msg)
 
    def updateAttempts():
        print(f'Updating attempts found for username:{username}, remote_ip:{remote_ip}')
        sql = "UPDATE request_events  set attempts_inrange = attempts_inrange +1 WHERE event_name=? and username=? and remote_ip=?"
        try:
            cur.execute(sql, (event_name, username, remote_ip))
            dbcon.commit()
        except Exception as e:
            msg = f'simpleban:updateattempts event_name:{event_name}, remote_ip:{remote_ip}'
            #scghttp.http_error(500, msg)
            print('error:',msg)
 
    def updateEventTS():
        print(f'Updating event TS for {username},{remote_ip}, refreshing ts')
        sql = "UPDATE request_events  set attempts_inrange = 1, event_inrange_ts=? WHERE event_name=? and username=? and remote_ip=?"
        try:
            cur.execute(sql, (now, event_name, username, remote_ip))
            dbcon.commit()
        except Exception as e:
            msg = 'simpleban:updateeventts username:%s, remote_ip:%s, error: %s'%(username,remote_ip,e)
            #scghttp.http_error(500, msg)
            print('error:',msg)
 

    if len(row) == 0: # never before
        addEvent()
    elif row[0]['ban_until_ts'] >= now: # still banned
        updateAttempts()
        reportBanUntil(row[0]['ban_until_ts'])
    elif row[0]['event_inrange_ts'] < (now - check_range_sec): # last event older than check range, update event_ts,
        print(f"Previous event was old {row[0]['event_inrange_ts']} for {username},{remote_ip}, updating event_inrange_ts")
        updateEventTS()
    elif row[0]['event_inrange_ts'] >= (now - check_range_sec): # in check range
        if row[0]['attempts_inrange'] > max_attempts:
            updateAttempts()
            banUntil(now+banfor_sec)
            reportBanUntil(now+banfor_sec)
        else:
            updateAttempts()
    else:
        print(f"*** Unhandled case, should not happen. now:{now}, row:{row}")

    print('')

if __name__ == '__main__':
    dbcon = init_db('bandb.db')
    while 1:
        line = sys.stdin.readline()
        ln=line.strip()
        print(f'Here, {ln}')
        #checkEvent(event_name, check_range_sec, max_attempts, banfor_sec, username, remote_ip):
        checkEvent(event_name='failed_otp', check_range_sec=10, max_attempts=3, banfor_sec=5, username='user1', remote_ip='1.2.3.4')
        if not line:
            break
