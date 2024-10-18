Proof of concept for banning events (e.g. failed logins).
Checks a set of (username, remote IP, event type), and decides on BAN after maximum events happening on a period. 

There is one DB row for each (username, remote IP, event type), no auth events are logged so it is rather economical on resources.

Algorithm:
For each event match, check if last event was older than check_range_sec seconds. If older, update the epoch of last event (event_inrange_ts), no further action. If in range of check, update attemts_inrange. If attempts exceed max_attempts, update ban_until_ts timestamp.




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

Each newline will produce a valid event, check if it gets banned.



