import customtkinter as ctk
from tkinter import ttk

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurações principais da janela
        self.title("Interface Exemplo")
        self.geometry("1000x600")

        # Menu lateral
        self.sidebar = ctk.CTkFrame(self, width=150)
        self.sidebar.pack(side="left", fill="y")

        # Logo
        self.logo_label = ctk.CTkLabel(self.sidebar, text="LOGO", font=("Arial", 20, "bold"))
        self.logo_label.pack(pady=20)

        # Botão de suporte
        self.support_button = ctk.CTkButton(self.sidebar, text="Suporte", command=self.support_action)
        self.support_button.pack(pady=10, padx=10, side="bottom")

        # Menu horizontal
        self.menu_frame = ctk.CTkFrame(self, height=50)
        self.menu_frame.pack(side="top", fill="x")

        # Botões do menu horizontal
        self.buttons = [
            ctk.CTkButton(self.menu_frame, text="Tabela 1", command=self.show_table_1),
            ctk.CTkButton(self.menu_frame, text="Tabela 2", command=self.show_table_2),
            ctk.CTkButton(self.menu_frame, text="Tabela 3", command=self.show_table_3),
            ctk.CTkButton(self.menu_frame, text="Atualizar Dados", command=self.update_database)
        ]

        for btn in self.buttons:
            btn.pack(side="left", padx=10, pady=10)

        # Frame para exibir tabelas
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.pack(side="top", fill="both", expand=True)
        
        # Inicializar Treeview
        self.treeview = None

    def show_table_1(self):
        data = [
            ["ID", "Nome", "Valor"],
            [1, "Produto A", 100],
            [2, "Produto B", 200],
            [3, "Produto C", 300]
        ]
        self.display_table(data)

    def show_table_2(self):
        data = [
            ["ID", "Item", "Quantidade"],
            [101, "Peça X", 50],
            [102, "Peça Y", 75],
            [103, "Peça Z", 100]
        ]
        self.display_table(data)

    def show_table_3(self):
        data = [
            ["Código", "Descrição", "Preço"],
            ["001", "Serviço A", 500],
            ["002", "Serviço B", 1000],
            ["003", "Serviço C", 1500]
        ]
        self.display_table(data)

    def display_table(self, data):
        # Limpar a tabela atual
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        # Criar Treeview
        self.treeview = ttk.Treeview(self.table_frame, columns=data[0], show="headings")
        
        # Configurar cabeçalhos
        for col in data[0]:
            self.treeview.heading(col, text=col)
            self.treeview.column(col, width=150)

        # Inserir dados
        for row in data[1:]:
            self.treeview.insert("", "end", values=row)

        self.treeview.pack(fill="both", expand=True)

    def update_database(self):
        # Função de atualização simulada
        ctk.CTkMessagebox.show_info("Atualizar Dados", "Dados atualizados com sucesso!")

    def support_action(self):
        # Função de suporte simulada
        ctk.CTkMessagebox.show_info("Suporte", "Ação de suporte ainda não implementada!")

if __name__ == "__main__":
    app = App()
    app.mainloop()
