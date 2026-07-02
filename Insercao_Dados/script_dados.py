import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from faker import Faker


np.random.seed(42)  # Geração de sementes aleatórias para garantir a reproducibilidade dos resultados
fake = Faker('pt_BR')  # Geração de dados falsos em português
Faker.seed(8)

print("Gerando dados...")

# Data de referência do "hoje" do dataset — usada para decidir quem está
# ativo e para não deixar nenhum evento (admissão, atendimento, visita etc.)
# acontecer no futuro.
REFERENCE_DATE = datetime(2026, 6, 26)

# =========================================================
# 1. Tabela "Prontuário de Usuários"
# =========================================================

Id_usuario = [f"USR{i:04d}" for i in range(1, 6501)]
nome = [fake.name() for _ in range(6500)]
sexo = np.random.choice(['Masculino', 'Feminino'], size=6500)
Nome_Familiar = [fake.name() for _ in range(6500)]
raca = ["Branca", "Preta", "Parda", "Amarela", "Indígena"]

idades = np.random.randint(0, 96, size=6500)
rua = [fake.street_name() for _ in range(6500)]
bairro = [fake.neighborhood() for _ in range(6500)]
pcd = ['Não há nenhuma condição.',
       'Deficiência Física',
       'Deficiência Mental',
       'Deficiência Visual',
       'Deficiência Auditiva']
pcd_probs = np.array([0.75, 0.10, 0.10, 0.05, 0.05])
pcd_probs /= pcd_probs.sum()
Telefone = [fake.phone_number() for _ in range(6500)]

usuarios_data = []
for i, uid in enumerate(Id_usuario):
    idade = idades[i]
    dt_nascimento = REFERENCE_DATE - timedelta(days=int(idade * 365.25) + int(np.random.randint(0, 300)))
    usuarios_data.append({
        'Id_usuario': uid,
        'Nome': nome[i],
        'Idade': int(idade),
        'Sexo': sexo[i],
        'Raca': np.random.choice(raca),
        'Nome_Familiar': Nome_Familiar[i],
        'Rua': rua[i],
        'Bairro': bairro[i],
        'PCD': np.random.choice(pcd, p=pcd_probs),
        'Telefone': Telefone[i],
        'Dt_Nascimento': dt_nascimento.strftime('%d-%m-%Y')
    })

df_usuarios = pd.DataFrame(usuarios_data)
print(f"Inserção de dados de usuários concluída! ({len(df_usuarios)} linhas)")

# =========================================================
# 2. Tabela "Técnicos"
# =========================================================

N_TECNICOS = 80
N_TECNICOS_ATIVOS = 10  # <- Requisito 1: só 10 técnicos ativos (não demitidos) em 2026

Id_tecnico = [f"TEC{i:02d}" for i in range(1, N_TECNICOS + 1)]
nome_tecnico = [fake.name() for _ in range(N_TECNICOS)]
sexo_tecnico = np.random.choice(['Masculino', 'Feminino'], size=N_TECNICOS)
cargos = ['Assistente Social', 'Psicólogo']
campos_atuacao = ['Crianças e Adolescentes', 'Terceira Idade', 'Jovens Infratores', 'PCD']
salas = [f'Sala {i}' for i in range(1, 6)]
escalas_tecnico = ["Segunda, terça e quarta.", "Terça, quarta e sexta.", "Segunda, quarta e quinta.",
                    "Segunda, quinta e sexta.", "Terça, quinta e sexta."]
turnos_tecnico = ["8h às 17h", "Somente a tarde.", "Somente a manhã.", "9h às 18h", "9h às 15h"]
contratos = ['Concurso Público', 'CLT']

tecnicos_ativos_idx = set(np.random.choice(range(1, N_TECNICOS + 1), size=N_TECNICOS_ATIVOS, replace=False))

