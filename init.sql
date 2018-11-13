
create database `mychat` default character set utf8 collate utf8_general_ci;

use mychat;

CREATE TABLE `message` (
  `msg_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(40) NOT NULL,
  `data` varchar(250) CHARACTER SET utf8mb4 NOT NULL,
  `time` varchar(25) NOT NULL,
  PRIMARY KEY (`msg_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `room` (
  `room_id` int(11) NOT NULL AUTO_INCREMENT,
  `invitor` varchar(40) NOT NULL,
  `guest` varchar(40) NOT NULL,
  PRIMARY KEY (`room_id`),
  UNIQUE KEY `room_id_UNIQUE` (`room_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `room_msg` (
  `room_msg_id` int(11) NOT NULL AUTO_INCREMENT,
  `room_id` int(11) NOT NULL,
  `name` varchar(40) NOT NULL,
  `data` varchar(250) CHARACTER SET utf8mb4 NOT NULL,
  `time` varchar(40) NOT NULL,
  PRIMARY KEY (`room_msg_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `user` (
  `user_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(40) NOT NULL,
  `password` varbinary(100) NOT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
