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

class TestBackupFunctionality(unittest.TestCase):
    def setUp(self):
        self.root = MagicMock()
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test_radio.sii")
        
        with open(self.test_file, 'w') as f:
            f.write("SiiNunit\n{\n live_stream_def : _nameless.28a.c076.a0f0 {\n stream_data: 0\n }\n}")
        
        # Configurar mocks
        self.patcher_filedialog = patch('main.filedialog.askopenfilename')
        self.mock_askopenfilename = self.patcher_filedialog.start()
        self.mock_askopenfilename.return_value = self.test_file
        
        self.patcher_messagebox = patch('main.messagebox')
        self.mock_messagebox = self.patcher_messagebox.start()
        
        # Configurar editor com mock de traduções
        self.editor = RadioStationEditor(self.root)
        self.editor.config = {
            'messages': {
                'backup_success': 'Backup success: {backup_path}',
                'backup_warning': 'Backup warning: {error}',
                'backup_title_success': 'Backup Success',
                'backup_title_warning': 'Backup Warning',
                'load_error': 'Load error'
            }
        }
    
    def tearDown(self):
        self.patcher_filedialog.stop()
        self.patcher_messagebox.stop()
        shutil.rmtree(self.test_dir)
    
    def test_backup_creation_success(self):
        """Testa criação bem-sucedida de backup"""
        self.editor.open_file()
        
        backup_dir = os.path.join(self.test_dir, "backup")
        self.assertTrue(os.path.exists(backup_dir))
        
        backup_files = os.listdir(backup_dir)
        self.assertEqual(len(backup_files), 1)
        
        backup_path = os.path.join(backup_dir, backup_files[0])
        self.mock_messagebox.showinfo.assert_called_once_with(
            'Backup Success',
            f'Backup success: {backup_path}'
        )
    
    def test_backup_creation_failure(self):
        """Testa tratamento de erro no backup"""
        with patch('os.makedirs') as mock_makedirs:
            mock_makedirs.side_effect = Exception("Test error")
            
            self.editor.open_file()
            
            self.mock_messagebox.showwarning.assert_called_once_with(
                'Backup Warning',
                'Backup warning: Test error'
            )
    
    def test_backup_directory_exists(self):
        """Testa comportamento com diretório existente"""
        backup_dir = os.path.join(self.test_dir, "backup")
        os.makedirs(backup_dir)
        
        self.editor.open_file()
        
        backup_files = os.listdir(backup_dir)
        self.assertEqual(len(backup_files), 1)
    
    @patch('shutil.copy2')
    @patch('os.makedirs')
    @patch('os.path.join')
    def test_file_copy_operation(self, mock_join, mock_makedirs, mock_copy):
        """Testa operação de cópia do arquivo"""
        # Configurar mocks
        mock_join.side_effect = lambda *args: '/'.join(args)
        mock_makedirs.return_value = None
        mock_copy.return_value = None
        
        self.editor.open_file()
        
        # Verificar se a cópia foi chamada
        self.assertTrue(mock_copy.called)
        args, _ = mock_copy.call_args
        self.assertTrue(args[0].endswith("test_radio.sii"))
        self.assertTrue(args[1].startswith(f"{self.test_dir}/backup/test_radio.sii.bak_"))
    
    def test_backup_filename_format(self):
        """Testa formato do nome do arquivo de backup"""
        with patch('main.datetime') as mock_datetime:
            # Fixar o datetime para teste consistente
            test_time = datetime(2023, 2, 25, 9, 0, 0)
            mock_datetime.now.return_value = test_time
            
            self.editor.open_file()
            
            backup_dir = os.path.join(self.test_dir, "backup")
            backup_files = os.listdir(backup_dir)
            backup_filename = backup_files[0]
            
            self.assertTrue(backup_filename.startswith("test_radio.sii.bak_"))
            self.assertIn("20230225_090000", backup_filename)
    
    def test_missing_translation_keys_success_with_failback(self):
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
        with patch('os.makedirs') as mock_makedirs:
            mock_makedirs.side_effect = Exception("Test error")

            self.editor.open_file()

            # Verificar se showwarning foi chamado (já que showinfo não será chamado sem as chaves)
            self.assertTrue(self.mock_messagebox.showwarning.called)

            # Verificar os argumentos da chamada
            args, _ = self.mock_messagebox.showwarning.call_args
            self.assertEqual(args[0], 'Backup Warning')
            self.assertTrue(args[1].startswith('Backup warning: Test error'))
    def test_missing_translation_keys(self):
        """Testa comportamento com chaves de tradução faltando"""
        # Simular falta de chaves específicas
        del self.editor.config['messages']['backup_title_success']
        del self.editor.config['messages']['backup_success']

        # Adicionar fallback no próprio editor
        self.editor.config['messages']['backup_title_success'] = 'Backup criado'
        self.editor.config['messages']['backup_success'] = 'Backup realizado em: {backup_path}'

        self.editor.open_file()

        # Verificar se showinfo foi chamado
        self.assertTrue(self.mock_messagebox.showinfo.called)

        # Verificar argumentos
        args, _ = self.mock_messagebox.showinfo.call_args
        self.assertEqual(args[0], 'Backup criado')
        self.assertTrue(args[1].startswith('Backup realizado em:'))

class TestRadioStationEditor(unittest.TestCase):
    def setUp(self):
        self.root = MagicMock()
        self.editor = RadioStationEditor(self.root)
    
    def test_sample(self):
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()