tecnicos_data = []
for i, uid in enumerate(Id_tecnico, start=1):
    if i in tecnicos_ativos_idx:
        ano_admissao = np.random.randint(2015, 2026)
        dt_admissao = datetime(ano_admissao, np.random.randint(1, 12), np.random.randint(1, 28))
        dt_desligamento = None
    else:
        ano_admissao = np.random.randint(2015, 2025)
        dt_admissao = datetime(ano_admissao, np.random.randint(1, 12), np.random.randint(1, 28))
        dias_ate_desligamento = int(np.random.randint(180, 1800))
        dt_desligamento = dt_admissao + timedelta(days=dias_ate_desligamento)
        # Garante que o desligamento realmente aconteceu antes de hoje
        if dt_desligamento >= REFERENCE_DATE:
            dt_desligamento = REFERENCE_DATE - timedelta(days=int(np.random.randint(30, 365)))
        if dt_desligamento <= dt_admissao:
            dt_desligamento = dt_admissao + timedelta(days=90)

    tecnicos_data.append({
        'Id_tecnico': uid,
        'Nome': nome_tecnico[i - 1],
        'Sexo': sexo_tecnico[i - 1],
        'Cargo': np.random.choice(cargos),
        'Campo_Atuacao': np.random.choice(campos_atuacao),
        'Sala': np.random.choice(salas),
        'Escala': np.random.choice(escalas_tecnico),
        'Turno': np.random.choice(turnos_tecnico),
        'Contrato': np.random.choice(contratos),
        'Dt_Admissao': dt_admissao.strftime('%d-%m-%Y'),
        'Dt_Desligamento': dt_desligamento.strftime('%d-%m-%Y') if dt_desligamento else None
    })

df_tecnicos = pd.DataFrame(tecnicos_data)
n_ativos_check = df_tecnicos['Dt_Desligamento'].isna().sum()
print(f"Inserção de dados de técnicos concluída! ({len(df_tecnicos)} linhas, {n_ativos_check} ativos em 2026)")

# Lookup rápido (datetime) de admissão/desligamento de cada técnico — usado
# em todo o resto do script para validar se um técnico estava empregado
# em uma determinada data.
tecnico_datas = {
    t['Id_tecnico']: (
        datetime.strptime(t['Dt_Admissao'], '%d-%m-%Y'),
        datetime.strptime(t['Dt_Desligamento'], '%d-%m-%Y') if t['Dt_Desligamento'] else None
    )
    for t in tecnicos_data
}


def tecnico_empregado_em(tid, data_ref):
    """True se o técnico `tid` estava empregado na data `data_ref`."""
    admissao, desligamento = tecnico_datas[tid]
    return admissao <= data_ref and (desligamento is None or data_ref <= desligamento)


# =========================================================
# 3. Violações
# =========================================================

violacoes_lista = ["Negligência", "Abuso Psicológico", "Abuso Sexual", "Financeira",
                    "Patrimonial", "Social", "Medida Sócio Educativa"]
descricao_violacoes = [
    "A omissão de um cuidado necessário.",
    "É uma forma de violência baseada em manipulação, controle e desvalorização. Envolve xingamentos, ameaças e chantagens, ou táticas sutis como ignorar sentimentos e isolar a vítima.",
    "Qualquer atividade ou contato sexual não consensual, seja por uso de força, ameaça, coação, ou por manipulação de quem não tem capacidade de consentir ou compreender a situação.",
    "É caracterizada pelo uso indevido, manipulação ou controle ilegal dos recursos econômicos de uma pessoa. Isso inclui reter, subtrair, destruir bens, forçar o endividamento ou impedir a vítima de gerir o próprio dinheiro para criar dependência.",
    "É qualquer conduta que configure retenção, subtração, destruição parcial ou total de bens, instrumentos de trabalho, documentos pessoais ou recursos econômicos de uma pessoa.",
    "É o uso intencional da força ou poder por indivíduos, grupos ou pela comunidade para coagir, oprimir ou causar danos a outros.",
    "São sanções legais aplicadas pelo Estado a adolescentes (entre 12 e 18 anos incompletos) que cometeram um ato infracional. Diferente das penas adultas, elas possuem caráter pedagógico e protetivo, visando responsabilizar o jovem, promover sua reinserção social e garantir seus direitos"
]

