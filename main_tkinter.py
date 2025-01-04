import psycopg2
import customtkinter as ctk
from tkinter import ttk
from datetime import datetime
from tkinter import messagebox


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
            ctk.CTkButton(self.menu_frame, text="Tabela BOM", command=self.show_table_from_db),
            ctk.CTkButton(self.menu_frame, text="Atualizar Dados", command=self.update_database)
        ]

        for btn in self.buttons:
            btn.pack(side="left", padx=10, pady=10)

        # frame de filtros
        self.filter_frame = ctk.CTkFrame(self)
        self.filter_frame.pack(side="top", fill="x", pady=5)

        # adicionar filtros para colunas especificas
        self.filter_comboboxes = {}

        columns_to_filter = ["ORG", "LOCAL", "PLANNER"]
        for col in columns_to_filter:
            label = ctk.CTkLabel(self.filter_frame, text=col)
            label.pack(side="left", padx=5)
            
            combobox = ttk.Combobox(self.filter_frame, state="readonly")
            combobox.pack(side="left", padx=5)
            combobox.bind("<<ComboboxSelected>>", self.filter_data)  # Vincula o evento de seleção
            self.filter_comboboxes[col] = combobox

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
        self.all_data = []  # Armazena todos os dados para buscas e paginação
        self.current_page = 0
        self.rows_per_page = 50

        # Frame de paginação
        self.pagination_frame = ctk.CTkFrame(self)
        self.pagination_frame.pack(side="bottom", fill="x")

        # Label para mostrar a data/hora da última atualização
        self.last_update_label = ctk.CTkLabel(self, text="Última atualização: Nenhuma", font=("Arial", 12), anchor="w")
        self.last_update_label.pack(side="bottom", fill="x", padx=10, pady=5)

         # Atualizar filtros quando a tabela for carregada
        self.update_filters(self.all_data)

    
    def update_filters(self, data):
        # Atualizar valores disponíveis nos filtros
        if not data:
            return

        headers, *rows = data
        for col, combobox in self.filter_comboboxes.items():
            if col in headers:
                col_index = headers.index(col)
                unique_values = sorted({row[col_index] for row in rows})
                combobox["values"] = ["Todos"] + unique_values
                combobox.set("Todos")  # Define o valor padrão como "Todos"

    def filter_data(self, event=None):
        # Filtrar dados com base nos critérios de filtragem
        headers, *rows = self.all_data
        filtered_rows = rows

        for col, combobox in self.filter_comboboxes.items():
            if combobox.get() != "Todos":
                col_index = headers.index(col)
                filtered_rows = [row for row in filtered_rows if row[col_index] == combobox.get()]

        # Atualizar tabela com os dados filtrados
        self.current_page = 0
        self.display_table([headers] + filtered_rows)

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
        self.treeview.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        # Configurar expansão
        container.grid_rowconfigure(0, weight=1)
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
            self.display_table(self.all_data)  # Mostrar todos os dados se o campo de busca estiver vazio
            return

        # Filtrar dados
        headers, *rows = self.all_data
        filtered_data = [row for row in rows if any(search_query in str(cell).lower() for cell in row)]

        # Atualizar exibição
        if filtered_data:
            self.current_page = 0
            self.display_table([headers] + filtered_data)
        else:
            ctk.CTkMessagebox.show_info("Busca", "Nenhum dado encontrado para o termo informado.")

    def show_table_from_db(self):
        # Configurações do banco de dados PostgreSQL
        db_config = {
            "dbname": "db_mrp",  # Substitua pelo nome do seu banco
            "user": "postgres",  # Substitua pelo seu usuário
            "password": "@manaus",  # Substitua pela sua senha
            "host": "localhost",  # Substitua se for um host remoto
        }

        try:
            # Conexão com o banco de dados
            connection = psycopg2.connect(**db_config)
            cursor = connection.cursor()

            # Execute uma consulta SQL
            query = "SELECT file_date, org, child_item, child_desc, child_uit, qpa, local, assy, planner, purchaser, supplier, supplier_name, model_mrp, infor, date, quantity FROM table_bom_teste"  # Ajuste conforme sua tabela e colunas
            cursor.execute(query)
            rows = cursor.fetchall()

            # Formate os dados para exibição
            data = [["DATA DO ARQUIVO", "ORG", "CHILD ITEM", "CHILD DESC", "CHILD UIT", "QPA", "LOCAL", "ASSY", "PLANNER", "PURCHASER", "SUPPLIER", "SUPPLIER NAME", "MODEL MRP", "INFOR", "DATE", "QUANTITY"]]  # Cabeçalhos
            data.extend(rows)

            self.all_data = data  # Salvar todos os dados
            self.current_page = 0
            self.display_table(data)

            # buscar a data mais recente
            cursor.execute("SELECT MAX(file_date) FROM table_bom_teste")
            ultima_data_arquivo = cursor.fetchone()[0]

            # Atualizar a data/hora da última atualização
            current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            data_arquivo_texto = ultima_data_arquivo.strftime("%d/%m/%Y") if ultima_data_arquivo else "Desconhecida"
            self.last_update_label.configure(
                text=f"Última atualização: {current_time} | Data mais recente: {data_arquivo_texto}"
            )
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao acessar o banco de dados: {e}")
        finally:
            if 'connection' in locals():
                connection.close()

    def update_database(self):
        # Função de atualização simulada
        messagebox.showinfo("Atualizar Dados", "Dados atualizados com sucesso!")

    def support_action(self):
        # Função de suporte simulada
        messagebox.showinfo("Suporte", "Ação de suporte ainda não implementada!")


if __name__ == "__main__":
    app = App()
    app.mainloop()
