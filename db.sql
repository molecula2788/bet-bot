-- MySQL dump 10.13  Distrib 8.0.27, for Linux (x86_64)
--
-- Host: localhost    Database: bot
-- ------------------------------------------------------
-- Server version	8.0.27

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
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
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bet_choices` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `bet_id` int unsigned NOT NULL,
  `choice` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `bet_id` (`bet_id`),
  CONSTRAINT `bet_choices_ibfk_1` FOREIGN KEY (`bet_id`) REFERENCES `bets` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
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
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bet_questions` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `bet_id` int unsigned NOT NULL,
  `question` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `bet_id` (`bet_id`),
  CONSTRAINT `bet_questions_ibfk_1` FOREIGN KEY (`bet_id`) REFERENCES `bets` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
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
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bet_votes` (
  `bet_id` int unsigned NOT NULL,
  `user` varchar(255) NOT NULL,
  `ts` bigint NOT NULL,
  `choice_id` int unsigned NOT NULL,
  PRIMARY KEY (`bet_id`,`user`),
  KEY `bet_id` (`bet_id`,`choice_id`),
  CONSTRAINT `bet_votes_ibfk_1` FOREIGN KEY (`bet_id`) REFERENCES `bets` (`id`),
  CONSTRAINT `bet_votes_ibfk_2` FOREIGN KEY (`bet_id`, `choice_id`) REFERENCES `bet_choices` (`bet_id`, `id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bet_votes`
--

LOCK TABLES `bet_votes` WRITE;
/*!40000 ALTER TABLE `bet_votes` DISABLE KEYS */;
/*!40000 ALTER TABLE `bet_votes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bet_votes_history`
--

DROP TABLE IF EXISTS `bet_votes_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bet_votes_history` (
  `bet_id` int unsigned NOT NULL,
  `user` varchar(255) NOT NULL,
  `ts` bigint NOT NULL,
  `choice_id` int unsigned NOT NULL,
  PRIMARY KEY (`bet_id`,`user`,`ts`),
  KEY `bet_id` (`bet_id`,`choice_id`),
  CONSTRAINT `bet_votes_history_ibfk_1` FOREIGN KEY (`bet_id`) REFERENCES `bets` (`id`),
  CONSTRAINT `bet_votes_history_ibfk_2` FOREIGN KEY (`bet_id`, `choice_id`) REFERENCES `bet_choices` (`bet_id`, `id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
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
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bets` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `user` varchar(255) NOT NULL,
  `ts` bigint NOT NULL,
  `resolve_date` bigint NOT NULL,
  `active` int NOT NULL,
  `correct_choice_id` int unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id` (`id`,`correct_choice_id`),
  CONSTRAINT `bets_ibfk_1` FOREIGN KEY (`id`, `correct_choice_id`) REFERENCES `bet_choices` (`bet_id`, `id`),
  CONSTRAINT `bets_chk_2` CHECK ((`active` <= 1)),
  CONSTRAINT `bets_chk_3` CHECK ((((`active` = 0) and (`correct_choice_id` is not null)) or ((`active` = 1) and (`correct_choice_id` is null))))
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
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
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bot_config` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(128) DEFAULT NULL,
  `value` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bot_config`
--

LOCK TABLES `bot_config` WRITE;
/*!40000 ALTER TABLE `bot_config` DISABLE KEYS */;
/*INSERT INTO `bot_config` VALUES (1,'channel_id','C02QWRJGHL2')*/;
/*!40000 ALTER TABLE `bot_config` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-01-02 14:18:07