df_violacoes = pd.DataFrame({
    'Id_Violacao': [f"VIO{i:02d}" for i in range(1, len(violacoes_lista) + 1)],
    'Violacao': violacoes_lista,
    'Descricao': descricao_violacoes
})

pcd_usuarios_ids = df_usuarios[df_usuarios['PCD'] != 'Não há nenhuma condição.']['Id_usuario'].values
geral_usuarios_ids = df_usuarios['Id_usuario'].values

# =========================================================
# 4/5/6. Tabelas "Casos", "Caso_Violacao" e "Caso_Acompanhado"
# =========================================================

origens = ["MP", "CRAS", "Hospital", "Disque 100", "Denúncia Espontânea", "Secretaria de Educação"]
status_opcoes = ['Ativo', 'Desligado', 'Em Plantão', 'Religado']
motivos = ["Atingiu maioridade.", "Caso transferido para outro setor.", "Não há mais violação de direitos.",
           "Caso encerrado por decisão judicial.", "Caso encerrado por decisão administrativa."]


def campo_compativel(campo, is_socioeducativa):
    if is_socioeducativa:
        return campo == "Jovens Infratores"
    return campo != "Jovens Infratores"


casos_data = []
caso_violacao_data = []
caso_acompanhado_data = []

# Guarda, para cada caso, quem é o técnico responsável "atual" (final),
# se houve transferência e, em caso positivo, quem era o técnico anterior
# e em que data a troca aconteceu. É usado depois nos Atendimentos e Visitas
# para nunca atribuir uma data a um técnico que já não estava mais empregado
# naquele momento e para escolher corretamente quem estava
# de fato acompanhando o caso naquela data.
caso_tecnico_info = {}

