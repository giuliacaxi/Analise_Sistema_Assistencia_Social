-- Estou alterando os ID manualmente de toda tabela para que sejam do tipo INT e autoincrementadas
-- Nessa tabela eu tive um problema, pois os antigos ID's em formato de texto não estavam
-- sendo alterados por nada, então eu precisei criar outra coluna para gerar os id de maneira
-- correta. Entretanto, eu acabei deletando a coluna certa dos ID's invés da antiga. 
-- Para consertar, estou fazendo recriando a coluna manualmente.

SET FOREIGN_KEY_CHECKS = 0;
SET SQL_SAFE_UPDATES = 0;

-- Tabela temporária para mapear as linhas físicas aos novos IDs sequenciais
CREATE TEMPORARY TABLE temp_ids AS 
SELECT 
    -- Usa uma Window Function para criar a numeração de 1 a 7000 (número total de casos na tabela)
    ROW_NUMBER() OVER () AS novo_id,
    casos.* FROM casos;

-- Limpeza dos dados da tabela de casos
TRUNCATE TABLE casos;

-- Inserção dos dados de volta com o ID sequencial gerado pelo ROW_NUMBER
INSERT INTO casos (id_caso, Origem, Dt_Abertura, Status, Dt_Encerramento, Motivo_Desligamento, Id_tecnico, Id_tecnico_anterior, Dt_Transferencia) -- Adicione aqui as outras colunas da sua tabela se houver (ex: descricao, data)
SELECT novo_id, Origem, Dt_Abertura, Status, Dt_Encerramento, Motivo_Desligamento, Id_tecnico, Id_tecnico_anterior, Dt_Transferencia FROM temp_ids;

-- Remove a tabela temporária da memória
DROP TEMPORARY TABLE temp_ids;

-- Modificando a coluna de ID's corretamente
ALTER TABLE casos MODIFY COLUMN id_caso INT NOT NULL;
ALTER TABLE casos ADD PRIMARY KEY (id_caso);
ALTER TABLE casos MODIFY COLUMN id_caso INT NOT NULL AUTO_INCREMENT;

SET FOREIGN_KEY_CHECKS = 1;
SET SQL_SAFE_UPDATES = 1;