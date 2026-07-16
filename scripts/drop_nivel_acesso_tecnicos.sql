-- Atualizando os logins dos técnicos para serem referentes ao seu cargo 

SET SQL_SAFE_UPDATES = 0;

UPDATE tecnicos
SET login = CONCAT(LOWER(SUBSTRING_INDEX(TRIM(nome), ' ', 1)), '.as')
WHERE cargo = 'Assistente Social';

UPDATE tecnicos
SET login = CONCAT(LOWER(SUBSTRING_INDEX(TRIM(nome), ' ', 1)), '.psi')
WHERE cargo = 'Psicólogo';


SET SQL_SAFE_UPDATES = 1;

SELECT login FROM tecnicos;