for i in range(1, 7001):
    cid = f"CAS{i:04d}"
    ano_abertura = np.random.randint(2015, 2026)
    dt_abertura = datetime(ano_abertura, np.random.randint(1, 12), np.random.randint(1, 28))
    if dt_abertura > REFERENCE_DATE:
        dt_abertura = datetime(2026, 5, 1)

    is_socioeducativa = i % 10 == 0

    if is_socioeducativa:
        vios_escolhida = ["VIO07"]  # Medida Sócio Educativa
    else:
        vios_escolhida = list(np.random.choice(df_violacoes['Id_Violacao'].values[:6],
                                                 size=np.random.randint(1, 4), replace=False))

    # --- Desfecho do caso é decidido ANTES da escolha do técnico, pois é
    # preciso saber até quando o caso ficou aberto para validar se o
    # técnico continuou empregado durante todo esse período. ---
    status = np.random.choice(status_opcoes)
    dt_encerramento_dt = None
    motivo_encerramento = None
    if status != "Ativo":
        if i <= 700:
            dt_encerramento_dt = dt_abertura + timedelta(days=int(np.random.randint(1825, 2500)))
        else:
            dt_encerramento_dt = dt_abertura + timedelta(days=int(np.random.randint(60, 400)))

        if dt_encerramento_dt > REFERENCE_DATE:
            dt_encerramento_dt, motivo_encerramento, status = None, None, "Ativo"
        else:
            motivo_encerramento = np.random.choice(motivos[:-1])

    dt_encerramento_str = dt_encerramento_dt.strftime('%d-%m-%Y') if dt_encerramento_dt else None
    # Se o caso está ativo, ele precisa de um técnico empregado até HOJE;
    # se está encerrado, precisa de um técnico empregado até a data de encerramento.
    efetiva_data_fim = dt_encerramento_dt if dt_encerramento_dt is not None else REFERENCE_DATE

    # --- Seleção do técnico responsável, com transferência quando necessário ---
    candidatos_completos = [
        t for t in tecnicos_data
        if campo_compativel(t['Campo_Atuacao'], is_socioeducativa)
        and tecnico_empregado_em(t['Id_tecnico'], dt_abertura)
        and tecnico_empregado_em(t['Id_tecnico'], efetiva_data_fim)
    ]

    tid_anterior = None
    dt_transferencia_dt = None

    if candidatos_completos:
        # Um único técnico cobre o caso do início ao fim: não há transferência.
        t_final = candidatos_completos[np.random.randint(len(candidatos_completos))]
        tid_final = t_final['Id_tecnico']
        especialidade = t_final['Campo_Atuacao']
    else:
        # Ninguém cobre o período inteiro -> alguém pegou o caso no início
        # e precisou repassá-lo para outro técnico continuar até o fechamento.
        candidatos_iniciais = [
            t for t in tecnicos_data
            if campo_compativel(t['Campo_Atuacao'], is_socioeducativa)
            and tecnico_empregado_em(t['Id_tecnico'], dt_abertura)
        ]
        if not candidatos_iniciais:
            candidatos_iniciais = [t for t in tecnicos_data
                                    if campo_compativel(t['Campo_Atuacao'], is_socioeducativa)] or tecnicos_data

        t_inicial = candidatos_iniciais[np.random.randint(len(candidatos_iniciais))]
        admissao_i, desligamento_i = tecnico_datas[t_inicial['Id_tecnico']]

        if desligamento_i is not None and desligamento_i < efetiva_data_fim:
            dt_transferencia_dt = desligamento_i
            candidatos_finais = [
                t for t in tecnicos_data
                if t['Id_tecnico'] != t_inicial['Id_tecnico']
                and campo_compativel(t['Campo_Atuacao'], is_socioeducativa)
                and tecnico_datas[t['Id_tecnico']][0] <= efetiva_data_fim
                and (tecnico_datas[t['Id_tecnico']][1] is None or tecnico_datas[t['Id_tecnico']][1] >= efetiva_data_fim)
            ]
            if not candidatos_finais:
                # Último recurso: relaxa a especialidade, priorizando alguém que
                # cobre até o fim do caso (ideal: um dos técnicos ativos hoje).
                candidatos_finais = [
                    t for t in tecnicos_data
                    if t['Id_tecnico'] != t_inicial['Id_tecnico']
                    and tecnico_datas[t['Id_tecnico']][0] <= efetiva_data_fim
                    and (tecnico_datas[t['Id_tecnico']][1] is None or tecnico_datas[t['Id_tecnico']][1] >= efetiva_data_fim)
                ]

            if candidatos_finais:
                t_final = candidatos_finais[np.random.randint(len(candidatos_finais))]
                tid_final = t_final['Id_tecnico']
                tid_anterior = t_inicial['Id_tecnico']
                especialidade = t_final['Campo_Atuacao']
            else:
                # Não achou substituto (situação rara): mantém o técnico inicial.
                tid_final = t_inicial['Id_tecnico']
                dt_transferencia_dt = None
                especialidade = t_inicial['Campo_Atuacao']
        else:
            tid_final = t_inicial['Id_tecnico']
            especialidade = t_inicial['Campo_Atuacao']

    dt_transferencia_str = dt_transferencia_dt.strftime('%d-%m-%Y') if dt_transferencia_dt else None

    caso_tecnico_info[cid] = {
        'final': tid_final,
        'anterior': tid_anterior,
        'transferencia': dt_transferencia_dt,
    }

    # --- Escolha do(s) usuário(s), considerando a especialidade do técnico responsável ---
    if is_socioeducativa:
        usuarios_potenciais = df_usuarios[df_usuarios['Idade'] >= 12]['Id_usuario'].values
        if len(usuarios_potenciais) == 0:
            usuarios_potenciais = geral_usuarios_ids
        usuarios_escolhido = np.random.choice(usuarios_potenciais, size=1, replace=False)
    elif especialidade == 'PCD' and len(pcd_usuarios_ids) > 0:
        usuarios_escolhido = np.random.choice(pcd_usuarios_ids, size=np.random.randint(1, 3), replace=False)
    elif especialidade == 'Crianças e Adolescentes':
        usuarios_potenciais = df_usuarios[df_usuarios['Idade'] < 18]['Id_usuario'].values
        if len(usuarios_potenciais) == 0:
            usuarios_potenciais = geral_usuarios_ids
        usuarios_escolhido = np.random.choice(usuarios_potenciais, size=np.random.randint(1, 3), replace=False)
    else:
        usuarios_escolhido = np.random.choice(geral_usuarios_ids, size=np.random.randint(1, 3), replace=False)

    for u in usuarios_escolhido:
        caso_acompanhado_data.append({"Id_caso": cid, "Id_usuario": u})

    for v in vios_escolhida:
        caso_violacao_data.append({"Id_caso": cid, "Id_violacao": v})

    casos_data.append({
        "Id_caso": cid,
        "Origem": np.random.choice(origens),
        "Dt_Abertura": dt_abertura.strftime('%d-%m-%Y'),
        "Status": status,
        "Dt_Encerramento": dt_encerramento_str,
        "Motivo_Desligamento": motivo_encerramento,
        "Id_tecnico": tid_final,
        "Id_tecnico_anterior": tid_anterior,
        "Dt_Transferencia": dt_transferencia_str,
    })

