import sys
import os
import json
import shutil
import tempfile
import unittest
from unittest.mock import patch, MagicMock, mock_open, call
from datetime import datetime
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import RadioStationEditor

class TestRadioStationEditorBase(unittest.TestCase):
    def setUp(self):
        self.root = MagicMock()
        self.editor = RadioStationEditor(self.root)
        self.editor.config = {
            'messages': {
                'backup_success': 'Backup success',
                'backup_warning': 'Backup warning',
                'backup_title_success': 'Success',
                'backup_title_warning': 'Warning',
                'load_error': 'Load error',
                'save_success': 'Save success',
                'save_error': 'Save error',
                'confirm_remove': 'Confirm remove',
                'select_station': 'Select station',
                'no_file': 'No file',
                'no_stations': 'No stations'
            },
            'buttons': {},
            'columns': {},
            'languages': {'en': 'English', 'pt_BR': 'Portuguese'}
        }

class TestInitialization(TestRadioStationEditorBase):
    def test_initialization(self):
        self.assertEqual(self.editor.stations, [])
        self.assertEqual(self.editor.current_file, "")
        self.assertIsNone(self.editor.sort_column)
        self.assertFalse(self.editor.sort_direction)
        
    def test_verify_structure(self):
        # Mock da messagebox
        with patch('main.messagebox') as mock_msg:
            # Teste com estrutura válida
            with tempfile.TemporaryDirectory() as temp_dir:
                # Criar estrutura válida
                lang_dir = os.path.join(temp_dir, "languages")
                os.makedirs(lang_dir, exist_ok=True)
                
                # Criar settings.json
                settings_file = os.path.join(temp_dir, "user_settings.json")
                with open(settings_file, 'w') as f:
                    json.dump({'language': 'en'}, f)
                
                # Criar arquivo de idioma padrão
                lang_file = os.path.join(lang_dir, f"config_{self.editor.default_language}.json")
                with open(lang_file, 'w') as f:
                    json.dump({}, f)
                
                # Substituir os paths do editor
                original_base = self.editor.base_dir
                original_settings = self.editor.settings_path
                original_lang_dir = self.editor.languages_dir
                
                self.editor.base_dir = Path(temp_dir)
                self.editor.settings_path = Path(settings_file)
                self.editor.languages_dir = Path(lang_dir)
                
                result = self.editor.verify_structure()
                self.assertTrue(result, "Deveria retornar True para estrutura válida")
                mock_msg.showerror.assert_not_called()
                
                # Restaurar configurações originais
                self.editor.base_dir = original_base
                self.editor.settings_path = original_settings
                self.editor.languages_dir = original_lang_dir
            
            # Teste com estrutura inválida
            with tempfile.TemporaryDirectory() as temp_dir:
                # Substituir os paths do editor (diretório vazio)
                original_base = self.editor.base_dir
                original_settings = self.editor.settings_path
                original_lang_dir = self.editor.languages_dir
                
                self.editor.base_dir = Path(temp_dir)
                self.editor.settings_path = Path(temp_dir) / "user_settings.json"
                self.editor.languages_dir = Path(temp_dir) / "languages"
                
                result = self.editor.verify_structure()
                self.assertFalse(result, "Deveria retornar False para estrutura inválida")
                mock_msg.showerror.assert_called_once()
                
                # Restaurar configurações originais
                self.editor.base_dir = original_base
                self.editor.settings_path = original_settings
                self.editor.languages_dir = original_lang_dir

