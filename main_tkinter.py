import psycopg2
import customtkinter as ctk
from tkinter import ttk
from datetime import datetime
from tkinter import messagebox
import pandas as pd  # Para manipulação de arquivos Excel


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
            ctk.CTkButton(self.menu_frame, text="Plan Assy", command=self.show_table_plan_assy),
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
        headers, *rows = self.all_data
        filtered_rows = rows

        for col, combobox in self.filter_comboboxes.items():
            if combobox.get() != "Todos":
                col_index = headers.index(col)
                filtered_rows = [row for row in filtered_rows if row[col_index] == combobox.get()]

        self.current_page = 0
        self.display_table([headers] + filtered_rows)

    def display_table(self, data):
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        container = ctk.CTkFrame(self.table_frame)
        container.pack(fill="both", expand=True)

        self.treeview = ttk.Treeview(container, columns=data[0], show="headings")

        for col in data[0]:
            self.treeview.heading(col, text=col)
            self.treeview.column(col, width=150)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", rowheight=25, font=("Arial", 12))
        style.map("Treeview", background=[("selected", "#347083")], foreground=[("selected", "white")])
        style.configure("Treeview.Heading", font=("Arial", 14, "bold"))

        self.treeview.tag_configure("evenrow", background="#f2f2f2")
        self.treeview.tag_configure("oddrow", background="white")

        start_index = self.current_page * self.rows_per_page
        end_index = start_index + self.rows_per_page
        page_data = data[1:][start_index:end_index]

        for i, row in enumerate(page_data):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.treeview.insert("", "end", values=row, tags=(tag,))

        v_scroll = ttk.Scrollbar(container, orient="vertical", command=self.treeview.yview)
        h_scroll = ttk.Scrollbar(container, orient="horizontal", command=self.treeview.xview)
        self.treeview.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.treeview.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.update_pagination_controls(len(data) - 1)

    def update_pagination_controls(self, total_rows):
        for widget in self.pagination_frame.winfo_children():
            widget.destroy()

        total_pages = (total_rows + self.rows_per_page - 1) // self.rows_per_page

        if self.current_page > 0:
            prev_button = ctk.CTkButton(self.pagination_frame, text="Anterior", command=self.previous_page)
            prev_button.pack(side="left", padx=10)

        page_info = ctk.CTkLabel(self.pagination_frame, text=f"Página {self.current_page + 1} de {total_pages}")
        page_info.pack(side="left", padx=10)

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

            query = "SELECT file_date, org, child_item, child_desc, child_uit, qpa, local, assy, planner, purchaser, supplier, supplier_name, model_mrp, infor, date, quantity FROM table_bom"
            cursor.execute(query)
            rows = cursor.fetchall()

            data = [["DATA DO ARQUIVO", "ORG", "CHILD ITEM", "CHILD DESC", "CHILD UIT", "QPA", "LOCAL", "ASSY", "PLANNER", "PURCHASER", "SUPPLIER", "SUPPLIER NAME", "MODEL MRP", "INFOR", "DATE", "QUANTITY"]]
            data.extend(rows)

            self.all_data = data
            self.current_page = 0
            self.display_table(data)

            cursor.execute("SELECT MAX(file_date) FROM table_bom")
            ultima_data_arquivo = cursor.fetchone()[0]

            current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            data_arquivo_texto = ultima_data_arquivo.strftime("%d/%m/%Y") if ultima_data_arquivo else "Desconhecida"
            self.last_update_label.configure(
                text=f"Última atualização: {current_time} | Data mais recente: {data_arquivo_texto}"
            )

            if not hasattr(self, "export_button"):
                self.export_button = ctk.CTkButton(
                    self,
                    text="Exportar para Excel",
                    command=self.export_to_excel
                )
                self.export_button.place(relx=0.95, rely=0.95, anchor="se")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao acessar o banco de dados: {e}")
        finally:
            if 'connection' in locals():
                connection.close()

    def export_to_excel(self):
        if len(self.all_data) <= 1:
            messagebox.showerror("Erro", "Nenhum dado disponível para exportação.")
            return

        headers = self.all_data[0]
        rows = self.all_data[1:]
        df = pd.DataFrame(rows, columns=headers)

        save_path = "dados_exportados.xlsx"
        try:
            df.to_excel(save_path, index=False)
            messagebox.showinfo("Sucesso", f"Dados exportados com sucesso para {save_path}!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar dados: {e}")

    def show_table_plan_assy(self):
        # Implementar funcionalidade para exibir a tabela Plan Assy
        pass

    def update_database(self):
        # Implementar funcionalidade para atualizar o banco de dados
        pass

    def support_action(self):
        # Implementar funcionalidade para suporte
        pass


if __name__ == "__main__":
    app = App()
    app.mainloop()
