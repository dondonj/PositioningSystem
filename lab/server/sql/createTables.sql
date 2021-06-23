-- SQLite CREATE ALL TABLES
CREATE TABLE fingerprint_value(id integer primary key, loc_id integer not null, ap_id integer not null, rssi real not null,  foreign key(ap_id) references accesspoint(id), foreign key(loc_id) references location(id));
CREATE TABLE calibrating_mobile(id integer primary key, mac_address text not null, loc_id integer not null, foreign key(loc_id) references location(id));


CREATE TABLE sample(id integer primary key, ap_id integer not null, source_address text not NULL, timestamp text not null,rssi real not null , foreign key(ap_id) references accesspoint(id));
CREATE TABLE location(id integer primary key, x numeric not null,  y numeric not null,  z numeric not null);

CREATE TABLE accesspoint(id integer primary key, mac_address text not null);