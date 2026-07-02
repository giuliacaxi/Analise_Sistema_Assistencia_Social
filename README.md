# **----------------------------------------------------OBJETIVO DO PROJETO-----------------------------------------------**

Este projeto tem como finalidade otimizar um sistema fictício de banco de dados de um setor da Assistência Social. Ele foi inspirado pelo meu estágio, onde atuei na área de dados, porém por N motivos, não consegui implementá-lo totalmente. 

Importante salientar que nenhum dado é real e que não tem relação a nenhum município.

## **-------------------------------------------------FERRAMENTAS UTILIZADAS---------------------------------------------**

-- Python (Pandas e Numpy);
-- Excel;

## **-----------------------------------------------CRIAÇÃO DE DADOS FICTÍCIOS-------------------------------------------**

Para gerar os dados, eu primeiramente montei um escopo de como eu gostaria que as tabelas ficassem. Dessa forma, surgiu algumas restrições que seriam necessárias para que os dados, mesmo que aleatórios e fictícios, tivessem algum sentido e se relacionassem corretamente entre as tabelas.

Em usuários (6500 linhas):

1. Neste setor da assistência social, só são acompanhados usuários menores de idade, jovens infratores e pessoas da terceira idade que tenham sofrido alguma violação de direitos. Usuários fora desses padrões, só podem ser acompanhados pelo setor se forem PCD (Pessoa com Deficiência).

Em técnicos (80 linhas):

1. Dos 80 técnicos gerados, apenas 6 estão com o contrato aberto. O restante, todos possuem uma data de desligamento do setor.

Em casos (7000 linhas):

1. Casos foi mais complexo de se gerar, pois tive que pensar em uma forma que fosse "menos bagunçado" de se visualizar. Como um mesmo usuário pode estar sendo acompanhado em dois casos diferentes ao mesmo tempo (Um jovem pode estar sofrendo negligência dos pais e ao mesmo tempo ter cometido uma infração), separei os ids dos usuários para serem mostrados na tabela de "Casos_Acompanhados".

2. Um fator extremamente importante nesta tabela são as datas. Um caso aberto em 2019 não pode ser acompanhado por um técnico que foi desligado em 2017, por exemplo.

3. Se o caso permanece ativo depois que houve o desligamento do técnico que acompanhava o caso, é necessário realizar a transferência do caso para outro técnico que esteja com o contrato aberto ainda na data.

4. Somente um técnico pode acompanhar cada caso. Não pode haver dois técnicos acompanhando o mesmo caso.

Em caso_violação:

1.  Como cada caso pode ter N violações e as violações podem estar em N casos, foi criado uma tabela de registros de violações por cada caso.

Em atendimentos_diários (9000 linhas):

1. Os atendimentos possuem registro de id de usuário e do caso acompanhado do técnico, entretanto, os atendimentos não necessariamente são realizados apenas com usuários acompanhados, sendo assim, aqueles que não possuem cadastro no sistema, não deverão ter os id's preenchidos.

2. Importante novamente as datas aqui, pois um técnico que foi desligado em 2018 não pode ter feito atendimento em 2025. 

Em motoristas (54 linhas):

1. Ele segue a mesma lógica da tabela de técnicos.

Em visitas_técnico (7800 linhas):

1. Ele segue a mesma lógica da tabela de atendimentos.

