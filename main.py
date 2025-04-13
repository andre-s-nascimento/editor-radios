import json
import os
import re
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import Menu
from pathlib import Path
from datetime import datetime

class RadioStationEditor:

    def __init__(self, root):
        self.root = root    
            
        # Configura os paths
        self.base_dir = Path(__file__).parent
        self.languages_dir = self.base_dir / "languages"
        self.settings_path = self.base_dir / "user_settings.json"

        # Cria a pasta languages se não existir
        self.languages_dir.mkdir(exist_ok=True)
        
        self.default_language = 'pt_BR'
        self.current_language = self.load_last_language()
        self.load_language_config()

        self.root.title(self.config['app_title'])
        self.stations = []
        self.current_file = ""
        self.sort_column = None
        self.sort_direction = False
        
        # Configurar a interface
        self.verify_structure()
        self.create_widgets()
        self.create_menu()
        self.load_language_config(self.current_language)
        
    def get_language_path(self, lang_code):
        """Retorna o caminho completo para o arquivo de idioma"""
        return self.languages_dir / f"config_{lang_code}.json"

    def load_last_language(self):
        """Carrega o último idioma usado"""
        try:
            if self.settings_path.exists():
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    return json.load(f).get('language', self.default_language)
            else:
                # Cria arquivo com idioma padrão se não existir
                self.save_language_preference(self.default_language)
                return self.default_language
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
            return self.default_language

    def save_language_preference(self, language):
        """Salva o idioma preferido"""
        try:
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump({'language': language}, f, indent=4)
        except Exception as e:
            print(f"Erro ao salvar preferências: {e}")

    def load_language_config(self, lang_code=None):
        """Carrega o arquivo de idioma com parâmetro opcional"""
        lang_code = lang_code or self.current_language or self.default_language
        lang_file = self.get_language_path(lang_code)

        try:
            with open(lang_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            self.current_language = lang_code
            return True
        except Exception as e:
            print(f"Erro ao carregar {lang_file}: {e}")
            if lang_code != self.default_language:
                return self.load_language_config(self.default_language)
            return False

    def get_project_path():
        """Retorna o caminho correto mesmo quando empacotado"""
        if getattr(sys, 'frozen', False):
            # Se estiver executando como um executável empacotado
            return Path(sys.executable).parent
        else:
            # Se estiver executando como script Python
            return Path(__file__).parent
        
    def get_config_path(self, lang_code):
        """Retorna o caminho relativo para o arquivo de idioma"""
        return self.project_path / f"config_{lang_code}.json"

    def change_language(self, lang_code):
        """Altera o idioma e persiste a escolha"""
        if self.load_language_config(lang_code):
            self.save_language_preference(lang_code)
            self.reload_ui()
        else:
            # Mensagem de erro atualizada com o caminho correto
            lang_file = self.get_language_path(lang_code)
            messagebox.showerror(
                "Erro",
                f"Falha ao carregar idioma {lang_code}\n"
                f"Verifique se o arquivo existe em:\n{lang_file}"
            )
    
    def validate_config(self):
        """Garante que o arquivo de idioma tem todas chaves necessárias"""
        required_keys = {
            'buttons': ['open', 'save', 'add', 'edit', 'remove', 'language'],
            'columns': ['favorite', 'name', 'genre', 'country', 'bitrate'],
            'messages': ['save_success', 'save_error', 'confirm_remove']
        }
        
        # Adiciona valores padrão se alguma chave faltar
        for category, keys in required_keys.items():
            if category not in self.config:
                self.config[category] = {}
            for key in keys:
                if key not in self.config[category]:
                    self.config[category][key] = f"[[{key}]]"  # Marcador visível

    def verify_structure(self):
        """Verifica se a estrutura de arquivos está correta"""
        errors = []

        # Verifica arquivo de configuração principal
        if not self.settings_path.exists():
            errors.append(f"Arquivo {self.settings_path} não encontrado")

        # Verifica se existe pelo menos o idioma padrão
        default_lang_path = self.get_language_path(self.default_language)
        if not default_lang_path.exists():
            errors.append(f"Arquivo de idioma padrão {default_lang_path} não encontrado")

        if errors:
            messagebox.showerror(
                "Problemas na Estrutura",
                "Os seguintes problemas foram encontrados:\n\n" + 
                "\n".join(errors) +
                "\n\nO programa pode não funcionar corretamente."
            )
            return False
        return True

    def create_menu(self):
        menubar = Menu(self.root)
        language_menu = Menu(menubar, tearoff=0)

        # Carrega a lista de idiomas do config atual
        for lang_code, lang_name in self.config['languages'].items():
            language_menu.add_command(
                label=lang_name,
                command=lambda lc=lang_code: self.change_language(lc)
            )

        menubar.add_cascade(label=self.config['buttons']['language'], menu=language_menu)
        self.root.config(menu=menubar)

    def reload_ui(self):
        # Atualiza título da janela
        self.root.title(self.config['app_title'])
        
        # Atualiza botões (precisa manter referência aos botões)
        for btn, text_key in zip(self.buttons, ['open', 'save', 'add', 'edit', 'remove']):
            btn.config(text=self.config['buttons'][text_key])
        
        # Atualiza cabeçalhos da treeview
        for col, text_key in zip(self.tree['columns'], ['favorite', 'name', 'genre', 'country', 'bitrate']):
            self.tree.heading(col, text=self.config['columns'][text_key])
        
        # Atualiza menu
        self.create_menu()

    def load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except Exception as e:
            # Configuração padrão caso o arquivo não exista
            self.config = {
                "app_title": "🎧 Editor de Estações de Rádio 📻",
                "buttons": {
                    "open": "📂 Abrir",
                    "save": "💾 Salvar",
                    "add": "➕ Adicionar",
                    "edit": "✏️ Editar",
                    "remove": "❌ Remover"
                },
                "columns": {
                    "favorite": "⭐ Favorita",
                    "name": "📻 Nome",
                    "genre": "🎵 Gênero",
                    "country": "🌍 País",
                    "bitrate": "🔊 Bitrate (kbps)"
                },
                "messages": {
                    "save_success": "Arquivo salvo com sucesso!",
                    "save_error": "Falha ao salvar arquivo: {error}",
                    "confirm_remove": "Tem certeza que deseja remover esta estação?"
                }
            }
        
    def create_widgets(self):
        # Frame superior com botões
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=5, pady=10)
        
        button_container = tk.Frame(top_frame)
        button_container.pack(expand=True)
        
        button_config = {
            'padx': 12,
            'pady': 6,
            'font': ('Arial', 10)
        }
        
        # Cria e armazena referência aos botões
        self.buttons = []
        for text_key in ['open', 'save', 'add', 'edit', 'remove']:
            btn = tk.Button(
                button_container,
                text=self.config['buttons'][text_key],
                command=getattr(self, {
                    'open': 'open_file',
                    'save': 'save_file',
                    'add': 'add_station',
                    'edit': 'edit_selected_station',
                    'remove': 'remove_station'
                }[text_key]),
                **button_config
            )
            btn.pack(side=tk.LEFT, padx=5)
            self.buttons.append(btn)
        
        # Frame principal com treeview
        main_frame = tk.Frame(self.root)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        
        # Árvore para exibir as estações
        self.tree = ttk.Treeview(main_frame, columns=('Favorite', 'Name', 'Genre', 'Country', 'Bitrate'), show='headings')
        
        # Configurar cabeçalhos
        for col, text_key in zip(self.tree['columns'], ['favorite', 'name', 'genre', 'country', 'bitrate']):
            self.tree.heading(col, text=self.config['columns'][text_key], 
                            command=lambda c=col: self.sort_treeview(c))
        
        # Configurar colunas
        self.tree.column('Favorite', width=80, anchor=tk.CENTER)
        self.tree.column('Name', width=250, anchor=tk.W)
        self.tree.column('Genre', width=150, anchor=tk.W)
        self.tree.column('Country', width=100, anchor=tk.W)
        self.tree.column('Bitrate', width=100, anchor=tk.CENTER)
        
        # Scrollbars
        y_scroll = ttk.Scrollbar(main_frame, orient="vertical", command=self.tree.yview)
        x_scroll = ttk.Scrollbar(main_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        # Layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Eventos
        self.tree.bind('<Double-1>', lambda e: self.edit_selected_station())
    
    def sort_treeview(self, column):
        if self.sort_column == column:
            self.sort_direction = not self.sort_direction
        else:
            self.sort_column = column
            self.sort_direction = False
        
        # Converter ★ para booleanos para ordenação
        if column == 'Favorite':
            items = [(self.tree.set(child, column) == '★', child) 
                    for child in self.tree.get_children('')]
        else:
            items = [(self.tree.set(child, column).lower(), child) 
                    for child in self.tree.get_children('')]
        
        items.sort(reverse=self.sort_direction)
        
        for index, (_, child) in enumerate(items):
            self.tree.move(child, '', index)
        
        # Atualizar cabeçalho com indicador de ordenação
        for col in self.tree['columns']:
            header_text = self.tree.heading(col)['text']
            if col == column:
                arrow = ' ↓' if self.sort_direction else ' ↑'
                if arrow not in header_text:
                    header_text = header_text.split(' ↓')[0].split(' ↑')[0] + arrow
            else:
                header_text = header_text.split(' ↓')[0].split(' ↑')[0]
            self.tree.heading(col, text=header_text)
        
    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("SII files", "*.sii"), ("All files", "*.*")])
        if file_path:
            # Criar backup antes de abrir
            try:
                backup_dir = os.path.join(os.path.dirname(file_path), "backup")
                os.makedirs(backup_dir, exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.basename(file_path)
                backup_path = os.path.join(backup_dir, f"{filename}.bak_{timestamp}")
                
                # Copiar o arquivo original para o backup
                import shutil
                shutil.copy2(file_path, backup_path)
                
                messagebox.showinfo(
                    "Backup criado",
                    f"Backup do arquivo criado com sucesso em:\n{backup_path}"
                )
            except Exception as e:
                messagebox.showwarning(
                    "Aviso de Backup",
                    f"Não foi possível criar backup:\n{str(e)}\n\nContinuando sem backup..."
                )
            
            self.current_file = file_path
            self.stations = self.load_file(file_path)
            self.update_treeview()

    def save_file(self):
        if not self.current_file:
            messagebox.showerror(
                self.config['messages'].get('error_title', 'Error'),
                self.config['messages']['no_file']
            )
            return
        
        if not self.stations:
            messagebox.showwarning(
                self.config['messages'].get('warning_title', 'Warning'),
                self.config['messages']['no_stations']
            )
            return
        
        if not self.current_file.lower().endswith('.sii'):
            self.current_file += '.sii'
        
        try:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                # Escreve o cabeçalho SiiNunit
                f.write("SiiNunit\n")
                f.write("{\n")
                f.write("live_stream_def : _nameless.28a.c076.a0f0 {\n")
                f.write(f" stream_data: {len(self.stations)}\n")
                
                # Escreve cada estação
                for i, station in enumerate(self.stations):
                    url_encoded = self.encode_to_escaped(station['url'])
                    name_encoded = self.encode_to_escaped(station['name'])
                    genre_encoded = self.encode_to_escaped(station['genre'])
                
                    line = f' stream_data[{i}]: "{url_encoded}|{name_encoded}|{genre_encoded}|{station["country"]}|{station["bitrate"]}|{int(station["favorite"])}"\n'
                    f.write(line)
                
                # Fecha a estrutura
                f.write(" }\n")
                f.write("}\n")
        
            messagebox.showinfo(
                self.config['messages'].get('success_title', 'Success'),
                self.config['messages']['save_success']
            )
        except Exception as e:
            messagebox.showerror(
                self.config['messages'].get('error_title', 'Error'),
                self.config['messages']['save_error'].format(error=str(e))
            )

    def load_file(self, filename):
        stations = []
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                station = self.parse_line(line)
                if station:
                    stations.append(station)
        return stations
    
    def parse_line(self, line):
        match = re.search(r'"(.*?)"', line)
        if not match:
            return None
        
        content = match.group(1)
        parts = content.split('|')
        
        if len(parts) < 5:
            return None
        
        # Decodifica cada parte
        decoded_parts = [self.decode_escaped_string(part) for part in parts]
        
        return {
            'url': decoded_parts[0],
            'name': decoded_parts[1],
            'genre': decoded_parts[2],
            'country': decoded_parts[3],
            'bitrate': decoded_parts[4],
            'favorite': bool(int(decoded_parts[5])) if len(decoded_parts) > 5 else False
        }
    
    def decode_escaped_string(self, s):
        try:
            # Primeiro, interpreta as sequências de escape (como \xd0) como bytes
            bytes_content = s.encode('latin1').decode('unicode-escape').encode('latin1')
            
            # Agora decodifica os bytes resultantes como UTF-8
            decoded = bytes_content.decode('utf-8')
            return decoded
        except Exception as e:
            print(f"Erro ao decodificar '{s}': {e}")
            return s

    def encode_to_escaped(self, s):
        try:
            # Converte para bytes UTF-8, depois cria sequência de escape
            escaped = s.encode('utf-8').decode('latin1').encode('unicode-escape').decode('ascii')
            return escaped
        except Exception as e:
            print(f"Erro ao codificar '{s}': {e}")
            return s
    
    def update_treeview(self):
        self.tree.delete(*self.tree.get_children())
        for station in self.stations:
            self.tree.insert('', 'end', values=(
                '★' if station['favorite'] else '',
                station['name'],
                station['genre'],
                station['country'],
                station['bitrate']
            ))
    
    def add_station(self):
        self.edit_station(None)
    
    def edit_selected_station(self, event=None):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                self.config['messages'].get('warning_title', 'Warning'),
                self.config['messages']['select_station']
            )
            return
        item_id = selected[0]
        index = self.tree.index(item_id)
        self.edit_station(index)

    def edit_station(self, index=None):
        if index is None:
            # Modo de adição
            station = {
                'url': '',
                'name': '',
                'genre': '',
                'country': '',
                'bitrate': '128',
                'favorite': False
            }
            title = self.config['messages'].get('add_title', 'Add Station')
        else:
            # Modo de edição
            station = self.stations[index]
            title = self.config['messages'].get('edit_title', 'Edit Station')

        # Janela de edição
        edit_win = tk.Toplevel(self.root)
        edit_win.title(title)

        # Dicionário de labels traduzidos
        labels = {
            'url': self.config['messages'].get('url_label', 'URL:'),
            'name': self.config['messages'].get('name_label', 'Name:'),
            'genre': self.config['messages'].get('genre_label', 'Genre:'),
            'country': self.config['messages'].get('country_label', 'Country:'),
            'bitrate': self.config['messages'].get('bitrate_label', 'Bitrate:'),
            'favorite': self.config['messages'].get('favorite_label', 'Favorite:'),
            'save_btn': self.config['messages'].get('save_btn', 'Save')
        }

        # Campos do formulário
        tk.Label(edit_win, text=labels['url']).grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)
        url_entry = tk.Entry(edit_win, width=50)
        url_entry.grid(row=0, column=1, padx=5, pady=5)
        url_entry.insert(0, station['url'])

        tk.Label(edit_win, text=labels['name']).grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)
        name_entry = tk.Entry(edit_win, width=50)
        name_entry.grid(row=1, column=1, padx=5, pady=5)
        name_entry.insert(0, station['name'])

        tk.Label(edit_win, text=labels['genre']).grid(row=2, column=0, sticky=tk.E, padx=5, pady=5)
        genre_entry = tk.Entry(edit_win, width=50)
        genre_entry.grid(row=2, column=1, padx=5, pady=5)
        genre_entry.insert(0, station['genre'])

        tk.Label(edit_win, text=labels['country']).grid(row=3, column=0, sticky=tk.E, padx=5, pady=5)
        country_entry = tk.Entry(edit_win, width=10)
        country_entry.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        country_entry.insert(0, station['country'])

        tk.Label(edit_win, text=labels['bitrate']).grid(row=4, column=0, sticky=tk.E, padx=5, pady=5)
        bitrate_entry = tk.Entry(edit_win, width=10)
        bitrate_entry.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        bitrate_entry.insert(0, station['bitrate'])

        tk.Label(edit_win, text=labels['favorite']).grid(row=5, column=0, sticky=tk.E, padx=5, pady=5)
        favorite_var = tk.BooleanVar(value=station['favorite'])
        tk.Checkbutton(edit_win, variable=favorite_var).grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)

        def save_changes():
            new_station = {
                'url': url_entry.get(),
                'name': name_entry.get(),
                'genre': genre_entry.get(),
                'country': country_entry.get(),
                'bitrate': bitrate_entry.get(),
                'favorite': favorite_var.get()
            }

            if index is None:
                self.stations.append(new_station)
            else:
                self.stations[index] = new_station

            self.update_treeview()
            edit_win.destroy()

        tk.Button(edit_win, text=labels['save_btn'], command=save_changes).grid(row=6, column=1, sticky=tk.E, padx=5, pady=5)

    def remove_station(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                self.config['messages'].get('warning_title', 'Warning'),
                self.config['messages']['select_station']
            )
            return
    
        if messagebox.askyesno(
            self.config['messages'].get('confirm_title', 'Confirm'),
            self.config['messages']['confirm_remove']
        ):
            item_id = selected[0]
            index = self.tree.index(item_id)
            del self.stations[index]
            self.update_treeview()

    def debug_language_files(self):
        """Mostra informações úteis para debug"""
        print("\n=== DEBUG DE ARQUIVOS DE IDIOMA ===")
        print(f"Pasta de idiomas: {self.languages_dir}")
        print(f"Idioma atual: {self.current_language}")

        # Lista todos os arquivos de idioma disponíveis
        print("\nArquivos de idioma encontrados:")
        for file in self.languages_dir.glob("config_*.json"):
            print(f"- {file.name}")

        # Verifica o arquivo do idioma atual
        current_file = self.get_language_path(self.current_language)
        print(f"\nArquivo atual: {current_file}")
        print(f"Existe? {current_file.exists()}")

        if current_file.exists():
            with open(current_file, 'r', encoding='utf-8') as f:
                print(f"Conteúdo válido? {'sim' if json.load(f) else 'não'}")
        print("==================================\n")

if __name__ == "__main__":
    
    root = tk.Tk()
    app = RadioStationEditor(root)
    
    if app.verify_structure():
        root.geometry("900x600")
        root.mainloop()
    else:
        root.destroy()