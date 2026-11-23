-- DSAN 6300 Mini-Project (HW4): dimension tables for schema FAA.
-- Table and column names match what MySQL Workbench's Table Data Import Wizard
-- creates from the Canvas CSV files (table name = file name), so the analysis
-- queries work whether you load these with the Wizard or with this script.
USE FAA;

CREATE TABLE IF NOT EXISTS L_AIRLINE_ID (
  `ID`   int  NOT NULL,
  `Name` text,
  PRIMARY KEY (`ID`)
);

CREATE TABLE IF NOT EXISTS L_AIRPORT (
  `Code` varchar(10) NOT NULL,
  `Name` text,
  PRIMARY KEY (`Code`)
);

CREATE TABLE IF NOT EXISTS L_AIRPORT_ID (
  `ID`   int  NOT NULL,
  `Name` text,
  PRIMARY KEY (`ID`)
);

CREATE TABLE IF NOT EXISTS L_CANCELATION (
  `Code`   varchar(5) NOT NULL,
  `Reason` text,
  PRIMARY KEY (`Code`)
);

CREATE TABLE IF NOT EXISTS L_DISTANCE_GROUP_250 (
  `Code`             int NOT NULL,
  `DistanceInterval` text,
  PRIMARY KEY (`Code`)
);

CREATE TABLE IF NOT EXISTS L_WEEKDAYS (
  `Code` int NOT NULL,
  `Day`  text,
  PRIMARY KEY (`Code`)
);
