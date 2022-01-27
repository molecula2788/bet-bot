-- MariaDB dump 10.19  Distrib 10.7.1-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: bot
-- ------------------------------------------------------
-- Server version	10.7.1-MariaDB-1:10.7.1+maria~focal

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `bet_choices`
--

DROP TABLE IF EXISTS `bet_choices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bet_choices` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `bet_id` int(10) unsigned NOT NULL,
  `choice` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `bet_id` (`bet_id`),
  CONSTRAINT `bet_choices_ibfk_1` FOREIGN KEY (`bet_id`) REFERENCES `bets` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bet_choices`
--

LOCK TABLES `bet_choices` WRITE;
/*!40000 ALTER TABLE `bet_choices` DISABLE KEYS */;
/*!40000 ALTER TABLE `bet_choices` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bet_questions`
--

DROP TABLE IF EXISTS `bet_questions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bet_questions` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `bet_id` int(10) unsigned NOT NULL,
  `question` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `bet_id` (`bet_id`),
  CONSTRAINT `bet_questions_ibfk_1` FOREIGN KEY (`bet_id`) REFERENCES `bets` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bet_questions`
--

LOCK TABLES `bet_questions` WRITE;
/*!40000 ALTER TABLE `bet_questions` DISABLE KEYS */;
/*!40000 ALTER TABLE `bet_questions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bet_votes`
--

DROP TABLE IF EXISTS `bet_votes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bet_votes` (
  `bet_id` int(10) unsigned NOT NULL,
  `user` varchar(255) NOT NULL,
  `ts` bigint(20) NOT NULL,
  `choice_id` int(10) unsigned NOT NULL,
  PRIMARY KEY (`bet_id`,`user`),
  KEY `bet_id` (`bet_id`,`choice_id`),
  CONSTRAINT `bet_votes_ibfk_1` FOREIGN KEY (`bet_id`) REFERENCES `bets` (`id`),
  CONSTRAINT `bet_votes_ibfk_2` FOREIGN KEY (`bet_id`, `choice_id`) REFERENCES `bet_choices` (`bet_id`, `id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bet_votes`
--

LOCK TABLES `bet_votes` WRITE;
/*!40000 ALTER TABLE `bet_votes` DISABLE KEYS */;
/*!40000 ALTER TABLE `bet_votes` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = latin1 */ ;
/*!50003 SET character_set_results = latin1 */ ;
/*!50003 SET collation_connection  = latin1_swedish_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`bot`@`%`*/ /*!50003 TRIGGER `check_bet_votes_date_insert` BEFORE INSERT ON `bet_votes`
FOR EACH ROW
BEGIN
    IF (new.ts > (SELECT voting_end_date from bets where id = new.bet_id)) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Vote date is after bet\'s end of voting';
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `bet_votes_history`
--

DROP TABLE IF EXISTS `bet_votes_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bet_votes_history` (
  `bet_id` int(10) unsigned NOT NULL,
  `user` varchar(255) NOT NULL,
  `ts` bigint(20) NOT NULL,
  `choice_id` int(10) unsigned NOT NULL,
  PRIMARY KEY (`bet_id`,`user`,`ts`),
  KEY `bet_id` (`bet_id`,`choice_id`),
  CONSTRAINT `bet_votes_history_ibfk_1` FOREIGN KEY (`bet_id`) REFERENCES `bets` (`id`),
  CONSTRAINT `bet_votes_history_ibfk_2` FOREIGN KEY (`bet_id`, `choice_id`) REFERENCES `bet_choices` (`bet_id`, `id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bet_votes_history`
--

LOCK TABLES `bet_votes_history` WRITE;
/*!40000 ALTER TABLE `bet_votes_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `bet_votes_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bets`
--

DROP TABLE IF EXISTS `bets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bets` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `user` varchar(255) NOT NULL,
  `ts` bigint(20) NOT NULL,
  `resolve_date` bigint(20) NOT NULL,
  `voting_end_date` bigint(20) NOT NULL,
  `active` int(11) NOT NULL,
  `correct_choice_id` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id` (`id`,`correct_choice_id`),
  CONSTRAINT `bets_ibfk_1` FOREIGN KEY (`id`, `correct_choice_id`) REFERENCES `bet_choices` (`bet_id`, `id`),
  CONSTRAINT `bets_chk_2` CHECK (`active` <= 1),
  CONSTRAINT `bets_chk_3` CHECK (`active` = 0 and `correct_choice_id` is not null or `active` = 1 and `correct_choice_id` is null),
  CONSTRAINT `bets_chk_4` CHECK (`voting_end_date` < `resolve_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bets`
--

LOCK TABLES `bets` WRITE;
/*!40000 ALTER TABLE `bets` DISABLE KEYS */;
/*!40000 ALTER TABLE `bets` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bot_config`
--

DROP TABLE IF EXISTS `bot_config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bot_config` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(128) DEFAULT NULL,
  `value` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` varchar(255) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `avatar_url` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-01-27 13:03:14
