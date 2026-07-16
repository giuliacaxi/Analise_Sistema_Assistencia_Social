import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

print("Conectando ao banco de dados MySQL...")
USER = os.getenv("DB_USER", "root")
PASSWORD = os.getenv("DB_PASSWORD", "")
HOST = os.getenv("DB_HOST", "localhost")
DATABASE = os.getenv("DB_NAME", "creas_system")

engine = create_engine(f"mysql+mysqlconnector://{USER}:{PASSWORD}@{HOST}/{DATABASE}")

arquivo_excel = "Dataset_Assistencia_Social.xlsx"

print("Lendo as abas do arquivo Excel...")
df_usuarios = pd.read_excel(arquivo_excel, sheet_name="Prontuário de Usuários")
df_tecnicos = pd.read_excel(arquivo_excel, sheet_name="Técnicos")
df_violacoes = pd.read_excel(arquivo_excel, sheet_name="Violações")
df_casos = pd.read_excel(arquivo_excel, sheet_name="Casos")
df_registro_violacoes_casos = pd.read_excel(arquivo_excel, sheet_name="Caso_Violacao")
df_acompanhamento_casos = pd.read_excel(arquivo_excel, sheet_name="Caso_Acompanhamento")
df_atendimentos_diarios = pd.read_excel(arquivo_excel, sheet_name="Atendimentos_Diarios")
df_motoristas = pd.read_excel(arquivo_excel, sheet_name="Motoristas")
df_visitas_tecnico = pd.read_excel(arquivo_excel, sheet_name="Visitas_Tecnico")
df_alocacao_motorista = pd.read_excel(arquivo_excel, sheet_name="Alocacao_Motorista")

df_casos.columns = df_casos.columns.str.lower()
if 'id_caso' in df_casos.columns:
    df_casos = df_casos.drop(columns=['id_caso'])

# 4. Enviar os dados de volta para a tabela vazia do MySQL
df_casos.to_sql('casos', con=engine, if_exists='append', index=False)

print("Dados restaurados com sucesso com IDs numéricos e sequenciais!")

# Ajustando maiúsculas e minúsculas para não dar KeyError
df_tecnicos.columns = df_tecnicos.columns.str.lower()

#Preparando logins e senhas dos tecnicos

if "login" not in df_tecnicos.columns:
    print("Gerando logins padrão para os Técnicos...")
    df_tecnicos["login"] = df_tecnicos["nome"].str.split().str[0].str.lower() + df_tecnicos["id_tecnico"].astype(str).str.lower()
    df_tecnicos["senha"] = "123456"

if "nivel_acesso" not in df_tecnicos.columns:
    df_tecnicos["nivel_acesso"] = "Técnico" 

# Criação das tabelas de coordenadores e outros funcionários
print("Criando tabelas de Coordenadores e Funcionários...")
with engine.connect() as con:
    con.execute(text("""
        CREATE TABLE IF NOT EXISTS coordenadores (
            id_coordenador VARCHAR(10) PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            dt_admissao DATE NOT NULL,
            dt_desligamento DATE,
            login VARCHAR(50) UNIQUE NOT NULL,
            senha VARCHAR(255) NOT NULL
        )
    """))
    
    con.execute(text("""
        CREATE TABLE IF NOT EXISTS funcionarios (
            id_funcionario VARCHAR(10) PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            cargo ENUM('Administrador','Analista de Dados', 'Recepcionista', 'Administrador de Banco de Dados') NOT NULL,
            dt_admissao DATE NOT NULL,
            dt_desligamento DATE,
            login VARCHAR(50) UNIQUE NOT NULL,
            senha VARCHAR(255) NOT NULL
        )
    """))
    
    # Inserindo dados iniciais padrões para conseguir logar no sistema pela primeira vez
    con.execute(text("INSERT IGNORE INTO coordenadores VALUES ('COR01', 'Marcos Aurélio Gomes', '2022-01-01', 'NULL', 'coordenador', '123456')"))
    con.execute(text("INSERT IGNORE INTO funcionarios VALUES ('ADM01', 'Larissa Almeida', 'Administrador', '2023-01-01', 'NULL', 'funcionario', '123456')"))
    con.commit()