class TestLanguageFunctions(TestRadioStationEditorBase):
    def test_load_last_language(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            # Teste com arquivo existente
            settings_path = os.path.join(temp_dir, "user_settings.json")
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump({'language': 'pt_BR'}, f)

            original_path = self.editor.settings_path
            self.editor.settings_path = Path(settings_path)

            result = self.editor.load_last_language()
            self.assertEqual(result, 'pt_BR')

            # Teste com arquivo não existente (deve criar)
            non_existent_path = os.path.join(temp_dir, "new_settings.json")
            self.editor.settings_path = Path(non_existent_path)

            result = self.editor.load_last_language()
            self.assertEqual(result, self.editor.default_language)
            self.assertTrue(os.path.exists(non_existent_path)), "Arquivo deveria ter sido criado"

            # Verifica o conteúdo do arquivo criado
            with open(non_existent_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                self.assertEqual(content['language'], self.editor.default_language)

            self.editor.settings_path = original_path

    def test_save_language_preference(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_path = os.path.join(temp_dir, "user_settings.json")
            original_path = self.editor.settings_path
            self.editor.settings_path = Path(settings_path)
            
            self.editor.save_language_preference('es')
            with open(settings_path, 'r') as f:
                data = json.load(f)
                self.assertEqual(data['language'], 'es')
            
            self.editor.settings_path = original_path

    def test_change_language(self):
        with patch.object(self.editor, 'load_language_config') as mock_load:
            mock_load.return_value = True
            with patch.object(self.editor, 'save_language_preference') as mock_save:
                with patch.object(self.editor, 'reload_ui') as mock_reload:
                    # Teste com sucesso
                    result = self.editor.change_language('pt_BR')
                    self.assertTrue(result)  # Agora deve passar
                    mock_load.assert_called_with('pt_BR')
                    mock_save.assert_called_with('pt_BR')
                    mock_reload.assert_called_once()

                    # Teste com falha
                    mock_load.return_value = False
                    with patch('main.messagebox') as mock_msg:
                        result = self.editor.change_language('invalid')
                        self.assertFalse(result)  # Teste para caso de falha
                        mock_msg.showerror.assert_called_once()

    def test_change_language_failure(self):
        """Testa comportamento com chaves de tradução faltando"""
        # Simular falta de chaves específicas
        del self.editor.config['messages']['backup_title_success']
        del self.editor.config['messages']['backup_success']

        # Garantir que outras chaves necessárias existam
        self.editor.config['messages'].update({
            'backup_title_warning': 'Backup Warning',
            'backup_warning': 'Backup warning: {error}'
        })

        # Forçar um erro no backup para testar o caminho de falha
        with patch('main.messagebox') as mock_msg:  # Corrigido aqui
            with patch.object(self.editor, 'load_language_config') as mock_load:
                mock_load.return_value = False
                with patch.object(self.editor, 'get_language_path') as mock_path:
                    mock_path.return_value = '/path/to/config.json'

                    result = self.editor.change_language('invalid')
                    self.assertFalse(result)
                    mock_msg.showerror.assert_called_once()

class TestFileOperations(TestRadioStationEditorBase):
    def setUp(self):
        super().setUp()
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test.sii")
        with open(self.test_file, 'w') as f:
            f.write("SiiNunit\n{\n live_stream_def : _nameless.28a.c076.a0f0 {\n stream_data: 1\n stream_data[0]: \"http://example.com|Test|Pop|US|128|1\"\n }\n}")
        
        self.editor.current_file = self.test_file
        # Adicione um mock para a treeview
        self.editor.tree = MagicMock()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_save_file_success(self):
        self.editor.stations = [{
            'url': 'http://test.com',
            'name': 'Test',
            'genre': 'Rock',
            'country': 'BR',
            'bitrate': '192',
            'favorite': False
        }]
        
        output_file = os.path.join(self.test_dir, "output.sii")
        self.editor.current_file = output_file
        
        with patch('main.messagebox') as mock_msg:
            self.editor.save_file()
            self.assertTrue(os.path.exists(output_file))
            mock_msg.showinfo.assert_called_once_with('Success', 'Save success')

    def test_save_file_error(self):
        self.editor.stations = [{'url': 'test'}]
        self.editor.current_file = "/invalid/path/test.sii"
        
        with patch('main.messagebox') as mock_msg:
            self.editor.save_file()
            mock_msg.showerror.assert_called_once()
            args, _ = mock_msg.showerror.call_args
            self.assertEqual(args[0], 'Error')

    def test_save_file_no_stations(self):
        self.editor.stations = []
        with patch('main.messagebox') as mock_msg:
            self.editor.save_file()
            mock_msg.showwarning.assert_called_once_with('Warning', 'No stations')

    def test_save_file_no_file(self):
        self.editor.current_file = ""
        with patch('main.messagebox') as mock_msg:
            self.editor.save_file()
            mock_msg.showerror.assert_called_once_with('Error', 'No file')

class TestStationParsing(TestRadioStationEditorBase):
    def test_parse_line_valid(self):
        line = ' stream_data[0]: "http://test.com|Test Station|Rock|US|128|1"'
        result = self.editor.parse_line(line)
        self.assertEqual(result['url'], "http://test.com")
        self.assertEqual(result['name'], "Test Station")
        self.assertEqual(result['genre'], "Rock")
        self.assertEqual(result['country'], "US")
        self.assertEqual(result['bitrate'], "128")
        self.assertTrue(result['favorite'])

    def test_parse_line_invalid(self):
        line = 'invalid line'
        result = self.editor.parse_line(line)
        self.assertIsNone(result)

    def test_parse_line_missing_parts(self):
        line = ' stream_data[0]: "http://test.com|Name only"'
        result = self.editor.parse_line(line)
        self.assertIsNone(result)

    def test_decode_escaped_string(self):
        test_str = "Test\\xd0\\x9f\\xd1\\x80\\xd0\\xb8\\xd0\\xb2\\xd0\\xb5\\xd1\\x82"
        result = self.editor.decode_escaped_string(test_str)
        self.assertEqual(result, "TestПривет")

    def test_encode_to_escaped(self):
        test_str = "TestПривет"
        result = self.editor.encode_to_escaped(test_str)
        # Verifica se a string codificada pode ser decodificada de volta
        decoded = self.editor.decode_escaped_string(result)
        self.assertEqual(decoded, test_str)

class TestTreeViewOperations(TestRadioStationEditorBase):
    def setUp(self):
        super().setUp()
        self.editor.stations = [
            {
                'url': 'http://test1.com',
                'name': 'Station 1',
                'genre': 'Pop',
                'country': 'US',
                'bitrate': '128',
                'favorite': True
            },
            {
                'url': 'http://test2.com',
                'name': 'Station 2',
                'genre': 'Rock',
                'country': 'UK',
                'bitrate': '192',
                'favorite': False
            }
        ]
        self.editor.tree = MagicMock()
        self.editor.tree.get_children.return_value = ['item1', 'item2']

    def test_update_treeview(self):
        with patch.object(self.editor.tree, 'delete') as mock_delete:
            with patch.object(self.editor.tree, 'insert') as mock_insert:
                self.editor.update_treeview()
                mock_delete.assert_called_once_with('item1', 'item2')
                self.assertEqual(mock_insert.call_count, 2)

    def test_sort_treeview(self):
        self.editor.tree.get_children.return_value = ['item1', 'item2']
        self.editor.tree.set.side_effect = lambda child, col: '★' if col == 'Favorite' and child == 'item1' else ''
        
        with patch.object(self.editor.tree, 'move') as mock_move:
            self.editor.sort_treeview('Favorite')
            self.assertEqual(mock_move.call_count, 2)
            self.assertEqual(self.editor.sort_column, 'Favorite')
            self.assertFalse(self.editor.sort_direction)

class TestStationManagement(TestRadioStationEditorBase):
    def setUp(self):
        super().setUp()
        self.editor.stations = [
            {
                'url': 'http://test1.com',
                'name': 'Station 1',
                'genre': 'Pop',
                'country': 'US',
                'bitrate': '128',
                'favorite': True
            }
        ]
        self.editor.tree = MagicMock()
        self.editor.tree.selection.return_value = ['item1']
        self.editor.tree.index.return_value = 0

        # Adicione esta configuração de mensagens
        self.editor.config = {
            'messages': {
                'confirm_title': 'Confirm',
                'confirm_remove': 'Confirm remove',
                'warning_title': 'Warning',
                'select_station': 'Please select a station first'
            }
        }

    def test_add_station(self):
        with patch.object(self.editor, 'edit_station') as mock_edit:
            self.editor.add_station()
            mock_edit.assert_called_once_with(None)

    def test_edit_selected_station(self):
        with patch.object(self.editor, 'edit_station') as mock_edit:
            self.editor.edit_selected_station()
            mock_edit.assert_called_once_with(0)

    def test_edit_selected_station_no_selection(self):
        # Configura o tree para retornar seleção vazia
        self.editor.tree.selection.return_value = []

        # Mock do messagebox e da função edit_station
        with patch('main.messagebox') as mock_msg, \
            patch.object(self.editor, 'edit_station') as mock_edit:

            # Chama o método a ser testado
            self.editor.edit_selected_station()

            # Verifica se a mensagem foi mostrada
            mock_msg.showwarning.assert_called_once_with(
                'Warning',
                'Please select a station first'
            )

            # Verifica que edit_station não foi chamada
            mock_edit.assert_not_called()

    def test_remove_station(self):
        # Configura uma estação de exemplo
        self.editor.stations = [{
            'url': 'http://example.com',
            'name': 'Test Station',
            'genre': 'Pop',
            'country': 'US',
            'bitrate': '128',
            'favorite': False
        }]

        # Configura a seleção da treeview
        self.editor.tree.selection.return_value = ['item1']
        self.editor.tree.index.return_value = 0

        # Mock do messagebox e update_treeview
        with patch('main.messagebox') as mock_msg, \
             patch.object(self.editor, 'update_treeview') as mock_update:

            # Caso usuário confirme
            mock_msg.askyesno.return_value = True
            self.editor.remove_station()

            # Verificações
            mock_msg.askyesno.assert_called_once_with(
                'Confirm',
                'Confirm remove'
            )
            self.assertEqual(len(self.editor.stations), 0)
            mock_update.assert_called_once()

            # Caso usuário cancele
            self.editor.stations = [{'url': 'http://example.com'}]
            mock_msg.askyesno.return_value = False
            self.editor.remove_station()
            self.assertEqual(len(self.editor.stations), 1)

    def test_remove_station_no_selection(self):
        # Configura seleção vazia
        self.editor.tree.selection.return_value = []

        with patch('main.messagebox') as mock_msg:
            self.editor.remove_station()
            mock_msg.showwarning.assert_called_once_with(
                self.editor.config['messages']['warning_title'],
                self.editor.config['messages']['select_station']
        )

    def test_remove_station_cancel(self):
        # Configura uma estação de exemplo
        self.editor.stations = [{
            'url': 'http://example.com',
            'name': 'Test Station', 
            'genre': 'Pop',
            'country': 'US',
            'bitrate': '128',
            'favorite': False
        }]

        # Configura a seleção da treeview
        self.editor.tree.selection.return_value = ['item1']
        self.editor.tree.index.return_value = 0

        # Mock do messagebox para simular o cancelamento
        with patch('main.messagebox') as mock_msg:
            mock_msg.askyesno.return_value = False  # Usuário clicou "Não"

            self.editor.remove_station()

            # Verifica se a estação NÃO foi removida
            self.assertEqual(len(self.editor.stations), 1)

            # Verifica se askyesno foi chamado corretamente
            mock_msg.askyesno.assert_called_once_with(
                self.editor.config['messages']['confirm_title'],
                self.editor.config['messages']['confirm_remove']
            )


if __name__ == '__main__':
    unittest.main()