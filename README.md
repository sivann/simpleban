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



