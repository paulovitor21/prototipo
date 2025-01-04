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
        self.support_button = ctk.CTkButton(self.sidebar, text="Suporte")
        self.support_button.pack(pady=10, padx=10, side="bottom")

        # Menu horizontal
        self.menu_frame = ctk.CTkFrame(self, height=50)
        self.menu_frame.pack(side="top", fill="x")

        # Botões do menu horizontal
        self.buttons = [
            ctk.CTkButton(self.menu_frame, text="Tabela Banco", command=self.show_table_from_db),
            ctk.CTkButton(self.menu_frame, text="Atualizar Dados")
        ]

        for btn in self.buttons:
            btn.pack(side="left", padx=10, pady=10)

        # Frame de busca
        self.search_frame = ctk.CTkFrame(self)
        self.search_frame.pack(side="top", fill="x", pady=10)

        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Digite para buscar...")
        self.search_entry.pack(side="left", padx=10, fill="x", expand=True)

        self.search_button = ctk.CTkButton(self.search_frame, text="Buscar", command=self.search_in_table)
        self.search_button.pack(side="left", padx=10)

        # Frame para exibir tabelas
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.pack(side="top", fill="both", expand=True)

        # Inicializar Treeview e controle de paginação
        self.treeview = None
        self.all_data = []  # Armazena todos os dados para buscas e filtros
        self.current_page = 0
        self.rows_per_page = 50
        self.filters = []  # Filtros por coluna

        # Frame de paginação
        self.pagination_frame = ctk.CTkFrame(self)
        self.pagination_frame.pack(side="bottom", fill="x")

    def display_table(self, data):
        # Limpar a tabela atual
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        # Frame para Treeview e barras de rolagem
        container = ctk.CTkFrame(self.table_frame)
        container.pack(fill="both", expand=True)

        # Criar Treeview
        self.treeview = ttk.Treeview(container, columns=data[0], show="headings")

        # Configurar cabeçalhos
        for col in data[0]:
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

        # Filtros por coluna
        self.filters = []
        filter_frame = ctk.CTkFrame(container)
        filter_frame.grid(row=0, column=0, sticky="nsew", pady=5)

        for col in data[0]:
            filter_entry = ctk.CTkEntry(filter_frame, placeholder_text=f"Filtro {col}")
            filter_entry.pack(side="left", padx=5, fill="x", expand=True)
            self.filters.append(filter_entry)

        filter_button = ctk.CTkButton(filter_frame, text="Aplicar Filtros", command=self.apply_filters)
        filter_button.pack(side="left", padx=10)

        # Paginação: calcular os índices
        start_index = self.current_page * self.rows_per_page
        end_index = start_index + self.rows_per_page
        page_data = data[1:][start_index:end_index]

        # Inserir dados
        for i, row in enumerate(page_data):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.treeview.insert("", "end", values=row, tags=(tag,))

        # Adicionar barras de rolagem
        v_scroll = ttk.Scrollbar(container, orient="vertical", command=self.treeview.yview)
        h_scroll = ttk.Scrollbar(container, orient="horizontal", command=self.treeview.xview)
        self.treeview.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        # Posicionar widgets
        self.treeview.grid(row=1, column=0, sticky="nsew")
        v_scroll.grid(row=1, column=1, sticky="ns")
        h_scroll.grid(row=2, column=0, sticky="ew")

        # Configurar expansão
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Atualizar paginação
        self.update_pagination_controls(len(data) - 1)

    def update_pagination_controls(self, total_rows):
        # Limpar controles anteriores
        for widget in self.pagination_frame.winfo_children():
            widget.destroy()

        # Calcular total de páginas
        total_pages = (total_rows + self.rows_per_page - 1) // self.rows_per_page

        # Botão Anterior
        if self.current_page > 0:
            prev_button = ctk.CTkButton(self.pagination_frame, text="Anterior", command=self.previous_page)
            prev_button.pack(side="left", padx=10)

        # Informação da Página
        page_info = ctk.CTkLabel(self.pagination_frame, text=f"Página {self.current_page + 1} de {total_pages}")
        page_info.pack(side="left", padx=10)

        # Botão Próximo
        if self.current_page < total_pages - 1:
            next_button = ctk.CTkButton(self.pagination_frame, text="Próximo", command=self.next_page)
            next_button.pack(side="left", padx=10)

    def apply_filters(self):
        headers, *rows = self.all_data
        filtered_rows = rows

        for i, filter_entry in enumerate(self.filters):
            filter_value = filter_entry.get().lower()
            if filter_value:
                filtered_rows = [row for row in filtered_rows if filter_value in str(row[i]).lower()]

        self.current_page = 0
        self.display_table([headers] + filtered_rows)

    def previous_page(self):
        self.current_page -= 1
        self.display_table(self.all_data)

    def next_page(self):
        self.current_page += 1
        self.display_table(self.all_data)

    def search_in_table(self):
        search_query = self.search_entry.get().lower()
        if not search_query:
            self.current_page = 0
            self.display_table(self.all_data)
            return

        headers, *rows = self.all_data
        filtered_data = [row for row in rows if any(search_query in str(cell).lower() for cell in row)]

        if filtered_data:
            self.current_page = 0
            self.display_table([headers] + filtered_data)
        else:
            ctk.CTkMessagebox.show_info("Busca", "Nenhum dado encontrado para o termo informado.")

    def show_table_from_db(self):
        db_config = {
            "dbname": "db_mrp",
            "user": "postgres",
            "password": "@manaus",
            "host": "localhost",
        }

        try:
            connection = psycopg2.connect(**db_config)
            cursor = connection.cursor()

            query = "SELECT org, child_item, child_desc, child_uit, qpa, local, assy, planner, purchaser, supplier, supplier_name, model_mrp, infor, date, quantity FROM table_bom_teste"
            cursor.execute(query)
            rows = cursor.fetchall()

            data = [["ORG", "CHILD ITEM", "CHILD DESC", "CHILD UIT", "QPA", "LOCAL", "ASSY", "PLANNER", "PURCHASER", "SUPPLIER", "SUPPLIER NAME", "MODEL MRP", "INFOR", "DATE", "QUANTITY"]]
            data.extend(rows)

            self.all_data = data
            self.current_page = 0
            self.display_table(data)

        except Exception as e:
            ctk.CTkMessagebox.show_error("Erro", f"Erro ao acessar o banco de dados: {e}")

        finally:
            if 'connection' in locals():
                connection.close()

if __name__ == "__main__":
    app = App()
    app.mainloop()
