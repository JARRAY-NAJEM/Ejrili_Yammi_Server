-- CREATE DATABASE postgres;

CREATE TABLE IF NOT EXISTS account_user (
  id SERIAL PRIMARY KEY NOT NULL ,
  firstname VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  username VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  phone VARCHAR(255) NOT NULL,
  password VARCHAR(255) NOT NULL,
  gradient VARCHAR(255) ,
  relationship VARCHAR(255) ,
  contact1 VARCHAR(255) ,
  contact2 VARCHAR(255) ,
  information VARCHAR(2555) ,
  medications  VARCHAR(2555)  ,
  allergies  VARCHAR(2555)  ,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);