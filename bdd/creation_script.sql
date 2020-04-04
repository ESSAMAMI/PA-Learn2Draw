-- MySQL Script generated by MySQL Workbench
-- Tue Mar 31 12:28:50 2020
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema learn2draw_db
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `learn2draw_db` ;

-- -----------------------------------------------------
-- Schema learn2draw_db
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `learn2draw_db` DEFAULT CHARACTER SET utf8 ;
USE `learn2draw_db` ;

-- -----------------------------------------------------
-- Table `learn2draw_db`.`USERS`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `learn2draw_db`.`USERS` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(200) NOT NULL,
  `email` VARCHAR(200) NOT NULL,
  `pwd` CHAR(64) NOT NULL,
  `admin` TINYINT NULL,
  `score` INT NULL DEFAULT 0,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- ---------------------------------------------------
-- Table `learn2draw_db`.`CATEGORY`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `learn2draw_db`.`CATEGORY` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(200) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -- -----------------------------------------------------
-- -- Table `learn2draw_db`.`DRAWING`
-- -- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `learn2draw_db`.`DRAWING` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `USERS_id` INT NOT NULL,
  `CATEGORY_id` INT NOT NULL,
  `location` VARCHAR(200) NOT NULL,
  `status` CHAR(1) NOT NULL DEFAULT 'U',
  `score` INT NULL,
  `time` INT NOT NULL,
  PRIMARY KEY (`id`, `USERS_id`, `CATEGORY_id`))
ENGINE = InnoDB;

--  CONSTRAINT FK DRAWING USERS | CATEGORY
ALTER TABLE `learn2draw_db`.`DRAWING` ADD
CONSTRAINT `fk_DRAWING_USERS_idx`
FOREIGN KEY (`USERS_id`)
REFERENCES `learn2draw_db`.`USERS` (`id`)
ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `learn2draw_db`.`DRAWING` ADD
CONSTRAINT `fk_DRAWING_CATEGORY1_idx`
FOREIGN KEY (`CATEGORY_id`)
REFERENCES `learn2draw_db`.`CATEGORY` (`id`)
ON DELETE CASCADE ON UPDATE CASCADE;

-- -- -----------------------------------------------------
-- -- Table `learn2draw_db`.`NOTATION`
-- -- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `learn2draw_db`.`NOTATION` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `score` VARCHAR(200) NOT NULL,
  `USERS_id` INT NOT NULL,
  `DRAWING_id` INT NOT NULL,
  `DRAWING_USERS_id` INT NOT NULL,
  `DRAWING_CATEGORY_id` INT NOT NULL,
  PRIMARY KEY (`id`, `USERS_id`, `DRAWING_id`, `DRAWING_USERS_id`, `DRAWING_CATEGORY_id`))
ENGINE = InnoDB;

ALTER TABLE `learn2draw_db`.`NOTATION` ADD
CONSTRAINT `fk_NOTATION_USERS1_idx`
FOREIGN KEY (`USERS_id`)
REFERENCES `learn2draw_db`.`USERS` (`id`)
ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `learn2draw_db`.`NOTATION` ADD
CONSTRAINT `fk_NOTATION_DRAWING1`
FOREIGN KEY (`DRAWING_id` , `DRAWING_USERS_id` , `DRAWING_CATEGORY_id`)
 REFERENCES `learn2draw_db`.`DRAWING` (`id` , `USERS_id` , `CATEGORY_id`)
ON DELETE CASCADE ON UPDATE CASCADE;


-- -----------------------------------------------------
-- Table `learn2draw_db`.`MODELS`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `learn2draw_db`.`MODELS` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(200) NOT NULL,
  `epochs` INT NOT NULL,
  `accuracy` DOUBLE NOT NULL,
  `loss` DOUBLE NOT NULL,
  `val_accuracy` DOUBLE NOT NULL,
  `val_loss` DOUBLE NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `learn2draw_db`.`RULES`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `learn2draw_db`.`RULES` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `first_param` VARCHAR(200) NULL,
  `second_param` VARCHAR(200) NULL,
  `MODELS_id` INT NOT NULL,
  PRIMARY KEY (`id`, `MODELS_id`))
ENGINE = InnoDB;

ALTER TABLE `learn2draw_db`.`RULES` ADD
CONSTRAINT `fk_RULES_MODELS1_idx`
FOREIGN KEY (`MODELS_id`)
REFERENCES `learn2draw_db`.`MODELS` (`id`)
ON DELETE CASCADE ON UPDATE CASCADE;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;