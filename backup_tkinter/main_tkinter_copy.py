import psycopg2
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
            ctk.CTkButton(self.menu_frame, text="Tabela Banco", command=self.show_table_from_db),
            ctk.CTkButton(self.menu_frame, text="Atualizar Dados", command=self.update_database)
        ]

        for btn in self.buttons:
            btn.pack(side="left", padx=10, pady=10)

        # Frame para exibir tabelas
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.pack(side="top", fill="both", expand=True)

        # Inicializar Treeview
        self.treeview = None

        # Dados para paginação
        self.data = []
        self.current_page = 0
        self.records_per_page = 50

        # Frame de paginação
        self.pagination_frame = ctk.CTkFrame(self)
        self.pagination_frame.pack(side="bottom", fill="x")

        # Sub-frame para centralizar os controles de paginação
        self.pagination_controls = ctk.CTkFrame(self.pagination_frame)
        self.pagination_controls.pack(side="bottom", pady=10)

        self.prev_button = ctk.CTkButton(self.pagination_controls, text="Anterior", command=self.prev_page)
        self.prev_button.pack(side="left", padx=10)

        self.page_label = ctk.CTkLabel(self.pagination_controls, text="Página 1")
        self.page_label.pack(side="left", padx=10)

        self.next_button = ctk.CTkButton(self.pagination_controls, text="Próximo", command=self.next_page)
        self.next_button.pack(side="left", padx=10)


    def display_table(self):
        # Limpar a tabela atual
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        # Frame para Treeview e barras de rolagem
        container = ctk.CTkFrame(self.table_frame)
        container.pack(fill="both", expand=True)

        # Criar Treeview
        self.treeview = ttk.Treeview(container, columns=self.data[0], show="headings")

        # Configurar cabeçalhos
        for col in self.data[0]:
            self.treeview.heading(col, text=col)
            self.treeview.column(col, width=150)

        # Configurar estilo
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", rowheight=25, font=("Arial", 12))
        style.map("Treeview", background=[("selected", "#347083")], foreground=[("selected", "white")])
        style.configure("Treeview.Heading", font=("Arial", 14, "bold"))

        # Tags de estilo
        self.treeview.tag_configure("evenrow", background="#f2f2f2")
        self.treeview.tag_configure("oddrow", background="white")

        # Obter dados para a página atual
        start_index = self.current_page * self.records_per_page + 1
        end_index = start_index + self.records_per_page
        page_data = self.data[start_index:end_index]

        # Inserir dados
        for i, row in enumerate(page_data):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.treeview.insert("", "end", values=row, tags=(tag,))

        # Adicionar barras de rolagem
        v_scroll = ttk.Scrollbar(container, orient="vertical", command=self.treeview.yview)
        h_scroll = ttk.Scrollbar(container, orient="horizontal", command=self.treeview.xview)
        self.treeview.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        # Posicionar widgets
        self.treeview.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        # Configurar expansão
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.update_pagination_label()

    def update_pagination_label(self):
        total_pages = (len(self.data) - 1) // self.records_per_page + 1
        self.page_label.configure(text=f"Página {self.current_page + 1} de {total_pages}")

    def next_page(self):
        total_pages = (len(self.data) - 1) // self.records_per_page + 1
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.display_table()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.display_table()

    def show_table_from_db(self):
        # Configurações do banco de dados PostgreSQL
        db_config = {
            "dbname": "db_mrp",
            "user": "postgres",
            "password": "@manaus",
            "host": "localhost",
        }

        try:
            # Conexão com o banco de dados
            connection = psycopg2.connect(**db_config)
            cursor = connection.cursor()

            # Execute uma consulta SQL
            query = "SELECT org, child_item, child_desc, child_uit, qpa, local, assy, planner, purchaser, supplier, supplier_name, model_mrp, infor, date, quantity FROM table_bom_teste"
            cursor.execute(query)
            rows = cursor.fetchall()

            # Formate os dados para exibição
            self.data = [["ORG", "CHILD ITEM", "CHILD DESC", "CHILD UIT", "QPA", "LOCAL", "ASSY", "PLANNER",
                          "PURCHASER", "SUPPLIER", "SUPPLIER NAME", "MODEL MRP", "INFOR", "DATE", "QUANTITY"]]  # Cabeçalhos
            self.data.extend(rows)

            self.current_page = 0
            self.display_table()

        except Exception as e:
            ctk.CTkMessagebox.show_error("Erro", f"Erro ao acessar o banco de dados: {e}")

        finally:
            if 'connection' in locals():
                connection.close()

    def update_database(self):
        # Função de atualização simulada
        ctk.CTkMessagebox.show_info("Atualizar Dados", "Dados atualizados com sucesso!")

    def support_action(self):
        # Função de suporte simulada
        ctk.CTkMessagebox.show_info("Suporte", "Ação de suporte ainda não implementada!")


if __name__ == "__main__":
    app = App()
    app.mainloop()