df_casos = pd.DataFrame(casos_data)
df_caso_violacao = pd.DataFrame(caso_violacao_data)
df_caso_acompanhado = pd.DataFrame(caso_acompanhado_data)

n_transferidos = df_casos['Id_tecnico_anterior'].notna().sum()
print(f"Inserção de dados de casos concluída! ({len(df_casos)} linhas, {n_transferidos} com transferência de técnico)")
print(f"Inserção de dados de caso_violacao concluída! ({len(df_caso_violacao)} linhas)")
print(f"Inserção de dados de caso_acompanhado concluída! ({len(df_caso_acompanhado)} linhas)")


def tecnico_responsavel_caso(id_caso, data_ref):
    """Retorna o técnico que estava de fato acompanhando `id_caso` na data
    `data_ref`, respeitando uma eventual transferência registrada em
    `caso_tecnico_info`, e garantindo que o técnico escolhido estava
    empregado nessa data (Requisito 3 e 4)."""
    info = caso_tecnico_info.get(id_caso)
    if info is None:
        candidato = None
    elif info['transferencia'] is not None and data_ref < info['transferencia']:
        candidato = info['anterior']
    else:
        candidato = info['final']

    if candidato is not None and tecnico_empregado_em(candidato, data_ref):
        return candidato

    # Fallback: qualquer técnico realmente empregado na data em questão.
    validos = [t['Id_tecnico'] for t in tecnicos_data if tecnico_empregado_em(t['Id_tecnico'], data_ref)]
    if validos:
        return validos[np.random.randint(len(validos))]
    # Último recurso (data anterior a qualquer admissão registrada).
    return min(tecnicos_data, key=lambda t: tecnico_datas[t['Id_tecnico']][0])['Id_tecnico']


# =========================================================
# 7. Tabela "Atendimentos_Diarios"
# =========================================================

motivos_atend_opcoes = [
    "Denúncia de violação de direitos sofrida por terceiros.",
    "Denúncia de violação de direitos sofrida pelo próprio usuário.",
    "Reunião com a família do usuário.",
    "Reunião de rede.",
    "Andamento de acompanhamento do caso."
]

status_atend_opcoes = [
    "Encaminhado para referenciação de técnico para acompanhar o caso",
    "Instruções e/ou orientações fornecidas ao usuário.",
    "Atendimento do caso acompanhado.",
    "Encaminhado para outro setor."
]

