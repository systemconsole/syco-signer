SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

CREATE SCHEMA IF NOT EXISTS `syslog` DEFAULT CHARACTER SET latin1 ;
USE `Syslog` ;

-- -----------------------------------------------------
-- Table `signed`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `signed` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `sign` VARCHAR(100) NULL DEFAULT NULL,
  `message` VARCHAR(255) NULL DEFAULT NULL,
  `signdate` DATE NULL DEFAULT NULL,
  `created` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `signed__signdate_idx` (`signdate` ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `exclude`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `trigger` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `user` VARCHAR(100) NULL DEFAULT NULL,
  `from_host_trigger` varchar(60) DEFAULT NULL,
  `sys_log_tag_trigger` varchar(60) DEFAULT NULL,
  `message_trigger` VARCHAR(255) NULL DEFAULT NULL,
  `status` ENUM('DELETE', 'CRITICAL_EXIST', 'WARNING_EXIST', 'CRITICAL_MISSING', 'WARNING_MISSING') NULL DEFAULT NULL,
  `total_deleted` INT(11) DEFAULT 0,
  `deleted_since_changed` INT(11) DEFAULT 0,
  `last_delete` DATETIME NULL DEFAULT NULL,
  `created` DATETIME NULL DEFAULT NULL,
  `changed` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;
ALTER TABLE `trigger` ADD UNIQUE INDEX `trigger_idx` (`status`, `from_host_trigger`, `sys_log_tag_trigger`, `message_trigger`);

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
