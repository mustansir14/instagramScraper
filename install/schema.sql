CREATE DATABASE IF NOT EXISTS `instagram` ;
USE `instagram`;

CREATE TABLE IF NOT EXISTS `profile` (
  `username` varchar(256) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text CHARACTER SET utf8mb4 DEFAULT NULL,
  `category` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `no_of_posts` int(10) unsigned DEFAULT NULL,
  `no_of_followers` int(10) unsigned DEFAULT NULL,
  `no_of_following` int(10) unsigned DEFAULT NULL,
  `date_inserted` datetime DEFAULT NULL,
  `date_updated` datetime DEFAULT NULL,
  `status` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `log` mediumtext COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `post` (
  `id` bigint(20) NOT NULL,
  `username` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `date_posted` datetime DEFAULT NULL,
  `caption` text COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `no_of_likes` int(11) DEFAULT NULL,
  `is_video` tinyint(1) DEFAULT NULL,
  `media_paths` varchar(1000) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `date_inserted` datetime DEFAULT NULL,
  `date_updated` datetime DEFAULT NULL,
  `status` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `log` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

