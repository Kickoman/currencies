DROP TABLE IF EXISTS `currency`;
CREATE TABLE `currency` (
  `internal_id` int NOT NULL,
  `internal_code` varchar(255) DEFAULT NULL,
  `abbreviation` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `name_blr` varchar(255) NOT NULL,
  `scale` decimal(18,6) NOT NULL,
  `periodicity` int NOT NULL,
  `date_start` datetime NOT NULL,
  `date_end` datetime NOT NULL,
  PRIMARY KEY (`internal_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

DROP TABLE IF EXISTS `rate`;
CREATE TABLE `rate` (
  `rate_id` int NOT NULL AUTO_INCREMENT,
  `date` timestamp NOT NULL,
  `currency_id` int NOT NULL,
  `rate` decimal(18,6) NOT NULL,
  PRIMARY KEY (`rate_id`),
  UNIQUE KEY `uniq_curr_date` (`date`,`currency_id`),
  KEY `currency_id` (`currency_id`),
  CONSTRAINT `rate_ibfk_1` FOREIGN KEY (`currency_id`) REFERENCES `currency` (`internal_id`)
) ENGINE=InnoDB AUTO_INCREMENT=703 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
