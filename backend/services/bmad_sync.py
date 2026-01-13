import json
import logging
import requests
import zipfile
import io
import shutil
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path
import re
from backend.config import Config

logger = logging.getLogger(__name__)


class BMADSyncService:
    """Handles checking for and downloading BMAD documentation updates."""

    def __init__(self, project_root: str, config: Dict[str, Any] = None):
        """
        Initialize BMAD sync service.

        Args:
            project_root: Root directory of the project
            config: Configuration dict with:
                - docs_url: Documentation URL (default: Config.BMAD_DOCS_URL)
                - repo_url: ZIP repo URL (default: Config.BMAD_REPO_URL)
                - check_interval_hours: Hours between checks (default: 24)
        """
        self.project_root = Path(project_root)
        self.config = config or {}
        self.docs_url = self.config.get('docs_url', Config.BMAD_DOCS_URL)
        self.repo_url = self.config.get('repo_url', Config.BMAD_REPO_URL)
        self.check_interval = timedelta(hours=self.config.get('check_interval_hours', 24))
        self.state_file = self.project_root / '.bmad_sync_state.json'
        self.target_dir = self.project_root / '_bmad'
        self._load_state()

    def _load_state(self) -> None:
        """Load sync state from file."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    self.state = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load BMAD sync state: {e}")
                self.state = {}
        else:
            self.state = {}

    def _save_state(self) -> None:
        """Save sync state to file."""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save BMAD sync state: {e}")

    def should_check_for_updates(self) -> bool:
        """
        Check if it's time to look for updates.
        """
        last_check = self.state.get('last_check')
        if not last_check:
            return True

        try:
            last_check_time = datetime.fromisoformat(last_check)
            return datetime.now() - last_check_time > self.check_interval
        except (ValueError, TypeError):
            return True

    def get_latest_docs_info(self) -> Optional[Dict[str, Any]]:
        """
        Fetch latest information from BMAD documentation site.
        """
        try:
            headers = {}
            if 'etag' in self.state:
                headers['If-None-Match'] = self.state['etag']

            response = requests.get(self.docs_url, headers=headers, timeout=10)

            if response.status_code == 304:
                return self.state.get('last_docs_info')

            response.raise_for_status()

            if 'ETag' in response.headers:
                self.state['etag'] = response.headers['ETag']

            version = 'latest'
            try:
                version_match = re.search(r'version[:\s]+([0-9.]+|latest)', response.text, re.IGNORECASE)
                if version_match:
                    version = version_match.group(1)
                else:
                    version_match = re.search(r'v([0-9]+\.[0-9]+(?:\.[0-9]+)?)', response.text)
                    if version_match:
                        version = version_match.group(1)
            except Exception:
                pass

            docs_info = {
                'version': version,
                'last_modified': response.headers.get('Last-Modified', datetime.now().isoformat()),
                'url': self.docs_url
            }

            self.state['last_docs_info'] = docs_info
            return docs_info

        except Exception as e:
            logger.error(f"Failed to fetch documentation info: {e}")
            return None

    def check_for_updates(self) -> Dict[str, Any]:
        """Check for updates and return status."""
        docs_info = self.get_latest_docs_info()
        if not docs_info:
            return {
                'has_updates': False,
                'error': 'Connection failed',
                'last_check': self.state.get('last_check')
            }

        self.state['last_check'] = datetime.now().isoformat()
        self._save_state()

        current_version = self.state.get('current_version', 'unknown')
        latest_version = docs_info['version']
        has_updates = current_version != latest_version

        return {
            'has_updates': has_updates,
            'current_version': current_version,
            'latest_version': latest_version,
            'last_check': self.state['last_check'],
            'docs_url': self.docs_url
        }

    def sync_docs(self) -> Dict[str, Any]:
        """
        Perform the actual ZIP download and extraction to _bmad/ folder.
        """
        try:
            logger.info(f"Downloading BMAD documentation from {self.repo_url}...")
            response = requests.get(self.repo_url, timeout=30)
            response.raise_for_status()

            # Unzip in memory
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                # Find the root directory in the zip (GitHub adds a prefix like 'repo-main/')
                root_prefix = z.namelist()[0].split('/')[0]
                
                # Create temp extraction path
                temp_extract = self.project_root / '.bmad_temp_extract'
                if temp_extract.exists():
                    shutil.rmtree(temp_extract)
                temp_extract.mkdir(parents=True, exist_ok=True)
                
                z.extractall(temp_extract)
                
                # Identify source (usually the folder inside the zip)
                source_path = temp_extract / root_prefix
                
                # Ensure target exists
                self.target_dir.mkdir(parents=True, exist_ok=True)
                
                # Merge/Overwrite target with source
                # Note: Simple sync - move contents of source to target
                for item in source_path.iterdir():
                    dest_item = self.target_dir / item.name
                    if dest_item.exists():
                        if dest_item.is_dir():
                            shutil.rmtree(dest_item)
                        else:
                            dest_item.unlink()
                    
                    if item.is_dir():
                        shutil.copytree(item, dest_item)
                    else:
                        shutil.copy2(item, dest_item)
                
                # Cleanup temp
                shutil.rmtree(temp_extract)

            # Update state
            docs_info = self.get_latest_docs_info()
            version = docs_info['version'] if docs_info else 'latest'
            
            self.state['current_version'] = version
            self.state['last_updated'] = datetime.now().isoformat()
            self._save_state()

            logger.info(f"Successfully synced BMAD documentation (Version: {version})")
            return {
                'success': True,
                'version': version,
                'message': 'Documentation successfully updated and merged.'
            }

        except Exception as e:
            logger.error(f"Sync failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def mark_docs_seen(self, version: str) -> Dict[str, Any]:
        """Mark as seen without necessarily syncing (fallback/legacy)."""
        self.state['current_version'] = version
        self.state['last_seen'] = datetime.now().isoformat()
        self._save_state()
        return {'success': True, 'version': version}

    def get_status(self) -> Dict[str, Any]:
        """Get current sync status."""
        return {
            'current_version': self.state.get('current_version', 'unknown'),
            'last_check': self.state.get('last_check'),
            'last_updated': self.state.get('last_updated'),
            'last_seen': self.state.get('last_seen'),
            'docs_url': self.docs_url
        }