atendimentos_data = []
for i in range(1, 9001):
    ano_atendimento = np.random.randint(2015, 2026)
    dt_atendimento = datetime(ano_atendimento, np.random.randint(1, 12), np.random.randint(1, 28))
    if dt_atendimento > REFERENCE_DATE:
        dt_atendimento = datetime(2026, 6, 1)

    motivo = np.random.choice(motivos_atend_opcoes)

    cid, uid = "", ""
    nome_usuario, nome_ref = "", ""
    status_atend = np.random.choice(status_atend_opcoes)
    tid = None

    if motivo in ['Andamento de acompanhamento do caso.', 'Reunião com a família do usuário.', 'Reunião de rede.']:
        escolha = np.random.randint(len(caso_acompanhado_data))
        cid = caso_acompanhado_data[escolha]['Id_caso']
        uid = caso_acompanhado_data[escolha]['Id_usuario']

        # Requisitos 3 e 4: usa o técnico que realmente acompanhava o caso
        # NESSA data (antes ou depois de uma eventual transferência), e que
        # estava empregado no momento do atendimento.
        tid = tecnico_responsavel_caso(cid, dt_atendimento)
        nome_ref = df_usuarios[df_usuarios['Id_usuario'] == uid]['Nome'].values[0]

        if np.random.rand() > 0.5:
            nome_usuario = nome_ref
        else:
            nome_usuario = df_usuarios[df_usuarios['Id_usuario'] != uid].sample(n=1).iloc[0]['Nome']

        status_atend = "Atendimento do caso acompanhado."

    elif motivo == "Denúncia de violação de direitos sofrida pelo próprio usuário.":
        if np.random.rand() > 0.4:
            escolha = np.random.randint(len(caso_acompanhado_data))
            cid = caso_acompanhado_data[escolha]['Id_caso']
            uid = caso_acompanhado_data[escolha]['Id_usuario']
            nome_ref = df_usuarios[df_usuarios['Id_usuario'] == uid]['Nome'].values[0]
            nome_usuario = nome_ref
            tid = tecnico_responsavel_caso(cid, dt_atendimento)
        else:  # Vítima não cadastrada
            cid, uid = "", ""
            nome_usuario = fake.name()
            nome_ref = nome_usuario
            tecnicos_validos = [t["Id_tecnico"] for t in tecnicos_data if tecnico_empregado_em(t["Id_tecnico"], dt_atendimento)]
            if tecnicos_validos:
                tid = tecnicos_validos[np.random.randint(len(tecnicos_validos))]
            else:
                tid = min(tecnicos_data, key=lambda t: tecnico_datas[t['Id_tecnico']][0])['Id_tecnico']

        status_atend = "Instruções e/ou orientações fornecidas ao usuário."

    else:  # Denúncia sofrida por terceiros
        if np.random.rand() > 0.3:  # Vítima cadastrada
            escolha = np.random.randint(len(caso_acompanhado_data))
            cid = caso_acompanhado_data[escolha]['Id_caso']
            uid = caso_acompanhado_data[escolha]['Id_usuario']
            nome_ref = df_usuarios[df_usuarios['Id_usuario'] == uid]['Nome'].values[0]
            tid = tecnico_responsavel_caso(cid, dt_atendimento)
        else:  # Sem cadastro
            cid, uid = "", ""
            nome_ref = fake.name()
            tecnicos_validos = [t["Id_tecnico"] for t in tecnicos_data if tecnico_empregado_em(t["Id_tecnico"], dt_atendimento)]
            if tecnicos_validos:
                tid = tecnicos_validos[np.random.randint(len(tecnicos_validos))]
            else:
                tid = min(tecnicos_data, key=lambda t: tecnico_datas[t['Id_tecnico']][0])['Id_tecnico']

        if np.random.rand() > 0.5:
            nome_usuario = f"Denunciante Anônimo n° {i}"
        else:
            if uid != "":
                nome_usuario = df_usuarios[df_usuarios["Id_usuario"] != uid].sample(n=1).iloc[0]["Nome"]
            else:
                nome_usuario = df_usuarios.sample(n=1).iloc[0]["Nome"]

        status_atend = "Encaminhado para referenciação de técnico para acompanhar o caso."

    atendimentos_data.append({
        "Id_atendimento": f"ATD{i:04d}",
        "Dt_Atendimento": dt_atendimento.strftime('%d-%m-%Y'),
        "Nome_usuario_atendido": nome_usuario,
        "Nome_usuario_referencia": nome_ref,
        "Id_usuario": uid,
        "Id_caso": cid,
        "Motivo_Atendimento": motivo,
        "Id_tecnico": tid,
        "Status_Atendimento": status_atend
    })

df_atendimentos = pd.DataFrame(atendimentos_data)
print(f"Inserção de dados de atendimentos concluída! ({len(df_atendimentos)} linhas)")

# =========================================================
# 9a. Tabela "Motoristas" 
# =========================================================

