-- Alterando os ID's da tabela de motoristas
SET SQL_SAFE_UPDATES = 0;

UPDATE motoristas 
SET Id_motorista = REPLACE(UPPER(Id_motorista), 'MOT', '');

UPDATE motoristas 
SET Id_motorista = CAST(Id_motorista AS UNSIGNED);

SET SQL_SAFE_UPDATES = 1;

ALTER TABLE motoristas MODIFY COLUMN Id_motorista VARCHAR(255) NOT NULL;
ALTER TABLE motoristas ADD PRIMARY KEY (Id_motorista);
ALTER TABLE motoristas MODIFY COLUMN Id_motorista INT NOT NULL AUTO_INCREMENT;