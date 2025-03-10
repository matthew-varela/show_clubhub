-- ------------------------------------------------------
-- Table structure for table `clubs`
-- ------------------------------------------------------

DROP TABLE IF EXISTS `clubs`;
CREATE TABLE `clubs` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) DEFAULT NULL,
  `affiliations` VARCHAR(255) DEFAULT NULL,
  `pres` INT DEFAULT NULL,
  `vp` INT DEFAULT NULL,
  `pic` BLOB,
  `instagram_handle` VARCHAR(255) DEFAULT NULL,
  `college` INT DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `clubs` (`id`,`name`,`affiliations`,`pres`,`vp`,`pic`,`instagram_handle`,`college`) VALUES
  (1,'Banking at Michigan','Sacs',1,3,NULL,NULL,8),
  (2,'TAMID','Israel',1,2,NULL,NULL,8),
  (3,'MUGSS',NULL,1,NULL,NULL,NULL,11),
  (4,'Solar Car','NASA',1,2,NULL,NULL,2);

-- ------------------------------------------------------
-- Table structure for table `college_clubs`
-- ------------------------------------------------------

DROP TABLE IF EXISTS `college_clubs`;
CREATE TABLE `college_clubs` (
  `college` INT NOT NULL,
  `club` INT NOT NULL,
  PRIMARY KEY (`college`,`club`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `college_clubs` (`college`,`club`) VALUES
  (2,4),
  (8,1),
  (8,2),
  (11,3);

-- ------------------------------------------------------
-- Table structure for table `colleges`
-- ------------------------------------------------------

DROP TABLE IF EXISTS `colleges`;
CREATE TABLE `colleges` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `college_name` VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `colleges` (`id`,`college_name`) VALUES
  (1,'LSA'),
  (2,'Engineering'),
  (3,'Kinesiology'),
  (4,'Nursing'),
  (5,'Pharmacy'),
  (6,'Public Health'),
  (7,'Rackham'),
  (8,'Ross'),
  (9,'SMTD'),
  (10,'Taubman'),
  (11,'Other');

-- ------------------------------------------------------
-- Table structure for table `users`
-- ------------------------------------------------------

DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(45) DEFAULT NULL,
  `email` VARCHAR(45) DEFAULT NULL,
  `password` VARCHAR(255) DEFAULT NULL,
  `firstname` VARCHAR(255) DEFAULT NULL,
  `lastname` VARCHAR(255) DEFAULT NULL,
  `profile_image` LONGBLOB,
  `phone` VARCHAR(255) DEFAULT NULL,
  `pic` BLOB,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `users` 
  (`id`, `username`, `email`, `password`, `firstname`, `lastname`, `profile_image`, `phone`, `pic`)
VALUES
  (1,'mattvarela','mattvarela@umich.edu','mattvarela','Matthew','Varela',
    _binary '... (truncated blob data) ...',
    '424-273-3835',
    NULL
  ),
  (4,'mattsuba','mattsuba@umich.edu','mattsuba','Matthew','Suba',
    NULL,
    NULL,
    NULL
  );

-- ------------------------------------------------------
-- Table structure for table `user_clubs`
-- ------------------------------------------------------

DROP TABLE IF EXISTS `user_clubs`;
CREATE TABLE `user_clubs` (
  `user_id` INT NOT NULL,
  `club_id` INT NOT NULL,
  PRIMARY KEY (`user_id`,`club_id`),
  KEY `club_id` (`club_id`),
  CONSTRAINT `user_clubs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `user_clubs_ibfk_2` FOREIGN KEY (`club_id`) REFERENCES `clubs` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `user_clubs` (`user_id`,`club_id`) VALUES
  (1,1),
  (2,1),
  (3,1),
  (1,2),
  (2,2),
  (1,3);

-- ------------------------------------------------------
-- Trigger to insert into college_clubs after clubs insert
-- ------------------------------------------------------

DROP TRIGGER IF EXISTS `after_clubs_insert`;
DELIMITER //
CREATE TRIGGER `after_clubs_insert`
AFTER INSERT ON `clubs`
FOR EACH ROW
BEGIN
    INSERT INTO `college_clubs` (college, club)
    VALUES (NEW.college, NEW.id);
END;
//
DELIMITER ;