N_MOTORISTAS = 54
N_MOTORISTAS_ATIVOS = 10  # <- Requisito 2: só 10 motoristas ativos em 2026

setores = ["CRAS X", "CRAS Y", "CREAS", "Centro POP", "Gerência", "CEAM"]
modelos = ["Fiat Argo", "Chevrolet Onix Plus", "Fiat Mobi", "Fiat Cronos"]
escalas_motorista = ["Segunda à Sexta.", "Terça, quarta e quinta.", "Quarta, Sexta e Sábado."]
turnos_motorista = ["8h às 17h.", "9h às 18h.", "7h às 16h.", "13h às 22h."]

motoristas_ativos_idx = set(np.random.choice(range(1, N_MOTORISTAS + 1), size=N_MOTORISTAS_ATIVOS, replace=False))
mapa_pos_ativo = {idx: pos for pos, idx in enumerate(sorted(motoristas_ativos_idx))}

motoristas_data = []
for i in range(1, N_MOTORISTAS + 1):
    mid = f"MOT{i:02d}"
    tel_mot = fake.cellphone_number()
    if i in motoristas_ativos_idx:
        pos = mapa_pos_ativo[i]
        ano_adm = np.random.randint(2015, 2026)
        dt_adm = datetime(ano_adm, np.random.randint(1, 12), np.random.randint(1, 28))
        dt_des = None
        escala_mot = escalas_motorista[pos % len(escalas_motorista)]
        turno_mot = turnos_motorista[pos % len(turnos_motorista)]
        setor_mot = setores[pos % len(setores)]
    else:
        ano_adm = np.random.randint(2015, 2025)
        dt_adm = datetime(ano_adm, np.random.randint(1, 12), np.random.randint(1, 28))
        dias_ate_desligamento = int(np.random.randint(180, 1800))
        dt_des = dt_adm + timedelta(days=dias_ate_desligamento)
        if dt_des >= REFERENCE_DATE:
            dt_des = REFERENCE_DATE - timedelta(days=int(np.random.randint(30, 365)))
        if dt_des <= dt_adm:
            dt_des = dt_adm + timedelta(days=90)
        escala_mot = np.random.choice(escalas_motorista)
        turno_mot = np.random.choice(turnos_motorista)
        setor_mot = np.random.choice(setores)

    motoristas_data.append({
        "Id_motorista": mid,
        "Nome": fake.name(),
        "Escala": escala_mot,
        "Turno": turno_mot,
        "Placa_Carro": f"ABC-{np.random.randint(1000, 9999)}",
        "Modelo_Carro": np.random.choice(modelos),
        "Telefone_Celular": tel_mot,
        "Setor_atribuido": setor_mot,
        "Contrato": np.random.choice(contratos),
        "Dt_Admissao": dt_adm.strftime("%d-%m-%Y"),
        "Dt_Desligamento": dt_des.strftime("%d-%m-%Y") if dt_des else ""
    })

df_motoristas = pd.DataFrame(motoristas_data)
n_motoristas_ativos_check = (df_motoristas['Dt_Desligamento'] == "").sum()
print(f"Inserção de dados de motoristas concluída! ({len(df_motoristas)} linhas, {n_motoristas_ativos_check} ativos em 2026)")

motorista_datas = {
    m['Id_motorista']: (
        datetime.strptime(m['Dt_Admissao'], '%d-%m-%Y'),
        datetime.strptime(m['Dt_Desligamento'], '%d-%m-%Y') if m['Dt_Desligamento'] else None
    )
    for m in motoristas_data
}


def motorista_empregado_em(mid, data_ref):
    admissao, desligamento = motorista_datas[mid]
    return admissao <= data_ref and (desligamento is None or data_ref <= desligamento)


# =========================================================
# 8. Tabela "Visitas_Tecnico"
# =========================================================

