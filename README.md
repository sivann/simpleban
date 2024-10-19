Proof of concept for banning events (e.g. failed logins).
Checks a set of (username, remote IP, event type), and decides on BAN after maximum events happening on a period. 

There is one DB row for each (username, remote IP, event type), no auth events are logged so it is rather economical on resources.

**Algorithm**
* ```check_range_sec```: forget events after this period 
* ```ban_for_sec```: how long to ban (event_name,username.remote_ip) set
* ```max_attempts```: max attempts in check_range_sec to allow before banning

For each event match, check if last event was older than ```check_range_sec``` seconds. If older, update the epoch of last event (```event_inrange_ts```), take no further action. If in range of check, increment ```attemts_inrange```. If ```attempts_inrange``` exceed ```max_attempts```, update ```ban_until_ts``` timestamp. If ```ban_until_ts``` is non-zero, and ```ban_until_ts``` is > current epoch, a ban state is inferred.




1. create db: 

```
 cat schema-ban.sql |sqlite3  bandb.db
```

2. add a watcher for state:
```
watch -n 0.5  "echo 'select * from request_events' | sqlite3 -header -column bandb.db "
```

3. run simpleban.py:
```
python3 simpleban.py
```

Each time you press newline, a new bannable event will be produced. Press enter fast enough to get a ban until ban_until_ts.



