-- phpMyAdmin SQL Dump
-- version 4.8.4
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1:3306
-- Généré le :  ven. 10 juil. 2020 à 07:34
-- Version du serveur :  5.7.24
-- Version de PHP :  7.2.14

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données :  `learn2draw_db`
--

-- --------------------------------------------------------

--
-- Structure de la table `categories`
--

DROP TABLE IF EXISTS `categories`;
CREATE TABLE IF NOT EXISTS `categories` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `dataset_available` int(1) NOT NULL, 
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;

--
-- Déchargement des données de la table `categories`
--

INSERT INTO `categories` (`id`, `name`, `dataset_available`) VALUES
(2, 'baseball', 1),
(3, 'broom', 1),
(4, 'dolphin', 1),
(1, 'tortue', 0);

-- --------------------------------------------------------

--
-- Structure de la table `drawings`
--

DROP TABLE IF EXISTS `drawings`;
CREATE TABLE IF NOT EXISTS `drawings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `USERS_id` int(11) NOT NULL,
  `CATEGORIES_id` int(11) NOT NULL,
  `CATEGORIES_PREDICTED_id` int(11) NOT NULL,
  `location` varchar(200) NOT NULL,
  `status` char(1) NOT NULL DEFAULT 'U',
  `score` int(11) DEFAULT NULL,
  `score_by_votes` int(11) DEFAULT NULL,
  `time` int(11) NOT NULL,
  PRIMARY KEY (`id`,`USERS_id`,`CATEGORIES_id`),
  UNIQUE KEY `location` (`location`),
  KEY `fk_DRAWINGS_USERS_idx` (`USERS_id`),
  KEY `fk_DRAWINGS_CATEGORIES1_idx` (`CATEGORIES_id`),
  KEY `fk_DRAWINGS_CATEGORIES_PREDICTED1_idx` (`CATEGORIES_PREDICTED_id`)
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=utf8;

--
-- Déchargement des données de la table `drawings`
--

INSERT INTO `drawings` (`id`, `USERS_id`, `CATEGORIES_id`, `CATEGORIES_PREDICTED_id`, `location`, `status`, `score`, `score_by_votes`, `time`) VALUES
(1, 2, 1, 1, '\\static\\assets\\images\\test\\draw.jpg', '0', 50, 0, 10),
(2, 2, 1, 1, '\\static\\assets\\images\\test\\draw1.jpg', '0', 90, 0, 10),
(3, 2, 1, 1, '\\static\\assets\\images\\test\\draw2.jpg', '0', 75, 0, 10),
(4, 2, 1, 1, '\\static\\assets\\images\\test\\draw3.jpg', '0', 45, 0, 10),
(5, 2, 1, 1, '\\static\\assets\\images\\test\\draw4.jpg', '0', 35, 0, 30),
(6, 2, 1, 1, '\\static\\assets\\images\\test\\plot1.png', '0', 90, 0, 30),
(7, 2, 1, 1, '\\static\\assets\\images\\test\\draw5.jpg', '0', 70, 0, 30),
(8, 2, 1, 1, '\\static\\assets\\images\\test\\draw6.jpg', '0', 60, 0, 30),
(9, 2, 1, 1, '\\static\\assets\\images\\test\\draw7.jpg', '0', 22, 0, 30),
(10, 2, 1, 1, '\\static\\assets\\images\\test\\draw8.jpg', '0', 50, 0, 30),
(11, 2, 1, 1, '\\static\\assets\\images\\test\\draw9.jpg', '0', 60, 0, 30),
(12, 2, 1, 1, '\\static\\assets\\images\\test\\draw10.jpg', '0', 60, 0, 30),
(13, 2, 1, 1, '\\static\\assets\\images\\test\\draw11.jpg', '0', 60, 0, 30),
(14, 2, 1, 1, '\\static\\assets\\images\\test\\draw12.jpg', '0', 60, 0, 30),
(15, 2, 1, 1, '\\static\\assets\\images\\test\\draw13.jpg', '0', 60, 0, 30),
(17, 2, 2, 2, '\\static\\doodle\\baseball\\baseball_92.jpg', '1', 97, 0, 10),
(18, 2, 2, 2, '\\static\\doodle\\baseball\\baseball_93.jpg', '1', 91, 0, 10),
(19, 2, 2, 2, '\\static\\doodle\\broom\\broom_38.jpg', '1', 100, 0, 5),
(20, 2, 2, 2, '\\static\\doodle\\baseball\\baseball_94.jpg', '1', 86, 0, 5),
(21, 2, 2, 2, '\\static\\doodle\\baseball\\baseball_95.jpg', '1', 78, 0, 5),
(22, 2, 2, 2, '\\static\\doodle\\baseball\\baseball_109.jpg', '0', 89, 0, 10),
(23, 2, 3, 3, '\\static\\doodle\\broom\\broom_43.jpg', '0', 56, 0, 10),
(24, 2, 3, 3, '\\static\\doodle\\broom\\broom_44.jpg', '0', 57, 0, 10),
(25, 2, 3, 2, '\\static\\doodle\\broom\\broom_45.jpg', '0', 63, 0, 17),
(26, 2, 4, 4, '\\static\\doodle\\dolphin\\dolphin_41.jpg', '0', 98, 0, 10),
(27, 2, 4, 4, '\\static\\doodle\\dolphin\\dolphin_42.jpg', '0', 84, 0, 10),
(28, 2, 4, 4, '\\static\\doodle\\dolphin\\dolphin_43.jpg', '0', 55, 0, 10),
(29, 2, 2, 4, '\\static\\doodle\\baseball\\baseball_110.jpg', '0', 97, 0, 10),
(30, 2, 2, 4, '\\static\\doodle\\baseball\\baseball_111.jpg', '0', 92, 0, 10),
(31, 2, 2, 2, '\\static\\doodle\\baseball\\baseball_112.jpg', '0', 62, 0, 10),
(32, 2, 2, 2, '\\static\\doodle\\baseball\\baseball_113.jpg', '0', 63, 0, 10),
(33, 2, 2, 3, '\\static\\doodle\\baseball\\baseball_114.jpg', '0', 79, 0, 10),
(34, 2, 3, 3, '\\static\\doodle\\broom\\broom_46.jpg', '0', 52, 0, 10),
(35, 2, 2, 2, '\\static\\doodle\\baseball\\baseball_115.jpg', '0', 95, 0, 10),
(36, 2, 2, 3, '\\static\\doodle\\baseball\\baseball_116.jpg', '0', 97, 0, 10),
(37, 2, 4, 2, '\\static\\doodle\\dolphin\\dolphin_44.jpg', '0', 82, 0, 15),
(38, 2, 4, 4, '\\static\\doodle\\dolphin\\dolphin_45.jpg', '0', 85, 0, 10),
(39, 2, 2, 3, '\\static\\doodle\\baseball\\baseball_117.jpg', '0', 34, 0, 10),
(40, 2, 2, 4, '\\static\\doodle\\baseball\\baseball_118.jpg', '0', 53, 0, 10),
(41, 4, 3, 3, '\\static\\doodle\\broom\\broom_47.jpg', '0', 96, 0, 20);

-- --------------------------------------------------------

--
-- Structure de la table `models`
--

DROP TABLE IF EXISTS `models`;
CREATE TABLE IF NOT EXISTS `models` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `epochs` int(11) NOT NULL,
  `accuracy` double NOT NULL,
  `loss` double NOT NULL,
  `val_accuracy` double NOT NULL,
  `val_loss` double NOT NULL,
  `params` varchar(800) NOT NULL,
  `time` varchar(40) NOT NULL,
  `categories_handled` varchar(800) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;

--
-- Déchargement des données de la table `models`
--

INSERT INTO `models` (`id`, `name`, `epochs`, `accuracy`, `loss`, `val_accuracy`, `val_loss`, `params`, `time`, `categories_handled`) VALUES
(1, 'default', 40, 0.993, 0.018, 0.988, 0.034, 'batch_size;1024;optimizer;adadelta;learning_rate;0.001', '20200628035258', 'baseball,broom'),
(7, 'cnn_model_1', 14, 0.972, 0.079, 0.966, 0.099, 'batch_size;100;optimizer;adadelta;learning_rate;0.001', '20200701121108', 'baseball,dolphin,broom');

-- --------------------------------------------------------

--
-- Structure de la table `notations`
--

DROP TABLE IF EXISTS `notations`;
CREATE TABLE IF NOT EXISTS `notations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `score` varchar(200) NOT NULL,
  `USERS_id` int(11) NOT NULL,
  `DRAWINGS_id` int(11) NOT NULL,
  `DRAWINGS_USERS_id` int(11) NOT NULL,
  `DRAWINGS_CATEGORIES_id` int(11) NOT NULL,
  PRIMARY KEY (`id`,`USERS_id`,`DRAWINGS_id`,`DRAWINGS_USERS_id`,`DRAWINGS_CATEGORIES_id`),
  KEY `fk_NOTATIONS_USERS1_idx` (`USERS_id`),
  KEY `fk_NOTATIONS_DRAWINGS1` (`DRAWINGS_id`,`DRAWINGS_USERS_id`,`DRAWINGS_CATEGORIES_id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;

--
-- Déchargement des données de la table `notations`
--

INSERT INTO `notations` (`id`, `score`, `USERS_id`, `DRAWINGS_id`, `DRAWINGS_USERS_id`, `DRAWINGS_CATEGORIES_id`) VALUES
(1, 'no', 3, 21, 2, 2),
(2, 'yes', 3, 19, 2, 2),
(3, 'yes', 3, 20, 2, 2),
(4, 'yes', 3, 18, 2, 2),
(5, 'yes', 3, 17, 2, 2),
(6, 'yes', 4, 15, 2, 1),
(10, 'yes', 4, 28, 2, 4),
(14, 'Yes', 4, 27, 2, 4);

-- --------------------------------------------------------

--
-- Structure de la table `rules`
--

DROP TABLE IF EXISTS `rules`;
CREATE TABLE IF NOT EXISTS `rules` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `first_param` varchar(200) DEFAULT NULL,
  `second_param` varchar(200) DEFAULT NULL,
  `MODELS_id` int(11) NOT NULL,
  PRIMARY KEY (`id`,`MODELS_id`),
  KEY `fk_RULES_MODELS1_idx` (`MODELS_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Structure de la table `trophee`
--

DROP TABLE IF EXISTS `trophee`;
CREATE TABLE IF NOT EXISTS `trophee` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `range` varchar(10) NOT NULL,
  `forme` varchar(100) NOT NULL,
  `icon` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

--
-- Déchargement des données de la table `trophee`
--

INSERT INTO `trophee` (`id`, `range`, `forme`, `icon`) VALUES
(1, '50-200', 'Wahou ! plus de 50 images notées !', 'assets/images/badges/badge_bronze.png'),
(2, '200-500', 'On à faire à un vrai joueur ! plus de 200 images notées ! Bravo...', 'assets/images/badges/badge_cuivre.png'),
(3, '500-1000', 'C\'est magique voici le roi des notations ! plus de 500 images notées ! Bravo...', 'assets/images/badges/badge_or.png');

-- --------------------------------------------------------

--
-- Structure de la table `users`
--

DROP TABLE IF EXISTS `users`;
CREATE TABLE IF NOT EXISTS `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(200) NOT NULL,
  `email` varchar(200) NOT NULL,
  `pwd` char(64) NOT NULL,
  `admin` tinyint(4) DEFAULT NULL,
  `score` int(11) DEFAULT '0',
  `count_notation` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;

--
-- Déchargement des données de la table `users`
--

INSERT INTO `users` (`id`, `username`, `email`, `pwd`, `admin`, `score`, `count_notation`) VALUES
(1, 'arnaudsimon091@gmail.comaa', 'arnaudsimon091@gmail.com', 'aqwzsx', 0, 0, 0),
(2, 'Zouzou l\'abricot', 'user1@gmail.com', 'aqwzsx', 0, 0, 0),
(3, 'arnaud_lasticotier', 'arnaud_lasticot@gmail.com', 'aqwzsxedc', 0, 0, 5),
(4, 'Hamza ESSAMAMI', 'hamza@learn2draw.com', 'azerty', 1, 45, 3),
(5, 'clem', 'clem@learn2draw.com', 'azerty', 0, 0, 0);

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `drawings`
--
ALTER TABLE `drawings`
  ADD CONSTRAINT `fk_DRAWINGS_CATEGORIES1_idx` FOREIGN KEY (`CATEGORIES_id`) REFERENCES `categories` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_DRAWINGS_CATEGORIES_PREDICTED1_idx` FOREIGN KEY (`CATEGORIES_PREDICTED_id`) REFERENCES `categories` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_DRAWINGS_USERS_idx` FOREIGN KEY (`USERS_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Contraintes pour la table `notations`
--
ALTER TABLE `notations`
  ADD CONSTRAINT `fk_NOTATIONS_DRAWINGS1` FOREIGN KEY (`DRAWINGS_id`,`DRAWINGS_USERS_id`,`DRAWINGS_CATEGORIES_id`) REFERENCES `drawings` (`id`, `USERS_id`, `CATEGORIES_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_NOTATIONS_USERS1_idx` FOREIGN KEY (`USERS_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Contraintes pour la table `rules`
--
ALTER TABLE `rules`
  ADD CONSTRAINT `fk_RULES_MODELS1_idx` FOREIGN KEY (`MODELS_id`) REFERENCES `models` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;