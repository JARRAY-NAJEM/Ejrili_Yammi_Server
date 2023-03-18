-- CREATE DATABASE postgres;

CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY NOT NULL AUTO_INCREMENT,
  firstname VARCHAR(255) NOT NULL,
  lastname VARCHAR(255) NOT NULL,
  Email VARCHAR(255) NOT NULL UNIQUE,
  phone INTEGER NOT NULL,
  password VARCHAR(255) NOT NULL,
  ------------------------------------------
  name VARCHAR(255) NOT NULL,
  Relationship VARCHAR(255) NOT NULL,
  Email VARCHAR(255) NOT NULL,
  phone VARCHAR(255) NOT NULL,


  ------------------------------------------
  medical_conditions VARCHAR(255) ,
  medications  VARCHAR(255)  ,
  allergies  VARCHAR(255)  ,

  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);