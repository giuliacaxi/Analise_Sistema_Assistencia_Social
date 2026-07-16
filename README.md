<<<<<<< Updated upstream
#### **----------------------------------------------------OBJETIVO DO PROJETO--------------------------------**
=======
#### **----------------------------------------------------OBJETIVO DO PROJETO-----------------------------------------------**
>>>>>>> Stashed changes

Este projeto tem como finalidade otimizar um sistema fictício de banco de dados de um setor da Assistência Social. Ele foi inspirado pelo meu estágio, onde atuei na área de dados, porém por N motivos, não consegui implementá-lo totalmente. 

Importante salientar que nenhum dado é real e que não tem relação a nenhum município.

<<<<<<< Updated upstream
#### **-------------------------------------------------FERRAMENTAS UTILIZADAS-------------------------------**
=======
#### **-------------------------------------------------FERRAMENTAS UTILIZADAS---------------------------------------------**
>>>>>>> Stashed changes

-- Python
    - Bibliotecas Usadas:
        1. Pandas;
        2. Numpy;
        3. sqlalchemy;
        4. os;
        5. dotenv;
        6. customtkinter;
        7. Faker;
        8. mysql.connector;
-- Excel;
-- MySQL.

<<<<<<< Updated upstream
#### **-----------------------------------------------CRIAÇÃO DE DADOS FICTÍCIOS-----------------------------**
=======
#### **-----------------------------------------------CRIAÇÃO DE DADOS FICTÍCIOS-------------------------------------------**
>>>>>>> Stashed changes

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

#### **-----------------------------------------------IMPORTAÇÃO DOS DADOS EXCEL -> MySQL-------------------------------------------**

Para importar os dados do excel para o MySQL, por questões de segurança, fiz utilidade das bibliotecas "os" e "dotenv" do Python, para que minhas informações como nome de usuário e senha, não fosse escrito no código.

Coloquei na raiz do projeto o arquivo .env com essas informações, para que o código só as carregasse sem mostrar nada. Também adicionei o arquivo no .gitignore.

Após realizar a leitura dos dados do excel, percebi que para o sistema ficar mais completo, eu esqueci de adicionar duas tabelas que seriam cruciais:

1. Coordenador;
2. Outros Funcionários.

Elas são importantes pois gostaria que o sistema possuísse níveis de acesso diferentes, para que houvesse uma melhor consistência. Não seria certo que o recepcionista tivesse o mesmo acesso que os técnicos (Assistentes Social e Psicólogos).

Então, até o momento, há três níveis de acesso diferentes que podem mudar mais para frente.

1. Coodernador;
2. Técnico;
3. Funcionário;

O nível funcionário remete a tabela "Funcionários" que foi criada, que contém os seguintes cargos:

1. Administrador;
2. Analista de Dados;
3. Administrador de Banco de Dados;
4. Recepcionista;

Por senso comum, é claro que o DBA teria acesso absoluto do sistema, ao contrário dos demais. No momento, fiz com que no script do aplicativo uma aba especial fosse aberta para ele, mas talvez seria melhor criar outro nível de acesso, para melhor padronização.


#### **-----------------------------------------------SISTEMA/APLICATIVO DE INTERFACE VISUAL-------------------------------------------**

Imaginando que para manter uma padronização melhor dos dados inseridos, minha próxima etapa e construir um sistema de interface visual que linke com o banco de dados, para que novos dados sejam inseridos através do sistema e seja armazenado diretamente no banco de dados local.

Para isso, é preciso montar a estrutura desse aplicativo, onde há diferentes login's que darão acesso a diferentes páginas. 

Um administrador não vai ter a mesma interface que o coordenador, por exemplo.


## Funcionalidades Implementadas até o momento:

### 2. Controle de Acesso Baseado em Papéis (RBAC)
* O sistema identifica o cargo do usuário no momento do login e constrói o menu lateral dinamicamente.
* **Níveis de Acesso mapeados:**
  * Administrador de Banco de Dados (DBA)
  * Administrador
  * Coordenador
  * Assistente Social (Técnico)
  * Psicólogo (Técnico)
  * Analista de Dados
  * Recepcionista

### 3. Automação e Gestão de Credenciais
* **Geração Automática de Login:** Ao cadastrar um novo funcionário, o sistema gera o login em tempo real baseado no primeiro nome e na extensão do cargo (ex: `gabriel.dba`, `paula.social`).
* **IDs Visuais Dinâmicos:** O banco de dados armazena apenas IDs numéricos puros para máxima performance (`AUTO_INCREMENT`), mas o sistema renderiza prefixos visuais baseados no cargo para o usuário final (ex: `DBA01`, `TEC12`, `ADM05`).

### 4. Validação e Tratamento de Dados
* **Máscara de Data Dinâmica (`dd/mm/yyyy`):** Campos de data na interface inserem as barras `/` automaticamente enquanto o usuário digita e bloqueiam letras.
* **Conversão de Datas:** Conversão automática do padrão brasileiro visual (`DD/MM/AAAA`) para o padrão universal do banco de dados (`YYYY-MM-DD`) utilizando a biblioteca nativa `datetime`.
* **Tratamento de Dados Nulos no SQL:** Estruturação correta para aceitar datas nulas (`NULL`) em funcionários ativos, contornando limitações de `NO_ZERO_DATE` do modo estrito do MySQL.
* **Prevenção de Duplicidade:** Tratamento de erros (`Error Code: 1062`) para evitar logins repetidos no banco.

---

##  Arquitetura do Código (`app.py`)
O código está organizado em blocos lógicos para facilitar a manutenção e escalabilidade:
1. **Configurações e Imports**
2. **Método Inicializador (Setup de Janela)**
3. **Funções de Banco de Dados:** Conexões e Queries.
4. **Fluxo de Autenticação:** Telas e validação de login.
5. **Estrutura Base do Painel:** Construção da Sidebar e Dashboard inicial.
6. **Subtelas (Interfaces):** Formulários de cadastro e visões específicas por cargo.
7. **Lógica de Negócios e Ações:** Processamento de inputs, cálculos e formatações (Bastidores).
