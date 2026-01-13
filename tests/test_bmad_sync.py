import unittest
import os
import shutil
import tempfile
import json
import zipfile
from unittest.mock import patch, MagicMock
from pathlib import Path
from backend.services.bmad_sync import BMADSyncService

class TestBMADSyncService(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.project_root = self.test_dir
        self.sync_service = BMADSyncService(self.project_root)
        
    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @patch('requests.get')
    def test_check_for_updates(self, mock_get):
        # Mock documentation site
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '<html><body>BMAD Version: 5.20.0</body></html>'
        mock_get.return_value = mock_response
        
        update_info = self.sync_service.check_for_updates()
        self.assertTrue(update_info['has_updates'])
        self.assertEqual(update_info['latest_version'], '5.20.0')

    @patch('requests.get')
    def test_sync_docs_success(self, mock_get):
        # Create a mock zip file in memory
        zip_path = os.path.join(self.test_dir, 'mock.zip')
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr('bmad-method-main/core/manifest.md', 'core manifest content')
            zf.writestr('bmad-method-main/bmm/workflow.md', 'workflow content')
        
        with open(zip_path, 'rb') as f:
            zip_content = f.read()
            
        # Mock ZIP download
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = zip_content
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        result = self.sync_service.sync_docs()
        
        self.assertTrue(result['success'])
        
        # Verify files extracted to _bmad/
        bmad_dir = Path(self.project_root) / '_bmad'
        self.assertTrue((bmad_dir / 'core' / 'manifest.md').exists())
        self.assertTrue((bmad_dir / 'bmm' / 'workflow.md').exists())
        
        with open(bmad_dir / 'core' / 'manifest.md', 'r') as f:
            self.assertEqual(f.read(), 'core manifest content')

    def test_get_status_initial(self):
        status = self.sync_service.get_status()
        self.assertEqual(status['current_version'], 'unknown')
        self.assertIsNone(status['last_updated'])

if __name__ == '__main__':
    unittest.main()