# Exportando os dados do Excel para o MySQL
print("Exportando tabelas do Excel para o MySQL...")
df_usuarios.to_sql("usuarios", con=engine, if_exists="replace", index=False)
df_tecnicos.to_sql("tecnicos", con=engine, if_exists="replace", index=False)
df_violacoes.to_sql("violacoes", con=engine, if_exists="replace", index=False)
df_casos.to_sql("casos", con=engine, if_exists="replace", index=False)
df_registro_violacoes_casos.to_sql("casos_violacao", con=engine, if_exists="replace", index=False)
df_acompanhamento_casos.to_sql("caso_acompanhamento", con=engine, if_exists="replace", index=False)
df_atendimentos_diarios.to_sql("atendimentos_diarios", con=engine, if_exists="replace", index=False)
df_motoristas.to_sql("motoristas", con=engine, if_exists="replace", index=False)
df_visitas_tecnico.to_sql("visitas_tecnico", con=engine, if_exists="replace", index=False)
df_alocacao_motorista.to_sql("alocacao_motorista", con=engine, if_exists="replace", index=False)

# Funções para gerar IDs únicos e inserir novos funcionários e coordenadores
def gerar_proximo_id(tabela, coluna_id, prefixo):
    with engine.connect() as con:
        resultado = con.execute(text(f"SELECT {coluna_id} FROM {tabela} WHERE {coluna_id} LIKE '{prefixo}%' ORDER BY {coluna_id} DESC LIMIT 1"))
        ultimo_id = resultado.fetchone()
        if ultimo_id is None:
            return f"{prefixo}01"
        else:
            numero = int(ultimo_id[0][len(prefixo):]) + 1
            return f"{prefixo}{numero:02d}"

def inserir_novo_funcionario(nome, cargo, login, senha):
    mapeamento_siglas = {
        "Administrador": "ADM",
        "Analista de Dados": "ANA",
        "Recepcionista": "REC",
        "Administrador de Banco de Dados": "DBA"
    }
    sigla = mapeamento_siglas.get(cargo, "FUC")  # FUC = Funcionário Comum, caso o cargo não esteja mapeado
    novo_id = gerar_proximo_id("funcionarios", "id_funcionario", sigla)
    
    with engine.connect() as con:
        con.execute(text("""
            INSERT INTO funcionarios (id_funcionario, nome, cargo, dt_admissao, dt_desligamento, login, senha)
            VALUES (:id, :nome, :cargo, CURDATE(), NULL, :login, :senha)
        """), {"id": novo_id, "nome": nome, "cargo": cargo, "login": login, "senha": senha})
        con.commit()
    print(f"Funcionário {nome} inserido com sucesso! ID: {novo_id}")

def alternar_coordenador_sistema(nome_novo, login_novo, senha_nova):
    novo_id = gerar_proximo_id("coordenadores", "id_coordenador", "COR")
    with engine.connect() as con:
        # Fecha o mandato do coordenador atual definindo a data de desligamento como hoje
        con.execute(text("UPDATE coordenadores SET dt_desligamento = CURDATE() WHERE dt_desligamento IS NULL"))
        # Insere o novo coordenador ativo
        con.execute(text("""
            INSERT INTO coordenadores (id_coordenador, nome, dt_admissao, dt_desligamento, login, senha)
            VALUES (:id, :nome, CURDATE(), NULL, :login, :senha)
        """), {"id": novo_id, "nome": nome_novo, "login": login_novo, "senha": senha_nova})
        con.commit()
    print(f"Novo Coordenador ativo! ID Gerado: {novo_id}")

# Executa testes de cadastro se rodar esse script diretamente
if __name__ == "__main__":
    inserir_novo_funcionario("Paula Souza", "Administrador", "paula.adm", "123456")
    alternar_coordenador_sistema("Mariana Costa", "mariana.coord", "123456")
    print("Carga inicial finalizada perfeitamente no MySQL!")