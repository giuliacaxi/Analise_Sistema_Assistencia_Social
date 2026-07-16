-- Vincula a tabela casos à tabela de tecnicos
ALTER TABLE casos 
ADD CONSTRAINT fk_casos_tecnicos 
FOREIGN KEY (id_tecnico) REFERENCES tecnicos(id_tecnico) 
ON DELETE SET NULL ON UPDATE CASCADE;

