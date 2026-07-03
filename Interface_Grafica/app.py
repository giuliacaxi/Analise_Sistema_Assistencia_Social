import customtkinter as ctk
from tkinter import messagebox
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

class AppSistemaSocial(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Assistência Social")
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

    def tela_login(self):
        login = self.txt_login.get()
        senha = self.txt_senha.get()
        
        con = self.conectar_banco_dados()
        if not con: return
        
        cursor = con.cursor(dictionary=True)
        
        query = """
            SELECT id_tecnico AS id, nome, cargo FROM tecnicos 
            WHERE login = %s AND senha = %s AND dt_desligamento IS NULL
            
            UNION
            
            SELECT id_coordenador AS id, nome, 'Coordenador' AS cargo FROM coordenadores 
            WHERE login = %s AND senha = %s AND dt_desligamento IS NULL
            
            UNION
            
            SELECT id_operacional AS id, nome, cargo FROM funcionarios 
            WHERE login = %s AND senha = %s AND dt_desligamento IS NULL;    
        """
        
        cursor.execute(query, (login, senha, login, senha, login, senha))
        resultado = cursor.fetchone()
        
        cursor.close()
        con.close()
        
        if resultado:
            self.id_usuario_logado = resultado['id']
            self.usuario_logado = resultado['nome']
            self.nivel_acesso_logado = resultado['nivel_acesso']
            
            messagebox.showinfo("Login Bem-Sucedido", f"Bem-vindo, {self.usuario_logado}!")
            self.tela_principal()
        
        else:
            messagebox.showerror("Login Falhou", "Credenciais inválidas.")
    
    def carregar_painel_principal(self):
        for widget in self.winfo_children():
            widget.destroy()
        
        self.geometry("700x600")
        
        if self.nivel_acesso_logado == "Administrador de Banco de Dados":
            btn_config_sistema.pack(pady=5)
            btn_banco_dados.pack(pady=5)
            
        elif self.nivel_acesso_logado == "Coordenador":
            btn_casos_funcionarios.pack(pady=5)
            btn_atendimentos.pack(pady=5)
            btn_visitas_tecnicos.pack(pady=5)
            btn_relatorios.pack(pady=5)
        
        elif self.nivel_acesso_logado == "Técnico":
            btn_casos_acompanhados.pack(pady=5)
            btn_relatorios_casos.pack(pady=5)
            btn_agendar_visitas.pack(pady=5)
        
        elif self.nivel_acesso_logado == "Administrador":
            btn_cadastrar_novo_usuario.pack(pady=5)
            btn_cadastrar_novo_tecnico.pack(pady=5)
            btn_cadastrar_novo_caso.pack(pady=5)
            btn_transferir_caso.pack(pady=5)
            btn_referenciar_caso.pack(pady=5)
            btn_visualizar_motoristas.pack(pady=5)
            btn_alocar_motorista.pack(pady=5)
        
        elif self.nivel_acesso_logado == "Analista de Dados":
            btn_abrir_dashboard.pack(pady=5)
            btn_visualizar_dados.pack(pady=5)
            btn_gerar_relatorios.pack(pady=5)
        
        elif self.nivel_acesso_logado == "Recepcionista":
            btn_registrar_atendimento_recepcao.pack(pady=5)
            btn_visualizar_agenda_tecnico.pack(pady=5)
            btn_gerar_relatorios_atendimentos.pack(pady=5)
            btn_visualizar_cadastro_usuarios.pack(pady=5)
        pass
    
    def dados_mascarados(lista_usuarios):
        lista_mascarada = []
        for usuario in lista_usuarios:
            nome = usuario['nome']
            nome_mascarado = " ".join([parte[0] + "*" * (len(parte) - 1) for parte in nome.split()])
            
            usuario_anonimo = {
                "id_usuario": usuario['id_usuario'],
                "nome": nome_mascarado,
                "idade": usuario["idade"],
                "sexo": usuario["sexo"],
                "raca": usuario["raca"],
                "nome_familiar": "Informação Oculta",
                "rua": "Informação Oculta",
                "bairro": usuario['bairro'],
                "pcd": usuario['pcd'],
                "telefone": "(XX) XXXXX-XXXX"
            }
            lista_mascarada.append(usuario_anonimo)
        return lista_mascarada
            
    if __name__ == "__main__":
        app = AppSistemaSocial()
        app.mainloop()