visitas_data = []
for i in range(1, 7801):
    ano_v = np.random.randint(2015, 2026)
    dt_v = datetime(ano_v, np.random.randint(1, 12), np.random.randint(1, 28))
    if dt_v > REFERENCE_DATE:
        dt_v = datetime(2026, 6, 1)

    if np.random.rand() > 0.4:
        escolha = np.random.randint(len(caso_acompanhado_data))
        cid = caso_acompanhado_data[escolha]["Id_caso"]
        uid = caso_acompanhado_data[escolha]["Id_usuario"]
        # Requisitos 3 e 4: mesmo tratamento usado nos atendimentos.
        tid = tecnico_responsavel_caso(cid, dt_v)
        nome_v = df_usuarios[df_usuarios["Id_usuario"] == uid]["Nome"].values[0]
    else:
        cid, uid = "", ""
        tecnicos_validos = [t["Id_tecnico"] for t in tecnicos_data if tecnico_empregado_em(t["Id_tecnico"], dt_v)]
        tid = tecnicos_validos[np.random.randint(len(tecnicos_validos))] if tecnicos_validos else \
            min(tecnicos_data, key=lambda t: tecnico_datas[t['Id_tecnico']][0])['Id_tecnico']
        nome_v = fake.name() + " (não cadastrado)"

    motoristas_validos = [m["Id_motorista"] for m in motoristas_data if motorista_empregado_em(m["Id_motorista"], dt_v)]
    id_motorista = motoristas_validos[np.random.randint(len(motoristas_validos))] if motoristas_validos else \
        min(motoristas_data, key=lambda m: motorista_datas[m['Id_motorista']][0])['Id_motorista']

    visitas_data.append({
        "Id_visita": f"VIS{i:04d}",
        "Dt_Visita": dt_v.strftime("%d-%m-%Y"),
        "Id_tecnico": tid,
        "Nome_usuario_visitado": nome_v,
        "Id_usuario": uid,
        "Id_caso": cid,
        "Id_motorista": id_motorista
    })

df_visitas = pd.DataFrame(visitas_data)
print(f"Inserção de dados de visitas concluída! ({len(df_visitas)} linhas)")

# =========================================================
# 9b. Tabela "Alocacao_Motorista"
# =========================================================

alocacao_data = []
for i in range(1, 1001):
    ano_aloc = np.random.randint(2015, 2027)
    dt_aloc = datetime(ano_aloc, np.random.randint(1, 12), np.random.randint(1, 28))
    if dt_aloc > REFERENCE_DATE:
        dt_aloc = datetime(2026, 4, 1)

    motoristas_validos = [m["Id_motorista"] for m in motoristas_data if motorista_empregado_em(m["Id_motorista"], dt_aloc)]
    id_motorista = motoristas_validos[np.random.randint(len(motoristas_validos))] if motoristas_validos else \
        min(motoristas_data, key=lambda m: motorista_datas[m['Id_motorista']][0])['Id_motorista']

    alocacao_data.append({
        "Id_motorista": id_motorista,
        "Setor_emprestado": np.random.choice(setores),
        "Dt_Alocacao": dt_aloc.strftime("%d-%m-%Y")
    })

df_alocacao = pd.DataFrame(alocacao_data)
print(f"Inserção de dados de alocação de motoristas concluída! ({len(df_alocacao)} linhas)")

# =========================================================
# Exportação para Excel
# =========================================================

with pd.ExcelWriter("Dataset_Assistencia_Social.xlsx", engine="openpyxl") as writer:
    df_usuarios.to_excel(writer, sheet_name="Prontuário de Usuários", index=False)
    df_tecnicos.to_excel(writer, sheet_name="Técnicos", index=False)
    df_violacoes.to_excel(writer, sheet_name="Violações", index=False)
    df_casos.to_excel(writer, sheet_name="Casos", index=False)
    df_caso_violacao.to_excel(writer, sheet_name="Caso_Violacao", index=False)
    df_caso_acompanhado.to_excel(writer, sheet_name="Caso_Acompanhamento", index=False)
    df_atendimentos.to_excel(writer, sheet_name="Atendimentos_Diarios", index=False)
    df_visitas.to_excel(writer, sheet_name="Visitas_Tecnico", index=False)
    df_motoristas.to_excel(writer, sheet_name="Motoristas", index=False)
    df_alocacao.to_excel(writer, sheet_name="Alocacao_Motorista", index=False)

print("Dataset gerado!")