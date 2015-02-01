-- MySQL dump 10.13  Distrib 5.5.34, for debian-linux-gnu (i686)
--
-- Host: localhost    Database: test
-- ------------------------------------------------------
-- Server version	5.5.34-0ubuntu0.13.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `blogs`
--

DROP TABLE IF EXISTS `blogs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `blogs` (
  `id` varchar(50) NOT NULL,
  `user_id` varchar(50) NOT NULL,
  `user_name` varchar(50) NOT NULL,
  `user_image` varchar(500) NOT NULL,
  `name` varchar(50) NOT NULL,
  `summary` varchar(200) NOT NULL,
  `content` mediumtext NOT NULL,
  `created_at` double NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `blogs`
--

LOCK TABLES `blogs` WRITE;
/*!40000 ALTER TABLE `blogs` DISABLE KEYS */;
INSERT INTO `blogs` VALUES ('0014222573651687dfc592bc6b54fc88808824e80075510000','00142224109225502d058716ca446a0bcaa7e5dbce57309000','David_Lin','','以前以后','现在怎么各自寂寞','本来就是浪漫炙热，被动冷漠，你的心里是否还只剩下温柔。',1422257365.168879),('0014222710765991225c0704ee448b4b3989c02ae2279bc000','00142224109225502d058716ca446a0bcaa7e5dbce57309000','David_Lin','','别打扰他的心','别去打扰他的心','让回忆别去打扰他的心。',1422271076.599505),('00142227326966930a07f72228147da8bc418daadef9c51000','00142224109225502d058716ca446a0bcaa7e5dbce57309000','David_Lin','','姐妹','你是我的姐妹，你是我的baby','你是我的姐妹，你是我的爱人，这天红液压，淘气小辣椒，世界多悠闲，让风怒。\n怎么可以忘掉？\n你是我的界面inish1iwo`1\\',1422273269.669237),('0014223344268654b64345acdb2440bae0d0e6181a35570000','00142224109225502d058716ca446a0bcaa7e5dbce57309000','David_Lin','','Alexandra Stan','give me give','tonight , we will fall in love',1422334426.865719);
/*!40000 ALTER TABLE `blogs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `comments`
--

DROP TABLE IF EXISTS `comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `comments` (
  `id` varchar(50) NOT NULL,
  `blog_id` varchar(50) NOT NULL,
  `user_id` varchar(50) NOT NULL,
  `user_name` varchar(50) NOT NULL,
  `user_image` varchar(500) NOT NULL,
  `content` mediumtext NOT NULL,
  `created_at` double NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `comments`
--

LOCK TABLES `comments` WRITE;
/*!40000 ALTER TABLE `comments` DISABLE KEYS */;
INSERT INTO `comments` VALUES ('0014223359372159008ec0b989d49c4b78f75a20fef16b9000','00142227326966930a07f72228147da8bc418daadef9c51000','00142224109225502d058716ca446a0bcaa7e5dbce57309000','David_Lin','http://www.gravatar.com/avatar/cfac63552ea2b882a2863e61b43e38c2?d=mm&s=120','hello',1422335937.215114);
/*!40000 ALTER TABLE `comments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `id` int(11) NOT NULL,
  `name` text,
  `email` text,
  `passwd` text,
  `last_modified` double DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` varchar(50) NOT NULL,
  `email` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  `admin` tinyint(1) NOT NULL,
  `name` varchar(50) NOT NULL,
  `image` varchar(500) NOT NULL,
  `created_at` double NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES ('0010018336417540987fff4508f43fbaed718e263442526000','admin@example.com','5f4dcc3b5aa765d61d8327deb882cf99',0,'Administrator','',1402909113.628),('001421343710265a6c7fabc98aa400eb6ad4cad80eaad90000','test@example.com','1234567890',0,'Test','about:blank',1421343710.265428),('0014213437192146abfbde925534df2a2df1cca5d215fc7000','test@example.com','1234567890',0,'Test','about:blank',1421343719.21404),('001421379417421e3278409a4b84fdcb58c255cd0199473000','test@example.com','1234567890',0,'Test','about:blank',1421379417.421192),('00142224109225502d058716ca446a0bcaa7e5dbce57309000','kringpin_lin@163.com','7fec2c3e0a86c54a3f2bfdc2ff4daeaa',1,'David_Lin','http://www.gravatar.com/avatar/cfac63552ea2b882a2863e61b43e38c2?d=mm&s=120',1422241092.255937),('001422241180111a8ef143bc2184b42b5f2bc4173c67bbf000','kringpin323@163.com','7fec2c3e0a86c54a3f2bfdc2ff4daeaa',0,'jgp','http://www.gravatar.com/avatar/2b994598781b4d226ebe836ddc99fa8b?d=mm&s=120',1422241180.111249),('00142225384963169292eb0438548dcbc0e6ccf7c24d3e0000','2pm@163.com','7fec2c3e0a86c54a3f2bfdc2ff4daeaa',0,'jun-K','http://www.gravatar.com/avatar/bae68a74ea97e5f162feee6508dec512?d=mm&s=120',1422253849.631761),('0014222568180808133eb7432fd474683cb271d28718da7000','kringpin323@gmail.com','7fec2c3e0a86c54a3f2bfdc2ff4daeaa',0,'kringpin323','http://www.gravatar.com/avatar/94d21dec91c5498e9557fe3e43cfe706?d=mm&s=120',1422256818.080325),('001422337165406be8d222633604f65a5175fdd84c40a05000','1325742149@qq.com','7fec2c3e0a86c54a3f2bfdc2ff4daeaa',0,'Kingpin','http://www.gravatar.com/avatar/da4d7b345a59bb9de40e44986b71909c?d=mm&s=120',1422337165.406889);
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

-- Dump completed on 2015-01-28 16:52:49
