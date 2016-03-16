drop table if exists user;
create table user (
  user_id integer primary key autoincrement,
  username text not null,
  email text not null,
  pw_hash text not null,
  access integer not null
);
drop table if exists email;
create table email (
  email_id integer primary key autoincrement,
  email text not null,
  email_pw text,
  access integer not null
);
drop table if exists pin;
create table pin (
  pin_id integer primary key autoincrement,
  pin integer not null,
  mode text not null
);
drop table if exists config;
create table config (
  config_id integer primary key autoincrement,
  config_name text not null,
  config_status text not null
);