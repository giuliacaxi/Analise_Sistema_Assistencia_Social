import customtkinter as ctk
from tkinter import messagebox
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("orange")

class AppSistemaSocial(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Controle de Dados")
        self.geometry("800x600")
        
        self.id_usuario_logado = None  # Variável para armazenar o ID do usuário logado
        self.usuario_logado = None
        self.nivel_acesso_logado = None
        
        self.tela_login()
        
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
        
    def limpar_tela(self):
        for widget in self.winfo_children():
            widget.destroy()
    
    def tela_login(self):
        self.limpar_tela()
        
        frame_login = ctk.CTkFrame(self,width=380,height=400, corner_radius=15)
        frame_login.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(frame_login, text = "Controle de Dados || Assistência Social", font=("Arial", 22, "bold"), text_color="#1f538d").pack(pady=(40,5))
        ctk.CTkLabel(frame_login, text = "Faça login para continuar", text_color="gray").pack(pady=(0, 20))
        
        self.txt_login = ctk.CTkEntry(frame_login, placeholder_text="Usuário", width=280, height=40, corner_radius=8)
        self.txt_login.pack(pady=(0, 10))
        
        self.txt_senha = ctk.CTkEntry(frame_login, placeholder_text="Senha", show="*", width=280, height=40, corner_radius=8)
        self.txt_senha.pack(pady=(0, 20))
        
        ctk.CTkButton(frame_login, text = "Acessar", width =280, height=40, corner_radius=8, font=("Arial", 14, "bold"), command=self.mock_login).pack(pady=30)
        
    def mock_login(self): # Função temporária para simular o login
        self.nivel_acesso_logado = "Administrador"
        self.usuario_logado = "Geralt de Rívia"
        self.id_usuario_logado = "ADM02"
        self.carregar_painel_principal()
        
    
    def carregar_painel_principal(self):
        self.limpar_tela()
        
        #Menu Lateral
        
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=("#ebebeb", "#1a1a1a")) 
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        #Título do Menu Lateral
        
        ctk.CTKLabel(self.sidebar, text="Sistema de Controle de Dados - AS", font=("Arial", 20, "bold"), text_color="#1f538d").pack(pady=(30, 5))
        ctk.CTkLabel(self.sidebar, text=f"id: {self.id_usuario_logado} | {self.usuario_logado} | {self.nivel_acesso_logado}", font=("Arial", 12), text_color="gray").pack(pady=(0, 20))
        
        #Painel Direito
        
        self.conteudo_principal = ctk.CTkFrame(self,corner_radius = 15, fg_color="transparent")
        self.conteudo_principal.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        
        #Cabeçalho do Painel Direito
        
        header = ctk.CTkFrame(self.conteudo_principal, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=10)
        self.lbl_titulo_pagina = ctk.CTkLabel(header, text = "Início", font=("Arial", 24, "bold"))
        self.lbl_titulo_pagina.pack(side="left")
        ctk.CTkLabel(header, text = f"Bem-vindo, {self.usuario_logado}!", font=("Arial", 14, "italic"), text_color="gray").pack(side="right")
        
        #Roteamento de botões no menu lateral
        
        self.construir_menu_lateral()
        
        #Botão de logout fixo no rodapé do menu lateral
        
        ctk.CTkButton(self.siderbar, text = "Sair"), fg_color="#cf4444", hover_color="#b33636", height=35, command=self.tela_login.pack(side="bottom", fill="x", padx=20, pady=20)
        
    def construir_menu_lateral(self):
        
        nivel = self.nivel_acesso_logado
        
        if nivel == "Admininstrador de Banco de Dados":
            self.criar_botao_menu("Configurações do Sistema", self.tela_dba_config)
            self.criar_botao_menu("Tabelas do Banco de Dados (SQL)", self.tela_dba_sql)
            self.criar_botao_menu("Cadastrar Funcionario", self.tela_dba_cadastrar_funcionario)
            self.criar_botao_menu("Cadastrar Coordenador", self.tela_dba_cadastrar_funcionario)
            
            
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
            # Repare que agora as funções abrem telas específicas dentro da nossa área de conteúdo!
            self.criar_botao_menu("Cadastrar Usuário", self.tela_admin_cadastrar_usuario)
            self.criar_botao_menu("Cadastrar Técnico", lambda: self.mudar_subtela("Cadastrar Técnico"))
            self.criar_botao_menu("Atribuir / Transferir Caso", lambda: self.mudar_subtela("Atribuir / Transferir Caso"))
            self.criar_botao_menu("Visualizar Motoristas", lambda: self.mudar_subtela("Visualizar Motoristas"))
            
        elif nivel == "Analista de Dados":
            self.criar_botao_menu("Abrir Dashboard", lambda: self.mudar_subtela("Dashboard Analítico"))
            self.criar_botao_menu("Visualizar Dados", lambda: self.mudar_subtela("Visualizar Dados"))
            
        elif nivel == "Recepcionista":
            self.criar_botao_menu("Registrar Atendimento na Recepção", lambda: self.mudar_subtela("Registrar Atendimento na Recepção"))
            self.criar_botao_menu("Agenda dos Técnicos", lambda: self.mudar_subtela("Agenda dos Técnicos"))
            self.criar_botao_menu("Consultar Cadastros", lambda: self.mudar_subtela("Consultar Usuários (Read-Only)"))        
    
    def criar_botao_menu(self,texto,comando):
        btn = ctk.CTkButton(self.sidebar, text=texto, anchor="w", heigh=40, fg_color="transparent", text_color=("#333", "#ccc"), hover_color=("#dbdbdb", "#2b2b2b"), font=("Arial", 13), command=comando)
        btn.pack(fill="x", padx=10, pady=4)
    
    def limpar_area_conteudo(self):
        #Mantém o cabeçalho superior e deleta o resto abaixo dele
        
        for widget in self.conteudo_principal_winfo_children():
            if widget != self.lbl_titulo_pagina.master: #Não deleta a header
                widget.destroy()
    
    #Função para formatação de entrada de datas
    
    def formatar_data_dinamica(self,texto_atual):
        apenas_numeros = "".join([c for c in texto_atual if c.isdigit()])
        
        #Limitando o tamanho para ser igual a de uma data (dd/mm/yyyy)
        apenas_numeros = apenas_numeros[:8]
        
        texto_formatado = ""
        for i, caractere in enumerate(apenas_numeros):
            if i == 2 or i == 4:
                texto_formatado += "/"
            texto_formatado += caractere
            
        return texto_formatado
    
    def validar_entrada_data(self,acao,texto_futuro,nome_var):
        if acao == '0': 
            return True
        
        var = self.nametowidget(nome_var)
        
        texto_pronto = self.formatar_data_dinamica(texto_futuro)
        
        self.after_idle(lambda: var.delete(0, 'end'))
        self.after_idle(lambda: var.insert(0,texto_pronto))
        
        return True
    
    #Subtelas
    
    def tela_admin_cadastrar_usuario(self):
        self.limpar_area_conteudo()
        self.lbl_titulo_pagina.configure(text = "Cadastrar Novo Usuário")
        
        frame_form = ctk.CTkScrollableFrame(self.conteudo_principal, label_text = "Dados do Usuário")
        frame_form.pack(fill="both", expand=True, pady=10)
        
        ent_nome = ctk.CTkEntry(frame_form, placeholder_text="Nome Completo", width=400)
        ent_nome.pack(pady=10, anchor="w", padx=20)
        
        ent_idade = ctk.CTkEntry(frame_form, placeholder_text="Idade", width=400)
        ent_idade.pack(pady=10, anchor="w", padx=20)
        
        ctk.CTkLabel(frame_form, text = "Sexo:", font=("Arial", 12, "bold")).pack(pady=(10, 2), anchor="w", padx=20)
        
        self.menu_sexo = ctk.CTkOptionMenu(
            frame_form,
            values = ["Masculino", "Feminino", "Outro"],
            width = 200,
            dynamic_resizing=False
        )
        self.menu_sexo.pack(pady=(0,10), anchor="w", padx=20)
        self.menu_sexo.set("Selecione...")
        
        ctk.CTkLabel(frame_form, text= "Raça:", font=("Arial", 12, "bold")).pack(pady=(10, 2), anchor="w", padx=20)
        
        self.menu_raca = ctk.CTkOptionMenu(
            frame_form,
            values = ["Preta", "Branco", "Pardo", "Amarelo", "Indígena"],
            width= 200,
            dynamic_resizing=False
        )
        self.menu_raca.pack(pady=(0,10),anchor="w", padx=20)
        self.menu_raca.set("Selecione...")
        
        ent_nome_familiar = ctk.CTkEntry(frame_form, placeholder_text="Nome Completo Familiar/Relacionado", width=400)
        ent_nome_familiar.pack(pady=10, anchor="w", padx=20)
        
        ent_rua = ctk.CTkEntry(frame_form, placeholder_text= "Rua", width = 200)
        ent_rua.pack(pady=10, anchor="w", padx=20)
        
        ent_bairro = ctk.CTkEntry(frame_form, placeholder_text="Bairro", width=400)
        ent_bairro.pack(pady=10, anchor="w", padx=20)
        
        ctk.CTkLabel(frame_form,text="PCD", font=("Arial", 12, "bold")).pack(pady=(10,2),anchor="w",padx=20)
        
        self.menu_pcd = ctk.CTkOptionMenu(
            frame_form,
            values=["Não há nenhuma condição","Deficiência Intelectual", "Deficiência Visual", "TEA","Deficiência Psicossocial", "Deficiência Física"],
            width=200,
            dynamic_resizing=False
        )
        self.menu_pcd.pack(pady=(0,10), anchor="w", padx=20)
        self.menu_pcd.set("Selecione...")
        
        ent_telefone = ctk.CTkEntry(frame_form, placeholder_text="Telefone de Contato", width=400)
        ent_telefone.pack(pady=10, anchor="w", padx=20)
        
        ctk.CTkLabel(frame_form, text="Data de Nascimento:", font=("Arial", 12, "bold")).pack(pady=(10, 2), anchor="w", padx=20)
        
        comando_validar = self.register(self.validar_entrada_data)
        
        self.ent_data_nasc = ctk.CTkEntry(
            frame_form,
            placeholder_text="dd/mm/aaaa",
            width=150,
            validate="key"
        )
        # Vincula o comando passando o status da ação (%d), o texto futuro (%P) e o próprio widget (%W)
        self.ent_data_nasc.configure(validatecommand=(comando_validar, '%d', '%P', '%W'))
        self.ent_data_nasc.pack(pady=(0,10), anchor='w', padx=20)
        
        ctk.CTkButton(frame_form, text="Salvar", command=self.salvar_com_data).pack(pady=20, padx=20, anchor="w")
        
    
    
    def tela_dba_cadastro_funcionario(self):
        self.limpar_area_conteudo()
        self.lbl_titulo_pagina.configure(text="Cadastro de funcionários no Sistema")
        
        frame_form = ctk.CTkScrollableFrame(self.conteudo_principal, label_text = "Dados do Funcionário")
        frame_form.pack(fill="both", expand=True, pady=10)
        
        ent_nome = ctk.CTkEntry(frame_form, placeholder_text= "Nome do Funcionário", width=400)
        ent_nome.pack(pady=10, anchor="w", padx=20)
        
        ctk.CTkLabel(frame_form,text="Cargo", font=("Arial",12,"bold")).pack(pady=(10,2),anchor="w",padx=20)
        
        self.menu_cargo = ctk.CTkOptionMenu(
            frame_form,
            values=["Administrador", "Técnico", "Analista de Dados", "Administrador de Banco de Dados", "Recepcionista"],
            width=200,
            dynamic_resizing=False
        )
        self.menu_cargo.pack(pady=(0,10), anchor="w", padx=20)
        self.menu_cargo.set("Selecione...")
        
        
        
