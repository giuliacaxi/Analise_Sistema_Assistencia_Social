import customtkinter as ctk
from tkinter import messagebox
import mysql.connector
import os
import calendar
from datetime import date
from dotenv import load_dotenv

load_dotenv()

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# ---------------------------------------------------------------------------
# Paleta fixa usada na sidebar / cabeçalho / tela inicial para dar uma cara
# mais limpa e consistente ao sistema
# ---------------------------------------------------------------------------
COR_SIDEBAR = "#26418f"
COR_SIDEBAR_HOVER = "#3a5aad"
COR_SIDEBAR_LINHA = "#4a63a8"
COR_FUNDO = "#fdf8ee"
COR_TEXTO_TITULO = "#1a1a1a"
COR_LINHA_DIVISORIA = "#dcd7c8"
COR_ACCENT = "#26418f"


class AppSistemaSocial(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Controle de Dados")
        self.geometry("1000x650")

        self.id_usuario_logado = None
        self.usuario_logado = None
        self.nivel_acesso_logado = None

        self.tela_login()

    # -----------------------------------------------------------------
    # Banco de dados
    # -----------------------------------------------------------------
    def conectar_banco_dados(self):
        try:
            connection = mysql.connector.connect(
                host=os.getenv("DB_HOST"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_NAME")
            )
            print("Conexão com o banco de dados estabelecida com sucesso.")
            return connection
        except mysql.connector.Error as err:
            messagebox.showerror("Erro de Conexão", f"Erro ao conectar ao banco de dados: {err}")
            return None

    def executar_query(self, query, valores=None, fetch=False, commit=False):
        """
        Helper central para não repetir abrir/fechar conexão em cada tela.
        fetch=True  -> retorna lista de dicts (SELECT)
        commit=True -> executa INSERT/UPDATE/DELETE e comita
        Retorna (sucesso: bool, dados_ou_erro)
        """
        con = self.conectar_banco_dados()
        if not con:
            return False, "Sem conexão com o banco de dados."

        cursor = con.cursor(dictionary=True) if fetch else con.cursor()
        try:
            cursor.execute(query, valores or ())
            if fetch:
                resultado = cursor.fetchall()
                return True, resultado
            if commit:
                con.commit()
                return True, cursor.rowcount
            return True, None
        except mysql.connector.Error as err:
            return False, str(err)
        finally:
            cursor.close()
            con.close()

    # -----------------------------------------------------------------
    # Navegação / limpeza de telas
    # -----------------------------------------------------------------
    def limpar_tela(self):
        for widget in self.winfo_children():
            widget.destroy()

    def tela_login(self):
        self.limpar_tela()
        self.configure(fg_color=COR_FUNDO)

        frame_login = ctk.CTkFrame(self, width=380, height=440, corner_radius=15, fg_color="white",
                                    border_width=1, border_color=COR_LINHA_DIVISORIA)
        frame_login.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(frame_login, text="Controle de Dados || Assistência Social",
                     font=("Arial", 22, "bold"), text_color=COR_ACCENT).pack(pady=(40, 5))
        ctk.CTkLabel(frame_login, text="Faça login para continuar", text_color="gray").pack(pady=(0, 20))

        self.txt_login = ctk.CTkEntry(frame_login, placeholder_text="Usuário", width=280, height=40,
                                       corner_radius=8, border_color=COR_LINHA_DIVISORIA)
        self.txt_login.pack(pady=(0, 10))

        self.txt_senha = ctk.CTkEntry(frame_login, placeholder_text="Senha", show="*", width=280, height=40,
                                       corner_radius=8, border_color=COR_LINHA_DIVISORIA)
        self.txt_senha.pack(pady=(0, 20))

        ctk.CTkButton(frame_login, text="Acessar", width=280, height=40, corner_radius=8,
                      fg_color=COR_ACCENT, hover_color=COR_SIDEBAR_HOVER,
                      font=("Arial", 14, "bold"), command=self.fazer_login).pack(pady=30)

        # Enter no campo de senha também tenta logar
        self.txt_senha.bind("<Return>", lambda event: self.fazer_login())

    def fazer_login(self):
        login = self.txt_login.get().strip()
        senha = self.txt_senha.get().strip()

        if not login or not senha:
            messagebox.showwarning("Erro", "Preencha usuário e senha.")
            return

        # Procura o login nas 3 tabelas que guardam credenciais.
        # A tabela em que o registro é encontrado já indica o "grupo" de acesso;
        # dentro de funcionarios, o campo `cargo` refina qual grupo específico.
        tabelas = [
            ("funcionarios", None),          # cargo vem da própria coluna `cargo`
            ("tecnicos", "Técnico"),         # qualquer cargo aqui = nível Técnico
            ("coordenadores", "Coordenador"),
        ]

        for tabela, nivel_fixo in tabelas:
            query = f"SELECT * FROM {tabela} WHERE login = %s AND senha = %s"
            sucesso, resultado = self.executar_query(query, (login, senha), fetch=True)

            if not sucesso:
                messagebox.showerror("Erro de Conexão", resultado)
                return

            if resultado:
                usuario = resultado[0]

                # Bloqueia login de quem já foi desligado, se a tabela tiver essa coluna
                if usuario.get("dt_desligamento"):
                    messagebox.showerror("Acesso negado", "Este usuário está desligado do sistema.")
                    return

                self.id_usuario_logado = usuario.get("id", login)
                self.usuario_logado = usuario.get("nome", login)
                self.nivel_acesso_logado = nivel_fixo or usuario.get("cargo")
                self.carregar_painel_principal()
                return

        messagebox.showerror("Acesso negado", "Usuário ou senha incorretos.")

    def carregar_painel_principal(self):
        self.limpar_tela()
        self.configure(fg_color=COR_FUNDO)

        # Menu Lateral
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=COR_SIDEBAR)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Título do Menu Lateral
        ctk.CTkLabel(self.sidebar, text="Sistema de Controle\nde Dados - AS", font=("Arial", 17, "bold"),
                     text_color="white", justify="center").pack(pady=(35, 8))
        ctk.CTkLabel(self.sidebar, text=f"Id: {self.id_usuario_logado} | {self.usuario_logado}\n{self.nivel_acesso_logado}",
                     font=("Arial", 11), text_color=("#d7deef"), wraplength=200, justify="center").pack(pady=(0, 15))

        # Linha divisória sob o título
        ctk.CTkFrame(self.sidebar, height=1, fg_color=COR_SIDEBAR_LINHA).pack(fill="x", padx=25, pady=(0, 15))

        # Área que recebe os botões de navegação (fica entre o título e o botão Sair)
        self.frame_botoes_menu = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.frame_botoes_menu.pack(fill="both", expand=True)

        # Painel Direito
        self.conteudo_principal = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.conteudo_principal.pack(side="right", fill="both", expand=True, padx=40, pady=30)

        # Cabeçalho do Painel Direito
        self.header = ctk.CTkFrame(self.conteudo_principal, fg_color="transparent")
        self.header.pack(fill="x", pady=(0, 20))
        self.lbl_titulo_pagina = ctk.CTkLabel(self.header, text="Início", font=("Arial", 28, "bold"),
                                               text_color=COR_TEXTO_TITULO)
        self.lbl_titulo_pagina.pack(side="left")

        # "Olá, nome!" só aparece na página inicial; nas subtelas dá lugar ao botão de voltar
        self.lbl_saudacao = ctk.CTkLabel(self.header, text=f"Olá, {self.usuario_logado}!",
                                          font=("Arial", 24, "bold"), text_color=COR_TEXTO_TITULO)
        self.btn_voltar_inicio = ctk.CTkButton(
            self.header, text="← Voltar ao Início", width=160, height=32, corner_radius=8,
            fg_color="transparent", border_width=1, border_color=COR_LINHA_DIVISORIA,
            text_color=COR_TEXTO_TITULO, hover_color=("#e8e2d0"), font=("Arial", 12, "bold"),
            command=self.ir_para_inicio
        )
        self.lbl_saudacao.pack(side="right")

        # Container onde as subtelas são desenhadas (abaixo do cabeçalho)
        self.area_conteudo = ctk.CTkFrame(self.conteudo_principal, fg_color="transparent")
        self.area_conteudo.pack(fill="both", expand=True)

        # Roteamento de botões no menu lateral
        self.construir_menu_lateral()

        # Botão de logout fixo no rodapé do menu lateral
        ctk.CTkButton(self.sidebar, text="Sair", fg_color="#cf4444", hover_color="#b33636",
                      corner_radius=20, height=38, font=("Arial", 13, "bold"),
                      command=self.tela_login).pack(side="bottom", fill="x", padx=25, pady=25)

        # Carrega o conteúdo da página inicial assim que o painel é montado
        self.ir_para_inicio()

    def ir_para_inicio(self):
        self.limpar_area_conteudo()
        self.lbl_titulo_pagina.configure(text="Início")
        self.btn_voltar_inicio.pack_forget()
        self.lbl_saudacao.pack(side="right")
        self.tela_inicio()

    def preparar_subtela(self, titulo):

        self.limpar_area_conteudo()
        self.lbl_titulo_pagina.configure(text=titulo)
        self.lbl_saudacao.pack_forget()
        self.btn_voltar_inicio.pack(side="right")

    def construir_menu_lateral(self):
        nivel = self.nivel_acesso_logado

        # Botão comum a todos os perfis: volta para a página inicial
        self.criar_botao_menu("Início", self.ir_para_inicio)

        if nivel == "Administrador de Banco de Dados":
            self.criar_botao_menu("Configurações do Sistema", self.tela_dba_config)
            self.criar_botao_menu("Tabelas do Banco de Dados (SQL)", self.tela_dba_sql)
            self.criar_botao_menu("Cadastrar Funcionário", self.tela_dba_cadastro_funcionario)
            self.criar_botao_menu("Cadastrar Coordenador", self.tela_dba_cadastro_coordenador)

        elif nivel == "Coordenador":
            self.criar_botao_menu("Casos dos Técnicos", lambda: self.mudar_subtela("Casos dos Técnicos"))
            self.criar_botao_menu("Painel de Atendimentos", lambda: self.mudar_subtela("Painel de Atendimentos"))
            self.criar_botao_menu("Monitorar Visitas", lambda: self.mudar_subtela("Monitorar Visitas"))
            self.criar_botao_menu("Relatórios Gerenciais", lambda: self.mudar_subtela("Relatórios Gerenciais"))

        elif nivel == "Técnico":
            self.criar_botao_menu("Meus Casos", lambda: self.mudar_subtela("Meus Casos"))
            self.criar_botao_menu("Novo Relatório de Evolução", lambda: self.mudar_subtela("Novo Relatório de Evolução"))
            self.criar_botao_menu("Agendar Visitas", lambda: self.mudar_subtela("Agendar Visitas"))
            self.criar_botao_menu("Minhas reuniões", lambda: self.mudar_subtela("Minhas reuniões"))
            self.criar_botao_menu("Agenda de Atendimentos", lambda: self.mudar_subtela("Agenda de Atendimentos"))

        elif nivel == "Administrador":
            self.criar_botao_menu("Cadastrar Usuário", self.tela_admin_cadastrar_usuario)
            self.criar_botao_menu("Cadastrar Técnico", self.tela_admin_cadastro_tecnico)
            self.criar_botao_menu("Atribuir / Transferir Caso", lambda: self.mudar_subtela("Atribuir / Transferir Caso"))
            self.criar_botao_menu("Visualizar Motoristas", lambda: self.mudar_subtela("Visualizar Motoristas"))

        elif nivel == "Analista de Dados":
            self.criar_botao_menu("Abrir Dashboard", lambda: self.mudar_subtela("Dashboard Analítico"))
            self.criar_botao_menu("Visualizar Dados", lambda: self.mudar_subtela("Visualizar Dados"))

        elif nivel == "Recepcionista":
            self.criar_botao_menu("Registrar Atendimento na Recepção", lambda: self.mudar_subtela("Registrar Atendimento na Recepção"))
            self.criar_botao_menu("Agenda dos Técnicos", lambda: self.mudar_subtela("Agenda dos Técnicos"))
            self.criar_botao_menu("Consultar Cadastros", lambda: self.mudar_subtela("Consultar Usuários (Read-Only)"))

        # Botão comum a todos os perfis: abrir/gerenciar chamados
        if nivel == "Administrador de Banco de Dados":
            self.criar_botao_menu("Gerenciar Chamados", lambda: self.mudar_subtela("Chamados"))
        else:
            self.criar_botao_menu("Chamados", lambda: self.mudar_subtela("Chamados"))

    def criar_botao_menu(self, texto, comando):
        btn = ctk.CTkButton(self.frame_botoes_menu, text=texto, anchor="w", height=40, fg_color="transparent",
                             text_color="white", hover_color=COR_SIDEBAR_HOVER, corner_radius=8,
                             font=("Arial", 13), command=comando)
        btn.pack(fill="x", padx=15, pady=3)

    def limpar_area_conteudo(self):
        # Limpa apenas o container de subtelas, mantendo o cabeçalho fixo
        for widget in self.area_conteudo.winfo_children():
            widget.destroy()

    # -----------------------------------------------------------------
    # Dispatcher central de subtelas
    # -----------------------------------------------------------------
    def mudar_subtela(self, nome_tela):
        mapa_telas = {
            # Técnico
            "Meus Casos": self.tela_meus_casos,
            "Novo Relatório de Evolução": self.tela_novo_relatorio_evolucao,
            "Agendar Visitas": self.tela_agendar_visitas,
            "Minhas reuniões": self.tela_minhas_reunioes,
            "Agenda de Atendimentos": self.tela_agenda_atendimentos_tecnico,
            # Coordenador
            "Casos dos Técnicos": self.tela_casos_dos_tecnicos,
            "Painel de Atendimentos": self.tela_painel_atendimentos,
            "Monitorar Visitas": self.tela_monitorar_visitas,
            "Relatórios Gerenciais": self.tela_relatorios_gerenciais,
            # Administrador
            "Atribuir / Transferir Caso": self.tela_atribuir_transferir_caso,
            "Visualizar Motoristas": self.tela_visualizar_motoristas,
            # Analista de Dados
            "Dashboard Analítico": self.tela_dashboard_analitico,
            "Visualizar Dados": self.tela_visualizar_dados,
            # Recepcionista
            "Registrar Atendimento na Recepção": self.tela_registrar_atendimento_recepcao,
            "Agenda dos Técnicos": self.tela_agenda_dos_tecnicos,
            "Consultar Usuários (Read-Only)": self.tela_consultar_usuarios_readonly,
            # Comum a todos os perfis
            "Chamados": self.tela_chamados,
        }

        funcao = mapa_telas.get(nome_tela)
        self.preparar_subtela(nome_tela)

        if funcao:
            funcao()
        else:
            ctk.CTkLabel(self.area_conteudo, text="Tela ainda não implementada.",
                         text_color="gray").pack(pady=40)

    # -----------------------------------------------------------------
    # Componentes reutilizáveis para a tela de "Início"
    # -----------------------------------------------------------------
    def criar_tabela(self, parent, colunas, dados, largura_colunas=None):
        """
        Cria uma "tabela" simples usando um CTkScrollableFrame + grid de labels,
        já que o customtkinter não tem widget de tabela nativo.
        `dados` é uma lista de dicts, cada dict com as mesmas chaves de `colunas`.
        """
        frame_tabela = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        frame_tabela.pack(fill="both", expand=True, pady=10)

        largura_colunas = largura_colunas or [1] * len(colunas)
        for i, largura in enumerate(largura_colunas):
            frame_tabela.grid_columnconfigure(i, weight=largura)

        # Cabeçalho
        for col_idx, coluna in enumerate(colunas):
            ctk.CTkLabel(frame_tabela, text=coluna, font=("Arial", 13, "bold"),
                         text_color=COR_ACCENT).grid(row=0, column=col_idx, sticky="w", padx=10, pady=(0, 6))

        # Linha divisória fina sob o cabeçalho
        ctk.CTkFrame(frame_tabela, height=1, fg_color=COR_LINHA_DIVISORIA).grid(
            row=1, column=0, columnspan=len(colunas), sticky="ew", padx=10, pady=(0, 6)
        )

        if not dados:
            ctk.CTkLabel(frame_tabela, text="Nenhum registro encontrado.",
                         text_color="gray").grid(row=2, column=0, columnspan=len(colunas), pady=20, sticky="w", padx=10)
            return frame_tabela

        for row_idx, linha in enumerate(dados, start=2):
            for col_idx, coluna in enumerate(colunas):
                valor = linha.get(coluna, "-")
                ctk.CTkLabel(frame_tabela, text=str(valor) if valor is not None else "-",
                             font=("Arial", 12), text_color=COR_TEXTO_TITULO).grid(row=row_idx, column=col_idx, sticky="w", padx=10, pady=6)

        return frame_tabela

    def mostrar_erro_tabela(self, parent, mensagem):
        ctk.CTkLabel(parent, text=f"⚠ {mensagem}", text_color="#cf4444",
                     font=("Arial", 13)).pack(pady=30)

    def criar_barra_filtro(self, parent, placeholder, comando_buscar):
        frame_filtro = ctk.CTkFrame(parent, fg_color="transparent")
        frame_filtro.pack(fill="x", pady=(0, 10))
        entrada = ctk.CTkEntry(frame_filtro, placeholder_text=placeholder, width=300, border_color=COR_LINHA_DIVISORIA)
        entrada.pack(side="left", padx=(0, 10))
        ctk.CTkButton(frame_filtro, text="Buscar", width=100, fg_color=COR_ACCENT, hover_color=COR_SIDEBAR_HOVER,
                      command=lambda: comando_buscar(entrada.get())).pack(side="left")
        return entrada

    def criar_card_dashboard(self, parent, titulo, valor, cor=None):
        
        cor = cor or COR_ACCENT
        linha = ctk.CTkFrame(parent, fg_color="transparent")
        linha.pack(fill="x", pady=6)
        ctk.CTkLabel(linha, text=titulo, font=("Arial", 13), text_color=COR_TEXTO_TITULO).pack(side="left")
        ctk.CTkLabel(linha, text=str(valor), font=("Arial", 18, "bold"), text_color=cor).pack(side="right")
        ctk.CTkFrame(parent, height=1, fg_color=COR_LINHA_DIVISORIA).pack(fill="x", pady=(2, 0))
        return linha

    # -----------------------------------------------------------------
    # Formatação/validação de datas 
    # -----------------------------------------------------------------
    def formatar_data_dinamica(self, texto_atual):
        apenas_numeros = "".join([c for c in texto_atual if c.isdigit()])
        apenas_numeros = apenas_numeros[:8]

        texto_formatado = ""
        for i, caractere in enumerate(apenas_numeros):
            if i == 2 or i == 4:
                texto_formatado += "/"
            texto_formatado += caractere

        return texto_formatado

    def validar_entrada_data(self, acao, texto_futuro, nome_var):
        if acao == '0':
            return True

        var = self.nametowidget(nome_var)
        texto_pronto = self.formatar_data_dinamica(texto_futuro)

        self.after_idle(lambda: var.delete(0, 'end'))
        self.after_idle(lambda: var.insert(0, texto_pronto))

        return True

    def sugerir_login_automatico(self):
        nome_completo = self.ent_nome.get().strip()
        cargo_selecionado = self.menu_cargo.get()

        if not nome_completo:
            self.ent_login.configure(state="normal")
            self.ent_login.delete(0, 'end')
            self.ent_login.configure(state="disabled")
            return

        primeiro_nome = nome_completo.split()[0].lower()
        sufixo = self.cargos_func_extensoes.get(cargo_selecionado, 'user')
        login_sugerido = f"{primeiro_nome}.{sufixo}"

        self.ent_login.configure(state="normal")
        self.ent_login.delete(0, 'end')
        self.ent_login.insert(0, login_sugerido)
        self.ent_login.configure(state="disabled")

    # ===================================================================
    # SUBTELAS - ADMINISTRADOR
    # ===================================================================
    def tela_admin_cadastrar_usuario(self):
        self.preparar_subtela("Cadastrar Novo Usuário")

        frame_form = ctk.CTkScrollableFrame(self.area_conteudo, label_text="Dados do Usuário")
        frame_form.pack(fill="both", expand=True, pady=10)

        self.ent_usuario_nome = ctk.CTkEntry(frame_form, placeholder_text="Nome Completo", width=400)
        self.ent_usuario_nome.pack(pady=10, anchor="w", padx=20)

        self.ent_usuario_idade = ctk.CTkEntry(frame_form, placeholder_text="Idade", width=400)
        self.ent_usuario_idade.pack(pady=10, anchor="w", padx=20)

        ctk.CTkLabel(frame_form, text="Sexo:", font=("Arial", 12, "bold")).pack(pady=(10, 2), anchor="w", padx=20)
        self.menu_usuario_sexo = ctk.CTkOptionMenu(frame_form, values=["Masculino", "Feminino", "Outro"],
                                                    width=200, dynamic_resizing=False)
        self.menu_usuario_sexo.pack(pady=(0, 10), anchor="w", padx=20)
        self.menu_usuario_sexo.set("Selecione...")

        ctk.CTkLabel(frame_form, text="Raça:", font=("Arial", 12, "bold")).pack(pady=(10, 2), anchor="w", padx=20)
        self.menu_usuario_raca = ctk.CTkOptionMenu(frame_form, values=["Preta", "Branco", "Pardo", "Amarelo", "Indígena"],
                                                    width=200, dynamic_resizing=False)
        self.menu_usuario_raca.pack(pady=(0, 10), anchor="w", padx=20)
        self.menu_usuario_raca.set("Selecione...")

        self.ent_usuario_nome_familiar = ctk.CTkEntry(frame_form, placeholder_text="Nome Completo Familiar/Relacionado", width=400)
        self.ent_usuario_nome_familiar.pack(pady=10, anchor="w", padx=20)

        self.ent_usuario_rua = ctk.CTkEntry(frame_form, placeholder_text="Rua", width=400)
        self.ent_usuario_rua.pack(pady=10, anchor="w", padx=20)

        self.ent_usuario_bairro = ctk.CTkEntry(frame_form, placeholder_text="Bairro", width=400)
        self.ent_usuario_bairro.pack(pady=10, anchor="w", padx=20)

        ctk.CTkLabel(frame_form, text="PCD", font=("Arial", 12, "bold")).pack(pady=(10, 2), anchor="w", padx=20)
        self.menu_usuario_pcd = ctk.CTkOptionMenu(
            frame_form,
            values=["Não há nenhuma condição", "Deficiência Intelectual", "Deficiência Visual", "TEA",
                    "Deficiência Psicossocial", "Deficiência Física"],
            width=200, dynamic_resizing=False
        )
        self.menu_usuario_pcd.pack(pady=(0, 10), anchor="w", padx=20)
        self.menu_usuario_pcd.set("Selecione...")

        self.ent_usuario_telefone = ctk.CTkEntry(frame_form, placeholder_text="Telefone de Contato", width=400)
        self.ent_usuario_telefone.pack(pady=10, anchor="w", padx=20)

        ctk.CTkLabel(frame_form, text="Data de Nascimento:", font=("Arial", 12, "bold")).pack(pady=(10, 2), anchor="w", padx=20)
        comando_validar = self.register(self.validar_entrada_data)
        self.ent_data_nasc = ctk.CTkEntry(frame_form, placeholder_text="dd/mm/aaaa", width=150, validate="key")
        self.ent_data_nasc.configure(validatecommand=(comando_validar, '%d', '%P', '%W'))
        self.ent_data_nasc.pack(pady=(0, 10), anchor='w', padx=20)

        ctk.CTkButton(frame_form, text="Finalizar cadastro", fg_color="green", hover_color="darkgreen",
                      command=self.salvar_usuario_banco).pack(pady=30, anchor="w", padx=20)

    def salvar_usuario_banco(self):
        nome = self.ent_usuario_nome.get().strip()
        idade = self.ent_usuario_idade.get().strip()
        sexo = self.menu_usuario_sexo.get()
        raca = self.menu_usuario_raca.get()
        nome_familiar = self.ent_usuario_nome_familiar.get().strip()
        rua = self.ent_usuario_rua.get().strip()
        bairro = self.ent_usuario_bairro.get().strip()
        pcd = self.menu_usuario_pcd.get()
        telefone = self.ent_usuario_telefone.get().strip()
        data_nasc = self.ent_data_nasc.get().strip()

        if not nome:
            messagebox.showwarning("Erro", "O nome do usuário não pode estar vazio.")
            return

        query = """INSERT INTO usuarios
                   (nome, idade, sexo, raca, nome_familiar, rua, bairro, pcd, telefone, data_nascimento)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        valores = (nome, idade, sexo, raca, nome_familiar, rua, bairro, pcd, telefone, data_nasc)

        sucesso, resultado = self.executar_query(query, valores, commit=True)
        if sucesso:
            self.registrar_atividade(f"Cadastrou o usuário '{nome}'")
            messagebox.showinfo("Sucesso!", f"Usuário '{nome}' cadastrado com sucesso.")
            self.tela_admin_cadastrar_usuario()
        else:
            messagebox.showerror("Erro", f"Falha ao salvar no banco: {resultado}")

    def tela_admin_cadastro_tecnico(self):
        self.preparar_subtela("Cadastro de técnicos no Sistema")

        frame_form = ctk.CTkScrollableFrame(self.area_conteudo, label_text="Dados do Técnico")
        frame_form.pack(fill="both", expand=True, pady=10)

        self.ent_nome = ctk.CTkEntry(frame_form, placeholder_text="Nome Completo", width=400)
        self.ent_nome.pack(pady=10, anchor="w", padx=20)
        self.ent_nome.bind("<KeyRelease>", lambda event: self.sugerir_login_automatico())

        ctk.CTkLabel(frame_form, text="Sexo:", font=("Arial", 12, "bold")).pack(pady=(10, 2), anchor="w", padx=20)
        self.menu_sexo = ctk.CTkOptionMenu(frame_form, values=["Masculino", "Feminino", "Outro"],
                                            width=200, dynamic_resizing=False)
        self.menu_sexo.pack(pady=(0, 10), anchor="w", padx=20)
        self.menu_sexo.set("Selecione...")

        ctk.CTkLabel(frame_form, text="Cargo:", font=("Arial", 12, "bold")).pack(pady=(10, 2), anchor="w", padx=20)
        self.cargos_func_extensoes = {
            "Administrador": "adm", "Recepcionista": "recep", "Analista de Dados": "ad",
            "Administrador de Banco de Dados": "dba", "Coordenador": "coord",
            "Psicólogo": "psi", "Assistente Social": "as"
        }
        self.menu_cargo = ctk.CTkOptionMenu(
            frame_form, values=["Psicólogo", "Assistente Social", "Pedagogo"],
            width=200, dynamic_resizing=False,
            command=lambda escolha: self.sugerir_login_automatico()
        )
        self.menu_cargo.pack(pady=(0, 10), anchor="w", padx=20)
        self.menu_cargo.set("Selecione...")

        ctk.CTkLabel(frame_form, text="Campo de Atuação:", font=("Arial", 12, "bold")).pack(pady=(10, 2), anchor="w", padx=20)
        self.menu_campo_atuacao = ctk.CTkOptionMenu(
            frame_form, values=["Jovens Infratores", "Terceira Idade", "Crianças e Adolescentes", "PCD"],
            width=200, dynamic_resizing=False)
        self.menu_campo_atuacao.pack(pady=(0, 10), anchor="w", padx=20)
        self.menu_campo_atuacao.set("Selecione...")

        ctk.CTkLabel(frame_form, text="Sala de Atendimento:", font=("Arial", 12, "bold")).pack(pady=(10, 2), anchor="w", padx=20)
        self.menu_sala = ctk.CTkOptionMenu(frame_form, values=["Sala 1", "Sala 2", "Sala 3", "Sala 4", "Sala 5"],
                                            width=200, dynamic_resizing=False)
        self.menu_sala.pack(pady=(0, 10), anchor="w", padx=20)
        self.menu_sala.set("Selecione...")

        ctk.CTkLabel(frame_form, text="Escala de Atendimento:", font=("Arial", 12, "bold")).pack(pady=(10, 2), anchor="w", padx=20)
        self.menu_escala = ctk.CTkOptionMenu(
            frame_form,
            values=["Terça, quarta e sexta", "Segunda, quinta e sexta", "Segunda, quarta e quinta",
                    "Segunda, terça e quarta", "Terça, quinta e sexta"],
            width=200, dynamic_resizing=False)
        self.menu_escala.pack(pady=(0, 10), anchor="w", padx=20)
        self.menu_escala.set("Selecione...")

        ctk.CTkLabel(frame_form, text="Turno/Horário:", font=("Arial", 12, "bold")).pack(pady=(10, 2), anchor="w", padx=20)
        self.menu_turno = ctk.CTkOptionMenu(frame_form, values=["Somente a manhã", "Somente a tarde", "8h às 17h", "9h às 18h"],
                                             width=200, dynamic_resizing=False)
        self.menu_turno.pack(pady=(0, 10), anchor="w", padx=20)
        self.menu_turno.set("Selecione...")

        ctk.CTkLabel(frame_form, text="Contrato:", font=("Arial", 12, "bold")).pack(pady=(10, 2), anchor="w", padx=20)
        self.menu_contrato = ctk.CTkOptionMenu(frame_form, values=["CLT", "Concurso Público"],
                                                width=200, dynamic_resizing=False)
        self.menu_contrato.pack(pady=(0, 10), anchor="w", padx=20)
        self.menu_contrato.set("Selecione...")

        ctk.CTkLabel(frame_form, text="Data de Admissão:", font=("Arial", 12, "bold")).pack(pady=(10, 2), anchor="w", padx=20)
        comando_validar = self.register(self.validar_entrada_data)
        self.ent_data_admissao = ctk.CTkEntry(frame_form, placeholder_text="dd/mm/aaaa", width=150, validate="key")
        self.ent_data_admissao.configure(validatecommand=(comando_validar, '%d', '%P', '%W'))
        self.ent_data_admissao.pack(pady=(0, 10), anchor='w', padx=20)

        ctk.CTkLabel(frame_form, text="Data de Desligamento:", font=("Arial", 12, "bold")).pack(pady=(10, 2), anchor="w", padx=20)
        self.ent_data_desligamento = ctk.CTkEntry(frame_form, placeholder_text="dd/mm/aaaa", width=150, validate="key")
        self.ent_data_desligamento.configure(validatecommand=(comando_validar, '%d', '%P', '%W'))
        self.ent_data_desligamento.pack(pady=(0, 10), anchor='w', padx=20)

        ctk.CTkLabel(frame_form, text="Login Sugerido:", font=("Arial", 12, "bold"), text_color="gray").pack(pady=(10, 2), anchor="w", padx=20)
        self.ent_login = ctk.CTkEntry(frame_form, width=250, fg_color=("#dbdbdb", "#2b2b2b"), state="disabled")
        self.ent_login.pack(pady=(0, 10), anchor="w", padx=20)

        ctk.CTkLabel(frame_form, text="Senha provisória: 123456", font=("Arial", 12, "italic"), text_color="#1f538d").pack(pady=10, anchor="w", padx=20)

        ctk.CTkButton(frame_form, text="Finalizar cadastro", fg_color="green", hover_color="darkgreen",
                      command=self.salvar_tecnico_banco).pack(pady=30, anchor="w", padx=20)

    def salvar_tecnico_banco(self):
        nome = self.ent_nome.get().strip()
        sexo = self.menu_sexo.get()
        cargo = self.menu_cargo.get()
        campo_atuacao = self.menu_campo_atuacao.get()
        sala = self.menu_sala.get()
        escala = self.menu_escala.get()
        turno = self.menu_turno.get()
        contrato = self.menu_contrato.get()
        dt_admissao = self.ent_data_admissao.get()
        dt_desligamento = self.ent_data_desligamento.get()
        login = self.ent_login.get()
        senha_padrao = "123456"

        if not nome:
            messagebox.showwarning("Erro", "O nome do técnico não pode estar vazio.")
            return

        query = """INSERT INTO tecnicos
                   (nome, sexo, cargo, campo_atuacao, sala, escala, turno, contrato,
                    dt_admissao, dt_desligamento, login, senha)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        valores = (nome, sexo, cargo, campo_atuacao, sala, escala, turno, contrato,
                   dt_admissao, dt_desligamento, login, senha_padrao)

        sucesso, resultado = self.executar_query(query, valores, commit=True)
        if sucesso:
            self.registrar_atividade(f"Cadastrou o técnico '{nome}'")
            messagebox.showinfo("Sucesso!", f"Técnico cadastrado\nLogin: {login}\nSenha: {senha_padrao}")
            self.tela_admin_cadastro_tecnico()
        else:
            if "1062" in str(resultado):
                messagebox.showerror("Erro", f"O login '{login}' já está em uso. Adicione o sobrenome no campo nome.")
            else:
                messagebox.showerror("Erro", f"Falha ao salvar no banco: {resultado}")

    def tela_atribuir_transferir_caso(self):
        frame = ctk.CTkScrollableFrame(self.area_conteudo, label_text="Atribuir / Transferir Caso")
        frame.pack(fill="both", expand=True, pady=10)

        ctk.CTkLabel(frame, text="Caso:", font=("Arial", 12, "bold")).pack(pady=(10, 2), anchor="w", padx=20)
        ent_caso = ctk.CTkEntry(frame, placeholder_text="ID ou nome do caso", width=400)
        ent_caso.pack(pady=(0, 10), anchor="w", padx=20)

        ctk.CTkLabel(frame, text="Técnico de destino:", font=("Arial", 12, "bold")).pack(pady=(10, 2), anchor="w", padx=20)
        sucesso, tecnicos = self.executar_query("SELECT nome FROM tecnicos", fetch=True)
        nomes_tecnicos = [t["nome"] for t in tecnicos] if sucesso and tecnicos else ["Nenhum técnico encontrado"]
        menu_tecnico = ctk.CTkOptionMenu(frame, values=nomes_tecnicos, width=300)
        menu_tecnico.pack(pady=(0, 10), anchor="w", padx=20)

        ctk.CTkLabel(frame, text="Motivo da transferência:", font=("Arial", 12, "bold")).pack(pady=(10, 2), anchor="w", padx=20)
        txt_motivo = ctk.CTkTextbox(frame, width=400, height=100)
        txt_motivo.pack(pady=(0, 10), anchor="w", padx=20)

        def salvar_transferencia():
            caso = ent_caso.get().strip()
            tecnico_destino = menu_tecnico.get()
            motivo = txt_motivo.get("1.0", "end").strip()
            if not caso:
                messagebox.showwarning("Erro", "Informe o caso a ser transferido.")
                return
            query = "UPDATE casos SET tecnico_responsavel = %s, motivo_transferencia = %s WHERE id = %s OR nome = %s"
            sucesso, resultado = self.executar_query(query, (tecnico_destino, motivo, caso, caso), commit=True)
            if sucesso:
                messagebox.showinfo("Sucesso", f"Caso atribuído/transferido para {tecnico_destino}.")
                ent_caso.delete(0, "end")
                txt_motivo.delete("1.0", "end")
            else:
                messagebox.showerror("Erro", f"Falha ao transferir: {resultado}")

        ctk.CTkButton(frame, text="Confirmar Transferência", fg_color="green", hover_color="darkgreen",
                      command=salvar_transferencia).pack(pady=20, anchor="w", padx=20)

    def tela_visualizar_motoristas(self):
        frame = ctk.CTkFrame(self.area_conteudo, fg_color="transparent")
        frame.pack(fill="both", expand=True)

        sucesso, dados = self.executar_query(
            "SELECT nome, cnh, veiculo, telefone, disponibilidade FROM motoristas", fetch=True
        )
        if not sucesso:
            self.mostrar_erro_tabela(frame, dados)
            return

        self.criar_tabela(frame, ["nome", "cnh", "veiculo", "telefone", "disponibilidade"], dados)

    # ===================================================================
    # SUBTELAS - ADMINISTRADOR DE BANCO DE DADOS
    # ===================================================================
    def tela_dba_config(self):
        self.preparar_subtela("Configurações do Sistema")
        frame = ctk.CTkScrollableFrame(self.area_conteudo, label_text="Configurações do Sistema")
        frame.pack(fill="both", expand=True, pady=10)

        ctk.CTkLabel(frame, text=f"Host do banco: {os.getenv('DB_HOST', 'não configurado')}").pack(anchor="w", padx=20, pady=5)
        ctk.CTkLabel(frame, text=f"Banco de dados: {os.getenv('DB_NAME', 'não configurado')}").pack(anchor="w", padx=20, pady=5)
        ctk.CTkLabel(frame, text=f"Usuário do banco: {os.getenv('DB_USER', 'não configurado')}").pack(anchor="w", padx=20, pady=5)

        ctk.CTkLabel(frame, text="Aparência:", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(20, 5))
        menu_aparencia = ctk.CTkOptionMenu(frame, values=["System", "Light", "Dark"],
                                            command=lambda modo: ctk.set_appearance_mode(modo), width=200)
        menu_aparencia.pack(anchor="w", padx=20)

        ctk.CTkButton(frame, text="Testar Conexão com o Banco", command=self.testar_conexao_dba).pack(anchor="w", padx=20, pady=30)

    def testar_conexao_dba(self):
        con = self.conectar_banco_dados()
        if con:
            messagebox.showinfo("Conexão", "Conexão com o banco de dados bem-sucedida!")
            con.close()

    def tela_dba_sql(self):
        self.preparar_subtela("Tabelas do Banco de Dados (SQL)")
        frame = ctk.CTkFrame(self.area_conteudo, fg_color="transparent")
        frame.pack(fill="both", expand=True)

        ctk.CTkLabel(frame, text="Executar consulta SQL (somente leitura recomendado):",
                     font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 5))
        txt_sql = ctk.CTkTextbox(frame, width=700, height=100)
        txt_sql.pack(anchor="w", pady=(0, 10), fill="x")
        txt_sql.insert("1.0", "SELECT * FROM tecnicos LIMIT 20;")

        frame_resultado = ctk.CTkFrame(frame, fg_color="transparent")
        frame_resultado.pack(fill="both", expand=True)

        def rodar_query():
            for widget in frame_resultado.winfo_children():
                widget.destroy()
            query = txt_sql.get("1.0", "end").strip().rstrip(";")
            if not query:
                return
            eh_select = query.strip().lower().startswith("select")
            sucesso, resultado = self.executar_query(query, fetch=eh_select, commit=not eh_select)
            if not sucesso:
                self.mostrar_erro_tabela(frame_resultado, resultado)
                return
            if eh_select:
                if resultado:
                    colunas = list(resultado[0].keys())
                    self.criar_tabela(frame_resultado, colunas, resultado)
                else:
                    ctk.CTkLabel(frame_resultado, text="Consulta executada, nenhum registro retornado.",
                                 text_color="gray").pack(pady=20)
            else:
                messagebox.showinfo("Sucesso", f"Comando executado. Linhas afetadas: {resultado}")

        ctk.CTkButton(frame, text="Executar", fg_color="green", hover_color="darkgreen", command=rodar_query).pack(anchor="w", pady=(0, 10))

    def tela_dba_cadastro_funcionario(self):
        self.preparar_subtela("Cadastro de funcionários no Sistema")

        frame_form = ctk.CTkScrollableFrame(self.area_conteudo, label_text="Dados do Funcionário")
        frame_form.pack(fill="both", expand=True, pady=10)

        self.ent_nome = ctk.CTkEntry(frame_form, placeholder_text="Nome do Funcionário", width=400)
        self.ent_nome.pack(pady=10, anchor="w", padx=20)
        self.ent_nome.bind("<KeyRelease>", lambda event: self.sugerir_login_automatico())

        ctk.CTkLabel(frame_form, text="Cargo", font=("Arial", 12, "bold")).pack(pady=(10, 2), anchor="w", padx=20)
        self.cargos_func_extensoes = {
            "Administrador": "adm", "Recepcionista": "recep", "Analista de Dados": "ad",
            "Administrador de Banco de Dados": "dba", "Coordenador": "coord",
            "Psicólogo": "psi", "Assistente Social": "as"
        }
        self.menu_cargo = ctk.CTkOptionMenu(
            frame_form,
            values=["Administrador", "Analista de Dados", "Administrador de Banco de Dados", "Recepcionista"],
            width=200, dynamic_resizing=False,
            command=lambda escolha: self.sugerir_login_automatico()
        )
        self.menu_cargo.pack(pady=(0, 10), anchor="w", padx=20)
        self.menu_cargo.set("Selecione...")

        ctk.CTkLabel(frame_form, text="Data de Admissão:", font=("Arial", 12, "bold")).pack(pady=(10, 2), anchor="w", padx=20)
        comando_validar = self.register(self.validar_entrada_data)
        self.ent_data_admissao = ctk.CTkEntry(frame_form, placeholder_text="dd/mm/aaaa", width=150, validate="key")
        self.ent_data_admissao.configure(validatecommand=(comando_validar, '%d', '%P', '%W'))
        self.ent_data_admissao.pack(pady=(0, 10), anchor='w', padx=20)

        ctk.CTkLabel(frame_form, text="Data de Desligamento:", font=("Arial", 12, "bold")).pack(pady=(10, 2), anchor="w", padx=20)
        self.ent_data_desligamento = ctk.CTkEntry(frame_form, placeholder_text="dd/mm/aaaa", width=150, validate="key")
        self.ent_data_desligamento.configure(validatecommand=(comando_validar, '%d', '%P', '%W'))
        self.ent_data_desligamento.pack(pady=(0, 10), anchor='w', padx=20)

        ctk.CTkLabel(frame_form, text="Login Sugerido:", font=("Arial", 12, "bold"), text_color="gray").pack(pady=(10, 2), anchor="w", padx=20)
        self.ent_login = ctk.CTkEntry(frame_form, width=250, fg_color=("#dbdbdb", "#2b2b2b"), state="disabled")
        self.ent_login.pack(pady=(0, 10), anchor="w", padx=20)

        ctk.CTkLabel(frame_form, text="Senha provisória: 123456", font=("Arial", 12, "italic"), text_color="#1f538d").pack(pady=10, anchor="w", padx=20)

        ctk.CTkButton(frame_form, text="Finalizar cadastro", fg_color="green", hover_color="darkgreen",
                      command=self.salvar_funcionario_banco).pack(pady=30, anchor="w", padx=20)

    def salvar_funcionario_banco(self):
        nome = self.ent_nome.get().strip()
        cargo = self.menu_cargo.get()
        dt_admissao = self.ent_data_admissao.get()
        dt_desligamento = self.ent_data_desligamento.get()
        login = self.ent_login.get()
        senha_padrao = "123456"

        if not nome:
            messagebox.showwarning("Erro", "O nome do funcionário não pode estar vazio.")
            return

        query = """INSERT INTO funcionarios (nome, cargo, dt_admissao, dt_desligamento, login, senha)
                   VALUES (%s, %s, %s, %s, %s, %s)"""
        valores = (nome, cargo, dt_admissao, dt_desligamento, login, senha_padrao)

        sucesso, resultado = self.executar_query(query, valores, commit=True)
        if sucesso:
            self.registrar_atividade(f"Cadastrou o funcionário '{nome}' ({cargo})")
            messagebox.showinfo("Sucesso!", f"Funcionário cadastrado\nLogin: {login}\nSenha: {senha_padrao}")
            self.tela_dba_cadastro_funcionario()
        else:
            if "1062" in str(resultado):
                messagebox.showerror("Erro", f"O login '{login}' já está em uso. Adicione o sobrenome no campo nome.")
            else:
                messagebox.showerror("Erro", f"Falha ao salvar no banco: {resultado}")

    def tela_dba_cadastro_coordenador(self):
        self.preparar_subtela("Cadastro do Coordenador no Sistema")

        frame_form = ctk.CTkScrollableFrame(self.area_conteudo, label_text="Dados do Coordenador")
        frame_form.pack(fill="both", expand=True, pady=10)

        self.ent_nome = ctk.CTkEntry(frame_form, placeholder_text="Nome do Coordenador", width=400)
        self.ent_nome.pack(pady=10, anchor="w", padx=20)
        self.cargos_func_extensoes = {"Coordenador": "coord"}
        self.ent_nome.bind("<KeyRelease>", lambda event: self._sugerir_login_coordenador())

        ctk.CTkLabel(frame_form, text="Data de Admissão:", font=("Arial", 12, "bold")).pack(pady=(10, 2), anchor="w", padx=20)
        comando_validar = self.register(self.validar_entrada_data)
        self.ent_data_admissao = ctk.CTkEntry(frame_form, placeholder_text="dd/mm/aaaa", width=150, validate="key")
        self.ent_data_admissao.configure(validatecommand=(comando_validar, '%d', '%P', '%W'))
        self.ent_data_admissao.pack(pady=(0, 10), anchor='w', padx=20)

        ctk.CTkLabel(frame_form, text="Data de Desligamento:", font=("Arial", 12, "bold")).pack(pady=(10, 2), anchor="w", padx=20)
        self.ent_data_desligamento = ctk.CTkEntry(frame_form, placeholder_text="dd/mm/aaaa", width=150, validate="key")
        self.ent_data_desligamento.configure(validatecommand=(comando_validar, '%d', '%P', '%W'))
        self.ent_data_desligamento.pack(pady=(0, 10), anchor='w', padx=20)

        ctk.CTkLabel(frame_form, text="Login Sugerido:", font=("Arial", 12, "bold"), text_color="gray").pack(pady=(10, 2), anchor="w", padx=20)
        self.ent_login = ctk.CTkEntry(frame_form, width=250, fg_color=("#dbdbdb", "#2b2b2b"), state="disabled")
        self.ent_login.pack(pady=(0, 10), anchor="w", padx=20)

        ctk.CTkLabel(frame_form, text="Senha provisória: 123456", font=("Arial", 12, "italic"), text_color="#1f538d").pack(pady=10, anchor="w", padx=20)

        ctk.CTkButton(frame_form, text="Finalizar cadastro", fg_color="green", hover_color="darkgreen",
                      command=self.salvar_coordenador_banco).pack(pady=30, anchor="w", padx=20)

    def _sugerir_login_coordenador(self):
        nome_completo = self.ent_nome.get().strip()
        if not nome_completo:
            self.ent_login.configure(state="normal")
            self.ent_login.delete(0, 'end')
            self.ent_login.configure(state="disabled")
            return
        primeiro_nome = nome_completo.split()[0].lower()
        login_sugerido = f"{primeiro_nome}.coord"
        self.ent_login.configure(state="normal")
        self.ent_login.delete(0, 'end')
        self.ent_login.insert(0, login_sugerido)
        self.ent_login.configure(state="disabled")

    def salvar_coordenador_banco(self):
        nome = self.ent_nome.get().strip()
        dt_admissao = self.ent_data_admissao.get()
        dt_desligamento = self.ent_data_desligamento.get()
        login = self.ent_login.get()
        senha_padrao = "123456"

        if not nome:
            messagebox.showwarning("Erro", "O nome do coordenador não pode estar vazio.")
            return

        query = """INSERT INTO coordenadores (nome, dt_admissao, dt_desligamento, login, senha)
                   VALUES (%s, %s, %s, %s, %s)"""
        valores = (nome, dt_admissao, dt_desligamento, login, senha_padrao)

        sucesso, resultado = self.executar_query(query, valores, commit=True)
        if sucesso:
            self.registrar_atividade(f"Cadastrou o coordenador '{nome}'")
            messagebox.showinfo("Sucesso!", f"Coordenador cadastrado\nLogin: {login}\nSenha: {senha_padrao}")
            self.tela_dba_cadastro_coordenador()
        else:
            if "1062" in str(resultado):
                messagebox.showerror("Erro", f"O login '{login}' já está em uso. Adicione o sobrenome no campo nome.")
            else:
                messagebox.showerror("Erro", f"Falha ao salvar no banco: {resultado}")

    # ===================================================================
    # SUBTELAS - TÉCNICO
    # ===================================================================
    def tela_meus_casos(self):
        frame = ctk.CTkFrame(self.area_conteudo, fg_color="transparent")
        frame.pack(fill="both", expand=True)

        def buscar(termo):
            for widget in frame_resultado.winfo_children():
                widget.destroy()
            query = "SELECT nome_usuario, status, data_abertura, ultima_atualizacao FROM casos WHERE tecnico_responsavel = %s"
            valores = [self.usuario_logado]
            if termo:
                query += " AND nome_usuario LIKE %s"
                valores.append(f"%{termo}%")
            sucesso, dados = self.executar_query(query, tuple(valores), fetch=True)
            if not sucesso:
                self.mostrar_erro_tabela(frame_resultado, dados)
                return
            self.criar_tabela(frame_resultado, ["nome_usuario", "status", "data_abertura", "ultima_atualizacao"], dados)

        self.criar_barra_filtro(frame, "Buscar por nome do usuário...", buscar)
        frame_resultado = ctk.CTkFrame(frame, fg_color="transparent")
        frame_resultado.pack(fill="both", expand=True)
        buscar("")

    def tela_novo_relatorio_evolucao(self):
        frame = ctk.CTkScrollableFrame(self.area_conteudo, label_text="Novo Relatório de Evolução")
        frame.pack(fill="both", expand=True, pady=10)

        ctk.CTkLabel(frame, text="Caso relacionado:", font=("Arial", 12, "bold")).pack(pady=(10, 2), anchor="w", padx=20)
        sucesso, casos = self.executar_query(
            "SELECT nome_usuario FROM casos WHERE tecnico_responsavel = %s", (self.usuario_logado,), fetch=True
        )
        nomes_casos = [c["nome_usuario"] for c in casos] if sucesso and casos else ["Nenhum caso encontrado"]
        menu_caso = ctk.CTkOptionMenu(frame, values=nomes_casos, width=350)
        menu_caso.pack(pady=(0, 10), anchor="w", padx=20)

        ctk.CTkLabel(frame, text="Data do atendimento:", font=("Arial", 12, "bold")).pack(pady=(10, 2), anchor="w", padx=20)
        comando_validar = self.register(self.validar_entrada_data)
        ent_data = ctk.CTkEntry(frame, placeholder_text="dd/mm/aaaa", width=150, validate="key")
        ent_data.configure(validatecommand=(comando_validar, '%d', '%P', '%W'))
        ent_data.pack(pady=(0, 10), anchor="w", padx=20)

        ctk.CTkLabel(frame, text="Relato de evolução:", font=("Arial", 12, "bold")).pack(pady=(10, 2), anchor="w", padx=20)
        txt_relato = ctk.CTkTextbox(frame, width=500, height=200)
        txt_relato.pack(pady=(0, 10), anchor="w", padx=20)

        def salvar_relatorio():
            caso = menu_caso.get()
            data = ent_data.get().strip()
            relato = txt_relato.get("1.0", "end").strip()
            if not relato:
                messagebox.showwarning("Erro", "O relato não pode estar vazio.")
                return
            query = """INSERT INTO relatorios_evolucao (nome_usuario, tecnico, data_atendimento, relato)
                       VALUES (%s, %s, %s, %s)"""
            sucesso, resultado = self.executar_query(query, (caso, self.usuario_logado, data, relato), commit=True)
            if sucesso:
                messagebox.showinfo("Sucesso", "Relatório de evolução salvo com sucesso.")
                txt_relato.delete("1.0", "end")
                ent_data.delete(0, "end")
            else:
                messagebox.showerror("Erro", f"Falha ao salvar relatório: {resultado}")

        ctk.CTkButton(frame, text="Salvar Relatório", fg_color="green", hover_color="darkgreen",
                      command=salvar_relatorio).pack(pady=20, anchor="w", padx=20)

    def tela_agendar_visitas(self):
        frame = ctk.CTkScrollableFrame(self.area_conteudo, label_text="Agendar Visita")
        frame.pack(fill="both", expand=True, pady=10)

        ctk.CTkLabel(frame, text="Usuário/Família a visitar:", font=("Arial", 12, "bold")).pack(pady=(10, 2), anchor="w", padx=20)
        ent_usuario = ctk.CTkEntry(frame, placeholder_text="Nome do usuário", width=400)
        ent_usuario.pack(pady=(0, 10), anchor="w", padx=20)

        ctk.CTkLabel(frame, text="Endereço da visita:", font=("Arial", 12, "bold")).pack(pady=(10, 2), anchor="w", padx=20)
        ent_endereco = ctk.CTkEntry(frame, placeholder_text="Rua, número, bairro", width=400)
        ent_endereco.pack(pady=(0, 10), anchor="w", padx=20)

        ctk.CTkLabel(frame, text="Data da visita:", font=("Arial", 12, "bold")).pack(pady=(10, 2), anchor="w", padx=20)
        comando_validar = self.register(self.validar_entrada_data)
        ent_data = ctk.CTkEntry(frame, placeholder_text="dd/mm/aaaa", width=150, validate="key")
        ent_data.configure(validatecommand=(comando_validar, '%d', '%P', '%W'))
        ent_data.pack(pady=(0, 10), anchor="w", padx=20)

        ctk.CTkLabel(frame, text="Horário:", font=("Arial", 12, "bold")).pack(pady=(10, 2), anchor="w", padx=20)
        ent_horario = ctk.CTkEntry(frame, placeholder_text="hh:mm", width=150)
        ent_horario.pack(pady=(0, 10), anchor="w", padx=20)

        ctk.CTkLabel(frame, text="Motorista necessário?", font=("Arial", 12, "bold")).pack(pady=(10, 2), anchor="w", padx=20)
        menu_motorista = ctk.CTkOptionMenu(frame, values=["Sim", "Não"], width=150)
        menu_motorista.pack(pady=(0, 10), anchor="w", padx=20)

        def salvar_visita():
            usuario = ent_usuario.get().strip()
            if not usuario:
                messagebox.showwarning("Erro", "Informe o usuário a ser visitado.")
                return
            query = """INSERT INTO visitas (nome_usuario, endereco, data_visita, horario, tecnico, motorista_necessario)
                       VALUES (%s, %s, %s, %s, %s, %s)"""
            valores = (usuario, ent_endereco.get().strip(), ent_data.get().strip(),
                       ent_horario.get().strip(), self.usuario_logado, menu_motorista.get())
            sucesso, resultado = self.executar_query(query, valores, commit=True)
            if sucesso:
                messagebox.showinfo("Sucesso", "Visita agendada com sucesso.")
                ent_usuario.delete(0, "end")
                ent_endereco.delete(0, "end")
                ent_data.delete(0, "end")
                ent_horario.delete(0, "end")
            else:
                messagebox.showerror("Erro", f"Falha ao agendar visita: {resultado}")

        ctk.CTkButton(frame, text="Agendar", fg_color="green", hover_color="darkgreen",
                      command=salvar_visita).pack(pady=20, anchor="w", padx=20)

    def tela_minhas_reunioes(self):
        frame = ctk.CTkFrame(self.area_conteudo, fg_color="transparent")
        frame.pack(fill="both", expand=True)

        sucesso, dados = self.executar_query(
            "SELECT titulo, data_reuniao, horario, local FROM reunioes WHERE tecnico = %s",
            (self.usuario_logado,), fetch=True
        )
        if not sucesso:
            self.mostrar_erro_tabela(frame, dados)
            return
        self.criar_tabela(frame, ["titulo", "data_reuniao", "horario", "local"], dados)

    def tela_agenda_atendimentos_tecnico(self):
        frame = ctk.CTkFrame(self.area_conteudo, fg_color="transparent")
        frame.pack(fill="both", expand=True)

        sucesso, dados = self.executar_query(
            "SELECT nome_usuario, data_atendimento, horario, sala FROM atendimentos WHERE tecnico = %s ORDER BY data_atendimento",
            (self.usuario_logado,), fetch=True
        )
        if not sucesso:
            self.mostrar_erro_tabela(frame, dados)
            return
        self.criar_tabela(frame, ["nome_usuario", "data_atendimento", "horario", "sala"], dados)

    # ===================================================================
    # SUBTELAS - COORDENADOR
    # ===================================================================
    def tela_casos_dos_tecnicos(self):
        frame = ctk.CTkFrame(self.area_conteudo, fg_color="transparent")
        frame.pack(fill="both", expand=True)

        def buscar(termo):
            for widget in frame_resultado.winfo_children():
                widget.destroy()
            query = "SELECT nome_usuario, tecnico_responsavel, status, ultima_atualizacao FROM casos"
            valores = ()
            if termo:
                query += " WHERE tecnico_responsavel LIKE %s OR nome_usuario LIKE %s"
                valores = (f"%{termo}%", f"%{termo}%")
            sucesso, dados = self.executar_query(query, valores, fetch=True)
            if not sucesso:
                self.mostrar_erro_tabela(frame_resultado, dados)
                return
            self.criar_tabela(frame_resultado, ["nome_usuario", "tecnico_responsavel", "status", "ultima_atualizacao"], dados)

        self.criar_barra_filtro(frame, "Buscar por técnico ou usuário...", buscar)
        frame_resultado = ctk.CTkFrame(frame, fg_color="transparent")
        frame_resultado.pack(fill="both", expand=True)
        buscar("")

    def tela_painel_atendimentos(self):
        frame = ctk.CTkFrame(self.area_conteudo, fg_color="transparent")
        frame.pack(fill="both", expand=True)

        sucesso, dados = self.executar_query(
            "SELECT nome_usuario, tecnico, data_atendimento, horario, sala FROM atendimentos ORDER BY data_atendimento DESC",
            fetch=True
        )
        if not sucesso:
            self.mostrar_erro_tabela(frame, dados)
            return
        self.criar_tabela(frame, ["nome_usuario", "tecnico", "data_atendimento", "horario", "sala"], dados)

    def tela_monitorar_visitas(self):
        frame = ctk.CTkFrame(self.area_conteudo, fg_color="transparent")
        frame.pack(fill="both", expand=True)

        sucesso, dados = self.executar_query(
            "SELECT nome_usuario, tecnico, data_visita, horario, status FROM visitas ORDER BY data_visita DESC",
            fetch=True
        )
        if not sucesso:
            self.mostrar_erro_tabela(frame, dados)
            return
        self.criar_tabela(frame, ["nome_usuario", "tecnico", "data_visita", "horario", "status"], dados)

    def tela_relatorios_gerenciais(self):
        frame = ctk.CTkFrame(self.area_conteudo, fg_color="transparent")
        frame.pack(fill="both", expand=True)

        frame_cards = ctk.CTkFrame(frame, fg_color="transparent")
        frame_cards.pack(fill="x", pady=(0, 20))

        consultas = [
            ("Casos Ativos", "SELECT COUNT(*) as total FROM casos WHERE status = 'Ativo'"),
            ("Visitas no Mês", "SELECT COUNT(*) as total FROM visitas WHERE MONTH(data_visita) = MONTH(CURDATE())"),
            ("Atendimentos no Mês", "SELECT COUNT(*) as total FROM atendimentos WHERE MONTH(data_atendimento) = MONTH(CURDATE())"),
        ]
        algum_erro = False
        for titulo, query in consultas:
            sucesso, dados = self.executar_query(query, fetch=True)
            valor = dados[0]["total"] if sucesso and dados else "—"
            if not sucesso:
                algum_erro = True
            self.criar_card_dashboard(frame_cards, titulo, valor)

        if algum_erro:
            ctk.CTkLabel(frame, text="Alguns indicadores não puderam ser calculados (verifique a conexão/tabelas).",
                         text_color="gray").pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(frame, text="Casos por Técnico:", font=("Arial", 14, "bold")).pack(anchor="w", pady=(10, 5))
        sucesso, dados = self.executar_query(
            "SELECT tecnico_responsavel, COUNT(*) as total_casos FROM casos GROUP BY tecnico_responsavel",
            fetch=True
        )
        if not sucesso:
            self.mostrar_erro_tabela(frame, dados)
            return
        self.criar_tabela(frame, ["tecnico_responsavel", "total_casos"], dados)

    # ===================================================================
    # SUBTELAS - ANALISTA DE DADOS
    # ===================================================================
    def tela_dashboard_analitico(self):
        frame = ctk.CTkFrame(self.area_conteudo, fg_color="transparent")
        frame.pack(fill="both", expand=True)

        frame_cards = ctk.CTkFrame(frame, fg_color="transparent")
        frame_cards.pack(fill="x", pady=(0, 20))

        consultas = [
            ("Usuários Cadastrados", "SELECT COUNT(*) as total FROM usuarios"),
            ("Casos Totais", "SELECT COUNT(*) as total FROM casos"),
            ("Técnicos Ativos", "SELECT COUNT(*) as total FROM tecnicos WHERE dt_desligamento IS NULL"),
            ("Visitas Realizadas", "SELECT COUNT(*) as total FROM visitas WHERE status = 'Concluída'"),
        ]
        for titulo, query in consultas:
            sucesso, dados = self.executar_query(query, fetch=True)
            valor = dados[0]["total"] if sucesso and dados else "—"
            self.criar_card_dashboard(frame_cards, titulo, valor)

        ctk.CTkLabel(frame, text="Usuários por Bairro:", font=("Arial", 14, "bold")).pack(anchor="w", pady=(10, 5))
        sucesso, dados = self.executar_query(
            "SELECT bairro, COUNT(*) as total FROM usuarios GROUP BY bairro ORDER BY total DESC", fetch=True
        )
        if not sucesso:
            self.mostrar_erro_tabela(frame, dados)
            return
        self.criar_tabela(frame, ["bairro", "total"], dados)

    def tela_visualizar_dados(self):
        frame = ctk.CTkFrame(self.area_conteudo, fg_color="transparent")
        frame.pack(fill="both", expand=True)

        ctk.CTkLabel(frame, text="Tabela:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 5))
        menu_tabela = ctk.CTkOptionMenu(frame, values=["usuarios", "casos", "visitas", "atendimentos", "tecnicos"], width=200)
        menu_tabela.pack(anchor="w", pady=(0, 10))

        frame_resultado = ctk.CTkFrame(frame, fg_color="transparent")
        frame_resultado.pack(fill="both", expand=True)

        def carregar_tabela(tabela=None):
            for widget in frame_resultado.winfo_children():
                widget.destroy()
            nome_tabela = tabela if isinstance(tabela, str) else menu_tabela.get()
            sucesso, dados = self.executar_query(f"SELECT * FROM {nome_tabela} LIMIT 100", fetch=True)
            if not sucesso:
                self.mostrar_erro_tabela(frame_resultado, dados)
                return
            colunas = list(dados[0].keys()) if dados else []
            self.criar_tabela(frame_resultado, colunas, dados)

        menu_tabela.configure(command=carregar_tabela)
        ctk.CTkButton(frame, text="Carregar", command=lambda: carregar_tabela()).pack(anchor="w", pady=(0, 10))
        carregar_tabela("usuarios")

    # ===================================================================
    # SUBTELAS - RECEPCIONISTA
    # ===================================================================
    def tela_registrar_atendimento_recepcao(self):
        frame = ctk.CTkScrollableFrame(self.area_conteudo, label_text="Registrar Atendimento na Recepção")
        frame.pack(fill="both", expand=True, pady=10)

        ctk.CTkLabel(frame, text="Nome do usuário:", font=("Arial", 12, "bold")).pack(pady=(10, 2), anchor="w", padx=20)
        ent_usuario = ctk.CTkEntry(frame, placeholder_text="Nome completo", width=400)
        ent_usuario.pack(pady=(0, 10), anchor="w", padx=20)

        ctk.CTkLabel(frame, text="Técnico/Setor de destino:", font=("Arial", 12, "bold")).pack(pady=(10, 2), anchor="w", padx=20)
        sucesso, tecnicos = self.executar_query("SELECT nome FROM tecnicos", fetch=True)
        nomes_tecnicos = [t["nome"] for t in tecnicos] if sucesso and tecnicos else ["Nenhum técnico encontrado"]
        menu_tecnico = ctk.CTkOptionMenu(frame, values=nomes_tecnicos, width=300)
        menu_tecnico.pack(pady=(0, 10), anchor="w", padx=20)

        ctk.CTkLabel(frame, text="Motivo do atendimento:", font=("Arial", 12, "bold")).pack(pady=(10, 2), anchor="w", padx=20)
        txt_motivo = ctk.CTkTextbox(frame, width=400, height=100)
        txt_motivo.pack(pady=(0, 10), anchor="w", padx=20)

        def salvar_atendimento():
            usuario = ent_usuario.get().strip()
            if not usuario:
                messagebox.showwarning("Erro", "Informe o nome do usuário.")
                return
            query = """INSERT INTO atendimentos (nome_usuario, tecnico, motivo, registrado_por)
                       VALUES (%s, %s, %s, %s)"""
            valores = (usuario, menu_tecnico.get(), txt_motivo.get("1.0", "end").strip(), self.usuario_logado)
            sucesso, resultado = self.executar_query(query, valores, commit=True)
            if sucesso:
                messagebox.showinfo("Sucesso", "Atendimento registrado com sucesso.")
                ent_usuario.delete(0, "end")
                txt_motivo.delete("1.0", "end")
            else:
                messagebox.showerror("Erro", f"Falha ao registrar atendimento: {resultado}")

        ctk.CTkButton(frame, text="Registrar", fg_color="green", hover_color="darkgreen",
                      command=salvar_atendimento).pack(pady=20, anchor="w", padx=20)

    def tela_agenda_dos_tecnicos(self):
        frame = ctk.CTkFrame(self.area_conteudo, fg_color="transparent")
        frame.pack(fill="both", expand=True)

        sucesso, dados = self.executar_query(
            "SELECT tecnico, nome_usuario, data_atendimento, horario, sala FROM atendimentos ORDER BY data_atendimento",
            fetch=True
        )
        if not sucesso:
            self.mostrar_erro_tabela(frame, dados)
            return
        self.criar_tabela(frame, ["tecnico", "nome_usuario", "data_atendimento", "horario", "sala"], dados)

    def tela_consultar_usuarios_readonly(self):
        frame = ctk.CTkFrame(self.area_conteudo, fg_color="transparent")
        frame.pack(fill="both", expand=True)

        def buscar(termo):
            for widget in frame_resultado.winfo_children():
                widget.destroy()
            query = "SELECT nome, telefone, bairro, data_nascimento FROM usuarios"
            valores = ()
            if termo:
                query += " WHERE nome LIKE %s"
                valores = (f"%{termo}%",)
            sucesso, dados = self.executar_query(query, valores, fetch=True)
            if not sucesso:
                self.mostrar_erro_tabela(frame_resultado, dados)
                return
            self.criar_tabela(frame_resultado, ["nome", "telefone", "bairro", "data_nascimento"], dados)

        self.criar_barra_filtro(frame, "Buscar por nome...", buscar)
        frame_resultado = ctk.CTkFrame(frame, fg_color="transparent")
        frame_resultado.pack(fill="both", expand=True)
        buscar("")

    # ===================================================================
    # REGISTRO DE ATIVIDADES (log usado no widget "Últimas Atividades")
    # ===================================================================
    def registrar_atividade(self, descricao):
        """Grava uma linha na tabela `atividades` para alimentar o feed da tela inicial."""
        query = """INSERT INTO atividades (usuario, cargo, descricao, data_hora)
                   VALUES (%s, %s, %s, NOW())"""
        self.executar_query(query, (self.usuario_logado, self.nivel_acesso_logado, descricao), commit=True)

    # ===================================================================
    # TELA INICIAL ("Início") - conteúdo varia por perfil
    # ===================================================================
    def tela_inicio(self):
        mapa_inicio = {
            "Administrador de Banco de Dados": self._tela_inicio_dba,
            "Coordenador": self._tela_inicio_coordenador,
            "Técnico": self._tela_inicio_tecnico,
            "Administrador": self._tela_inicio_administrador,
            "Analista de Dados": self._tela_inicio_analista,
            "Recepcionista": self._tela_inicio_recepcionista,
        }
        funcao = mapa_inicio.get(self.nivel_acesso_logado, self._tela_inicio_generica)
        funcao()

    def criar_titulo_secao(self, parent, texto):
        """Título com linha sublinhada, no estilo 'Calendário' / 'Lista de tarefas' da referência."""
        ctk.CTkLabel(parent, text=texto, font=("Arial", 16, "bold"),
                     text_color=COR_TEXTO_TITULO).pack(anchor="w", pady=(0, 4))
        ctk.CTkFrame(parent, height=2, fg_color=COR_LINHA_DIVISORIA).pack(fill="x", pady=(0, 15))

    def construir_duas_colunas(self, secoes):
        """
        Monta a área de conteúdo em duas colunas lado a lado, separadas por uma
        linha vertical fina — mesmo padrão da referência (Calendário | Lista de tarefas).

        `secoes` é uma lista de tuplas (titulo, funcao_construtora). A primeira
        metade das seções vai para a coluna esquerda, o restante para a direita.
        `funcao_construtora` recebe o frame onde deve desenhar seu conteúdo.
        """
        frame_colunas = ctk.CTkFrame(self.area_conteudo, fg_color="transparent")
        frame_colunas.pack(fill="both", expand=True)

        col_esquerda = ctk.CTkFrame(frame_colunas, fg_color="transparent")
        col_esquerda.pack(side="left", fill="both", expand=True, padx=(0, 25))

        ctk.CTkFrame(frame_colunas, width=1, fg_color=COR_LINHA_DIVISORIA).pack(side="left", fill="y")

        col_direita = ctk.CTkFrame(frame_colunas, fg_color="transparent")
        col_direita.pack(side="left", fill="both", expand=True, padx=(25, 0))

        metade = (len(secoes) + 1) // 2
        for titulo, construtor in secoes[:metade]:
            self.criar_titulo_secao(col_esquerda, titulo)
            construtor(col_esquerda)
        for titulo, construtor in secoes[metade:]:
            self.criar_titulo_secao(col_direita, titulo)
            construtor(col_direita)

        return col_esquerda, col_direita

    def construir_lista_query(self, parent, colunas, query, valores=None):
        """Helper genérico: roda uma query e desenha o resultado como tabela limpa."""
        sucesso, dados = self.executar_query(query, valores, fetch=True)
        if not sucesso:
            self.mostrar_erro_tabela(parent, dados)
            return
        self.criar_tabela(parent, colunas, dados)

    def construir_indicadores(self, parent, indicadores):
        """
        Mostra uma lista de indicadores no estilo 'linha limpa' (título à esquerda,
        valor em destaque à direita, linha fina embaixo). `indicadores` é uma lista
        de tuplas (titulo, query_que_retorna_uma_coluna_'total').
        """
        for titulo, query in indicadores:
            sucesso, dados = self.executar_query(query, fetch=True)
            valor = dados[0]["total"] if sucesso and dados else "—"
            self.criar_card_dashboard(parent, titulo, valor)

    def construir_aviso_chamados(self):
        """Aviso reutilizável de chamados em aberto, com atalho para a tela de gerenciamento."""
        sucesso, dados = self.executar_query(
            "SELECT COUNT(*) as total FROM chamados WHERE status = 'Aberto'", fetch=True
        )
        total_abertos = dados[0]["total"] if sucesso and dados else "—"

        frame_aviso = ctk.CTkFrame(self.area_conteudo, fg_color="transparent")
        frame_aviso.pack(fill="x", pady=(20, 0))
        ctk.CTkLabel(frame_aviso, text=f"📋 {total_abertos} chamado(s) em aberto",
                     font=("Arial", 13, "bold"), text_color=COR_ACCENT).pack(side="left")
        ctk.CTkButton(frame_aviso, text="Ver Chamados", width=140, fg_color=COR_ACCENT,
                      hover_color=COR_SIDEBAR_HOVER,
                      command=lambda: self.mudar_subtela("Chamados")).pack(side="right")

    # -----------------------------------------------------------------
    # Homes específicas de cada cargo
    # -----------------------------------------------------------------
    def _tela_inicio_dba(self):
        self.construir_duas_colunas([
            ("Calendário", self.construir_calendario),
            ("Lista de tarefas", self.construir_todo_list),
        ])

        frame_baixo = ctk.CTkFrame(self.area_conteudo, fg_color="transparent")
        frame_baixo.pack(fill="both", expand=True, pady=(30, 0))
        self.criar_titulo_secao(frame_baixo, "Últimas Atividades")
        self.construir_atividades_recentes(frame_baixo)

        self.construir_aviso_chamados()

    def _tela_inicio_coordenador(self):
        self.construir_duas_colunas([
            ("Lista de tarefas", self.construir_todo_list),
            ("Casos em Aberto", lambda p: self.construir_lista_query(
                p, ["nome_usuario", "tecnico_responsavel", "status"],
                "SELECT nome_usuario, tecnico_responsavel, status FROM casos "
                "WHERE status != 'Encerrado' ORDER BY ultima_atualizacao DESC LIMIT 8"
            )),
        ])

        frame_baixo = ctk.CTkFrame(self.area_conteudo, fg_color="transparent")
        frame_baixo.pack(fill="x", pady=(30, 0))
        self.criar_titulo_secao(frame_baixo, "Panorama da Equipe")
        self.construir_indicadores(frame_baixo, [
            ("Casos Ativos", "SELECT COUNT(*) as total FROM casos WHERE status = 'Ativo'"),
            ("Visitas Hoje", "SELECT COUNT(*) as total FROM visitas WHERE data_visita = CURDATE()"),
            ("Atendimentos Hoje", "SELECT COUNT(*) as total FROM atendimentos WHERE data_atendimento = CURDATE()"),
        ])

        self.construir_aviso_chamados()

    def _tela_inicio_tecnico(self):
        self.construir_duas_colunas([
            ("Lista de tarefas", self.construir_todo_list),
            ("Minha Agenda", lambda p: self.construir_lista_query(
                p, ["nome_usuario", "data_atendimento", "horario"],
                "SELECT nome_usuario, data_atendimento, horario FROM atendimentos "
                "WHERE tecnico = %s ORDER BY data_atendimento LIMIT 8",
                (self.usuario_logado,)
            )),
        ])

        frame_baixo = ctk.CTkFrame(self.area_conteudo, fg_color="transparent")
        frame_baixo.pack(fill="both", expand=True, pady=(30, 0))
        self.criar_titulo_secao(frame_baixo, "Próximas Visitas")
        self.construir_lista_query(
            frame_baixo, ["nome_usuario", "endereco", "data_visita", "horario"],
            "SELECT nome_usuario, endereco, data_visita, horario FROM visitas "
            "WHERE tecnico = %s ORDER BY data_visita LIMIT 8",
            (self.usuario_logado,)
        )

        self.construir_aviso_chamados()

    def _tela_inicio_administrador(self):
        self.construir_duas_colunas([
            ("Lista de tarefas", self.construir_todo_list),
            ("Últimas Atividades", self.construir_atividades_recentes),
        ])

        frame_baixo = ctk.CTkFrame(self.area_conteudo, fg_color="transparent")
        frame_baixo.pack(fill="x", pady=(30, 0))
        self.criar_titulo_secao(frame_baixo, "Quadro de Pessoal")
        self.construir_indicadores(frame_baixo, [
            ("Funcionários Ativos", "SELECT COUNT(*) as total FROM funcionarios WHERE dt_desligamento IS NULL"),
            ("Técnicos Ativos", "SELECT COUNT(*) as total FROM tecnicos WHERE dt_desligamento IS NULL"),
            ("Coordenadores Ativos", "SELECT COUNT(*) as total FROM coordenadores WHERE dt_desligamento IS NULL"),
        ])

        self.construir_aviso_chamados()

    def _tela_inicio_analista(self):
        self.construir_duas_colunas([
            ("Lista de tarefas", self.construir_todo_list),
            ("Indicadores Rápidos", lambda p: self.construir_indicadores(p, [
                ("Usuários Cadastrados", "SELECT COUNT(*) as total FROM usuarios"),
                ("Casos Totais", "SELECT COUNT(*) as total FROM casos"),
                ("Técnicos Ativos", "SELECT COUNT(*) as total FROM tecnicos WHERE dt_desligamento IS NULL"),
                ("Visitas Concluídas", "SELECT COUNT(*) as total FROM visitas WHERE status = 'Concluída'"),
            ])),
        ])

        frame_baixo = ctk.CTkFrame(self.area_conteudo, fg_color="transparent")
        frame_baixo.pack(fill="both", expand=True, pady=(30, 0))
        self.criar_titulo_secao(frame_baixo, "Usuários por Bairro")
        self.construir_lista_query(
            frame_baixo, ["bairro", "total"],
            "SELECT bairro, COUNT(*) as total FROM usuarios GROUP BY bairro ORDER BY total DESC LIMIT 8"
        )

        self.construir_aviso_chamados()

    def _tela_inicio_recepcionista(self):
        self.construir_duas_colunas([
            ("Lista de tarefas", self.construir_todo_list),
            ("Agenda de Hoje", lambda p: self.construir_lista_query(
                p, ["tecnico", "nome_usuario", "horario", "sala"],
                "SELECT tecnico, nome_usuario, horario, sala FROM atendimentos "
                "WHERE data_atendimento = CURDATE() ORDER BY horario LIMIT 8"
            )),
        ])

        frame_baixo = ctk.CTkFrame(self.area_conteudo, fg_color="transparent")
        frame_baixo.pack(fill="both", expand=True, pady=(30, 0))
        self.criar_titulo_secao(frame_baixo, "Visitas Agendadas para Hoje")
        self.construir_lista_query(
            frame_baixo, ["nome_usuario", "tecnico", "horario"],
            "SELECT nome_usuario, tecnico, horario FROM visitas WHERE data_visita = CURDATE() ORDER BY horario"
        )

        self.construir_aviso_chamados()

    def _tela_inicio_generica(self):
        # Fallback simples, usado apenas se o cargo não tiver home customizada.
        frame = ctk.CTkFrame(self.area_conteudo, fg_color="transparent")
        frame.pack(fill="both", expand=True)
        ctk.CTkLabel(frame, text="Bem-vindo(a) de volta!", font=("Arial", 20, "bold"),
                     text_color=COR_TEXTO_TITULO).pack(pady=(40, 10), anchor="w")
        ctk.CTkLabel(frame, text="Use o menu ao lado para navegar pelas funcionalidades do seu perfil.",
                     text_color="gray").pack(anchor="w")

    # -----------------------------------------------------------------
    # Widget: Calendário (navegável por mês, sem dependências externas)
    # -----------------------------------------------------------------
    def construir_calendario(self, parent):
        hoje = date.today()
        self._cal_ano = hoje.year
        self._cal_mes = hoje.month

        meses_pt = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho",
                    "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(pady=(0, 10), anchor="w")

        lbl_mes_ano = ctk.CTkLabel(header, text="", font=("Arial", 13, "bold"), text_color=COR_TEXTO_TITULO)

        frame_dias = ctk.CTkFrame(parent, fg_color="transparent")
        frame_dias.pack(anchor="w")

        def desenhar():
            for widget in frame_dias.winfo_children():
                widget.destroy()

            lbl_mes_ano.configure(text=f"{meses_pt[self._cal_mes - 1]} de {self._cal_ano}")

            for i, dia_sem in enumerate(["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]):
                ctk.CTkLabel(frame_dias, text=dia_sem, font=("Arial", 11, "bold"),
                             text_color="gray", width=32).grid(row=0, column=i, pady=(0, 5))

            for r, semana in enumerate(calendar.monthcalendar(self._cal_ano, self._cal_mes), start=1):
                for c, dia in enumerate(semana):
                    eh_hoje = (dia == hoje.day and self._cal_mes == hoje.month and self._cal_ano == hoje.year)
                    ctk.CTkLabel(
                        frame_dias, text=str(dia) if dia else "", width=32, height=28, corner_radius=16,
                        fg_color=COR_ACCENT if eh_hoje else "transparent",
                        text_color="white" if eh_hoje else COR_TEXTO_TITULO
                    ).grid(row=r, column=c, padx=2, pady=2)

        def mudar_mes(delta):
            novo_mes = self._cal_mes + delta
            if novo_mes > 12:
                self._cal_mes = 1
                self._cal_ano += 1
            elif novo_mes < 1:
                self._cal_mes = 12
                self._cal_ano -= 1
            else:
                self._cal_mes = novo_mes
            desenhar()

        ctk.CTkButton(header, text="◀", width=26, height=26, fg_color="transparent", text_color=COR_TEXTO_TITULO,
                      hover_color=("#e8e2d0"), command=lambda: mudar_mes(-1)).pack(side="left", padx=(0, 8))
        lbl_mes_ano.pack(side="left")
        ctk.CTkButton(header, text="▶", width=26, height=26, fg_color="transparent", text_color=COR_TEXTO_TITULO,
                      hover_color=("#e8e2d0"), command=lambda: mudar_mes(1)).pack(side="left", padx=(8, 0))

        desenhar()
        return frame_dias

    # -----------------------------------------------------------------
    # Widget: To-do list (tarefas pessoais do usuário logado)
    # -----------------------------------------------------------------
    def construir_todo_list(self, parent):
        frame_add = ctk.CTkFrame(parent, fg_color="transparent")
        frame_add.pack(fill="x", pady=(0, 12))
        ent_tarefa = ctk.CTkEntry(frame_add, placeholder_text="Nova tarefa...", border_color=COR_LINHA_DIVISORIA)
        ent_tarefa.pack(side="left", fill="x", expand=True, padx=(0, 8))

        frame_lista = ctk.CTkScrollableFrame(parent, fg_color="transparent", height=220)
        frame_lista.pack(fill="both", expand=True)

        def carregar_tarefas():
            for widget in frame_lista.winfo_children():
                widget.destroy()

            sucesso, dados = self.executar_query(
                "SELECT id, descricao, concluida FROM tarefas WHERE usuario = %s ORDER BY concluida, data_criacao DESC",
                (self.usuario_logado,), fetch=True
            )
            if not sucesso:
                ctk.CTkLabel(frame_lista, text="Não foi possível carregar as tarefas.",
                             text_color="#cf4444", font=("Arial", 11), wraplength=250).pack(pady=10, anchor="w")
                return
            if not dados:
                ctk.CTkLabel(frame_lista, text="Nenhuma tarefa cadastrada.", text_color="gray").pack(pady=10, anchor="w")
                return

            for tarefa in dados:
                linha = ctk.CTkFrame(frame_lista, fg_color="transparent")
                linha.pack(fill="x", pady=3)

                var_check = ctk.BooleanVar(value=bool(tarefa["concluida"]))

                def alternar(id_tarefa=tarefa["id"], var=var_check):
                    novo_status = 1 if var.get() else 0
                    self.executar_query("UPDATE tarefas SET concluida = %s WHERE id = %s",
                                         (novo_status, id_tarefa), commit=True)
                    carregar_tarefas()

                ctk.CTkCheckBox(linha, text=tarefa["descricao"], variable=var_check,
                                command=alternar, font=("Arial", 12), text_color=COR_TEXTO_TITULO,
                                fg_color=COR_ACCENT, hover_color=COR_SIDEBAR_HOVER,
                                width=200).pack(side="left", anchor="w")

                def excluir(id_tarefa=tarefa["id"]):
                    self.executar_query("DELETE FROM tarefas WHERE id = %s", (id_tarefa,), commit=True)
                    carregar_tarefas()

                ctk.CTkButton(linha, text="✕", width=24, height=24, fg_color="transparent",
                              text_color="#cf4444", hover_color=("#f0d0d0", "#3a2020"),
                              command=excluir).pack(side="right")

        def adicionar_tarefa():
            descricao = ent_tarefa.get().strip()
            if not descricao:
                return
            query = "INSERT INTO tarefas (usuario, cargo, descricao, concluida) VALUES (%s, %s, %s, 0)"
            sucesso, resultado = self.executar_query(
                query, (self.usuario_logado, self.nivel_acesso_logado, descricao), commit=True
            )
            if sucesso:
                ent_tarefa.delete(0, "end")
                carregar_tarefas()
            else:
                messagebox.showerror("Erro", f"Não foi possível salvar a tarefa: {resultado}")

        ctk.CTkButton(frame_add, text="+", width=36, fg_color=COR_ACCENT, hover_color=COR_SIDEBAR_HOVER,
                      command=adicionar_tarefa).pack(side="left")
        ent_tarefa.bind("<Return>", lambda event: adicionar_tarefa())

        carregar_tarefas()
        return frame_lista

    # -----------------------------------------------------------------
    # Widget: Últimas atividades (feed alimentado por registrar_atividade)
    # -----------------------------------------------------------------
    def construir_atividades_recentes(self, parent):
        frame_lista = ctk.CTkScrollableFrame(parent, fg_color="transparent", height=180)
        frame_lista.pack(fill="both", expand=True)

        sucesso, dados = self.executar_query(
            "SELECT usuario, descricao, data_hora FROM atividades ORDER BY data_hora DESC LIMIT 15",
            fetch=True
        )
        if not sucesso:
            ctk.CTkLabel(frame_lista, text="Não foi possível carregar as atividades.",
                         text_color="#cf4444", font=("Arial", 11)).pack(pady=10, anchor="w")
            return frame_lista
        if not dados:
            ctk.CTkLabel(frame_lista, text="Nenhuma atividade registrada ainda.", text_color="gray").pack(pady=10, anchor="w")
            return frame_lista

        for atividade in dados:
            linha = ctk.CTkFrame(frame_lista, fg_color="transparent")
            linha.pack(fill="x", pady=4)
            ctk.CTkLabel(linha, text=str(atividade["data_hora"]), font=("Arial", 10),
                         text_color="gray", width=110, anchor="w").pack(side="left")
            ctk.CTkLabel(linha, text=f"{atividade['usuario']}: {atividade['descricao']}",
                         font=("Arial", 12), text_color=COR_TEXTO_TITULO, anchor="w", justify="left",
                         wraplength=500).pack(side="left", fill="x", expand=True)

        return frame_lista

    # ===================================================================
    # SUBTELA - CHAMADOS (comum a todos os perfis)
    # ===================================================================

    def tela_chamados(self):
        if self.nivel_acesso_logado == "Administrador de Banco de Dados":
            self.tela_chamados_dba()
        else:
            self.tela_chamados_usuario()

    def tela_chamados_usuario(self):
        """Tela onde qualquer usuário (exceto o DBA) pode abrir um chamado e ver os seus."""
        frame = ctk.CTkScrollableFrame(self.area_conteudo, fg_color="transparent")
        frame.pack(fill="both", expand=True)

        frame_form = ctk.CTkFrame(frame, fg_color="transparent")
        frame_form.pack(fill="x", pady=(0, 25))

        self.criar_titulo_secao(frame_form, "Abrir Novo Chamado")

        ctk.CTkLabel(frame_form, text="Motivo do chamado:", font=("Arial", 12, "bold"), text_color=COR_TEXTO_TITULO).pack(anchor="w")
        ent_motivo = ctk.CTkEntry(frame_form, placeholder_text='Ex: "Preciso que o fulano seja cadastrado no sistema"',
                                   width=500, border_color=COR_LINHA_DIVISORIA)
        ent_motivo.pack(anchor="w", pady=(2, 10))

        ctk.CTkLabel(frame_form, text="Informações adicionais:", font=("Arial", 12, "bold"), text_color=COR_TEXTO_TITULO).pack(anchor="w")
        txt_info = ctk.CTkTextbox(frame_form, width=500, height=100, border_color=COR_LINHA_DIVISORIA, border_width=1)
        txt_info.pack(anchor="w", pady=(2, 10))

        frame_lista = ctk.CTkFrame(frame, fg_color="transparent")

        def carregar_meus_chamados():
            for widget in frame_lista.winfo_children():
                widget.destroy()
            sucesso, dados = self.executar_query(
                "SELECT id AS n_chamado, motivo, status, data_abertura FROM chamados "
                "WHERE solicitante = %s ORDER BY data_abertura DESC",
                (self.usuario_logado,), fetch=True
            )
            if not sucesso:
                self.mostrar_erro_tabela(frame_lista, dados)
                return
            self.criar_tabela(frame_lista, ["n_chamado", "motivo", "status", "data_abertura"], dados)

        def abrir_chamado():
            motivo = ent_motivo.get().strip()
            if not motivo:
                messagebox.showwarning("Erro", "Descreva o motivo do chamado.")
                return
            info = txt_info.get("1.0", "end").strip()
            query = """INSERT INTO chamados (solicitante, cargo_solicitante, motivo, informacoes_adicionais, status, data_abertura)
                       VALUES (%s, %s, %s, %s, 'Aberto', NOW())"""
            sucesso, resultado = self.executar_query(
                query, (self.usuario_logado, self.nivel_acesso_logado, motivo, info), commit=True
            )
            if sucesso:
                self.registrar_atividade(f"Abriu chamado: {motivo}")
                messagebox.showinfo("Sucesso", "Chamado aberto com sucesso! A equipe responsável vai analisar.")
                ent_motivo.delete(0, "end")
                txt_info.delete("1.0", "end")
                carregar_meus_chamados()
            else:
                messagebox.showerror("Erro", f"Não foi possível abrir o chamado: {resultado}")

        ctk.CTkButton(frame_form, text="Abrir Chamado", fg_color=COR_ACCENT, hover_color=COR_SIDEBAR_HOVER,
                      command=abrir_chamado).pack(anchor="w", pady=(5, 0))

        self.criar_titulo_secao(frame, "Meus Chamados")
        frame_lista.pack(fill="both", expand=True)
        carregar_meus_chamados()

    def tela_chamados_dba(self):
        """Tela do DBA para visualizar e resolver os chamados abertos por qualquer usuário."""
        frame = ctk.CTkFrame(self.area_conteudo, fg_color="transparent")
        frame.pack(fill="both", expand=True)

        frame_filtro = ctk.CTkFrame(frame, fg_color="transparent")
        frame_filtro.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(frame_filtro, text="Filtrar por status:", font=("Arial", 12, "bold"),
                     text_color=COR_TEXTO_TITULO).pack(side="left", padx=(0, 10))
        menu_status = ctk.CTkOptionMenu(frame_filtro, values=["Aberto", "Em andamento", "Resolvido", "Todos"], width=180)
        menu_status.set("Aberto")
        menu_status.pack(side="left")

        frame_lista = ctk.CTkFrame(frame, fg_color="transparent")

        def carregar_chamados(status=None):
            for widget in frame_lista.winfo_children():
                widget.destroy()
            filtro = status if isinstance(status, str) else menu_status.get()
            colunas = ["n_chamado", "solicitante", "cargo_solicitante", "motivo", "status", "data_abertura"]
            select = f"SELECT id AS n_chamado, solicitante, cargo_solicitante, motivo, status, data_abertura FROM chamados"
            if filtro == "Todos":
                sucesso, dados = self.executar_query(select + " ORDER BY data_abertura DESC", fetch=True)
            else:
                sucesso, dados = self.executar_query(
                    select + " WHERE status = %s ORDER BY data_abertura DESC", (filtro,), fetch=True
                )
            if not sucesso:
                self.mostrar_erro_tabela(frame_lista, dados)
                return
            self.criar_tabela(frame_lista, colunas, dados)

        menu_status.configure(command=carregar_chamados)
        ctk.CTkButton(frame_filtro, text="Atualizar Lista", fg_color=COR_ACCENT, hover_color=COR_SIDEBAR_HOVER,
                      command=lambda: carregar_chamados()).pack(side="left", padx=10)

        frame_lista.pack(fill="both", expand=True, pady=(0, 20))
        carregar_chamados("Aberto")

        # Formulário para atualizar/resolver um chamado específico
        frame_resolver = ctk.CTkFrame(frame, fg_color="transparent")
        frame_resolver.pack(fill="x", pady=(10, 0))

        self.criar_titulo_secao(frame_resolver, "Atualizar Chamado")

        frame_campos = ctk.CTkFrame(frame_resolver, fg_color="transparent")
        frame_campos.pack(fill="x")

        ctk.CTkLabel(frame_campos, text="N° do chamado:", text_color=COR_TEXTO_TITULO).pack(side="left")
        ent_num_chamado = ctk.CTkEntry(frame_campos, width=100, border_color=COR_LINHA_DIVISORIA)
        ent_num_chamado.pack(side="left", padx=(5, 20))

        ctk.CTkLabel(frame_campos, text="Novo status:", text_color=COR_TEXTO_TITULO).pack(side="left")
        menu_novo_status = ctk.CTkOptionMenu(frame_campos, values=["Em andamento", "Resolvido"], width=150)
        menu_novo_status.pack(side="left", padx=(5, 0))

        ctk.CTkLabel(frame_resolver, text="Observação da resolução:", font=("Arial", 12),
                     text_color=COR_TEXTO_TITULO).pack(anchor="w", pady=(15, 2))
        txt_obs = ctk.CTkTextbox(frame_resolver, width=500, height=80, border_color=COR_LINHA_DIVISORIA, border_width=1)
        txt_obs.pack(anchor="w", pady=(0, 10))

        def atualizar_chamado():
            numero = ent_num_chamado.get().strip()
            if not numero:
                messagebox.showwarning("Erro", "Informe o número do chamado.")
                return
            novo_status = menu_novo_status.get()
            obs = txt_obs.get("1.0", "end").strip()
            query = """UPDATE chamados SET status = %s, resolvido_por = %s,
                       observacao_resolucao = %s, data_resolucao = NOW() WHERE id = %s"""
            sucesso, resultado = self.executar_query(
                query, (novo_status, self.usuario_logado, obs, numero), commit=True
            )
            if sucesso:
                self.registrar_atividade(f"Atualizou chamado #{numero} para '{novo_status}'")
                messagebox.showinfo("Sucesso", f"Chamado #{numero} atualizado para '{novo_status}'.")
                ent_num_chamado.delete(0, "end")
                txt_obs.delete("1.0", "end")
                carregar_chamados()
            else:
                messagebox.showerror("Erro", f"Não foi possível atualizar o chamado: {resultado}")

        ctk.CTkButton(frame_resolver, text="Salvar Atualização", fg_color=COR_ACCENT, hover_color=COR_SIDEBAR_HOVER,
                      command=atualizar_chamado).pack(anchor="w", pady=(5, 0))


if __name__ == "__main__":
    app = AppSistemaSocial()
    app.mainloop()