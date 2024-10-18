
CREATE TABLE request_events  (
   event_name TEXT,
   event_inrange_ts INTEGER,
   attempts_inrange INTEGER,
   ban_until_ts INTEGER,
   username TEXT,
   remote_ip TEXT,
   PRIMARY KEY (event_name, username, remote_ip)
);
