UPDATE `learn2draw_db`.`drawings` SET `status` = '1', `score_by_votes` = '0' WHERE (`id` = '1050');# and (`USERS_id` = '3') and (`CATEGORIES_id` = '3');
UPDATE `learn2draw_db`.`drawings` SET `status` = '3' WHERE (`id` BETWEEN 50 AND 1049);# and (`USERS_id` = '3') and (`CATEGORIES_id` = '3');
UPDATE `learn2draw_db`.`categories` SET `dataset_available` = '0' WHERE (`name` = 'chat' );
DELETE FROM `learn2draw_db`.`notations` WHERE (`USERS_id` = '4') and (`DRAWINGS_id` = '1050');