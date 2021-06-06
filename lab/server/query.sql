-- SQLite
CREATE TABLE fingerprint_value(id integer primary key, loc_id integer not null, ap_id integer not null, foreign key(ap_id) references accesspoint(id), foreign key(loc_id) references location(id));
CREATE TABLE calibrating_mobile(mac_address text primary key, loc_id integer not null, foreign key(loc_id) references location(id));