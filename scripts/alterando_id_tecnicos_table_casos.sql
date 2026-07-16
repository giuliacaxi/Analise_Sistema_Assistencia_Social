-- Removendo as letras dos ID's dos técnicos e modificando para inteiros

SET SQL_SAFE_UPDATES = 0;

UPDATE casos SET id_tecnico = REPLACE(UPPER(id_tecnico), 'TEC', '');
UPDATE casos SET id_tecnico_anterior = REPLACE(UPPER(id_tecnico_anterior), 'TEC', '');

ALTER TABLE casos MODIFY COLUMN id_tecnico INT NULL;
ALTER TABLE casos MODIFY COLUMN id_tecnico_anterior INT NULL;

SET SQL_SAFE_UPDATES = 1;

