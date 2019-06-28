-- MySQL dump 10.13  Distrib 8.0.16, for Win64 (x86_64)
--
-- Host: 34.94.60.13    Database: discord_db
-- ------------------------------------------------------
-- Server version	8.0.16

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
 SET NAMES utf8 ;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `games`
--

DROP TABLE IF EXISTS `games`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `games` (
  `identi` varchar(18) NOT NULL,
  `enemy` varchar(15) NOT NULL,
  `e_wpn` varchar(15) NOT NULL,
  `e_stats` varchar(15) NOT NULL,
  `p_stats` varchar(15) NOT NULL,
  `inv` varchar(100) NOT NULL,
  `dice_ranks` varchar(30) NOT NULL,
  `dice_values` varchar(15) NOT NULL,
  `e_blessings` tinyint(4) NOT NULL,
  `p_blessings` tinyint(4) NOT NULL,
  `cur_level` tinyint(4) NOT NULL,
  `p_b_uses` varchar(15) NOT NULL,
  `p_wounds` varchar(50) NOT NULL,
  `e_wounds` varchar(50) NOT NULL,
  `p_dice` varchar(15) NOT NULL,
  `e_dice` varchar(15) NOT NULL,
  `actions` varchar(350) NOT NULL DEFAULT '',
  `p_targeting` varchar(10) NOT NULL DEFAULT 'chest',
  `e_targeting` varchar(10) NOT NULL DEFAULT 'chest',
  `e_attacked` tinyint(4) NOT NULL DEFAULT '0',
  `p_d_count` varchar(15) NOT NULL,
  `e_d_count` varchar(15) NOT NULL,
  `p_extra` varchar(15) NOT NULL,
  `loot` varchar(100) NOT NULL DEFAULT 'none',
  `p_popper` varchar(50) NOT NULL,
  `e_popper` varchar(50) NOT NULL,
  PRIMARY KEY (`identi`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2019-06-28 11:29:19
