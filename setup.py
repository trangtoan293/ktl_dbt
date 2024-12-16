from setuptools import setup
from setuptools.command.install import install
import os
import shutil
import subprocess
import logging


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):    
        install.run(self)
        
        source_dir = os.path.join(self.install_lib, 'ktl_dbt', 'dbt')
        target_dir = os.path.join(self.install_lib, 'dbt')
        shutil.copytree(source_dir, target_dir, dirs_exist_ok=True)
        shutil.rmtree(source_dir)

        target_dir = os.path.join(self.install_lib, 'ktl_dbt')
        try:
            print("Installing mermaid-cli...")
            
            # Checking Node version
            min_version = (14, 0, 0)
            result = subprocess.run(['node', '--version'], capture_output=True, text=True, check=True)
            version_str = result.stdout.strip().lstrip('v')
            major, minor, patch = map(int, version_str.split('.'))
            if (major, minor, patch) < min_version:
                raise Exception(f"Node.js version {major}.{minor}.{patch} is installed, but version {min_version[0]}.{min_version[1]}.{min_version[2]} or higher is required.")
        
            subprocess.check_call(
                args=['npm', 'install', '-gf', '@mermaid-js/mermaid-cli'],
                cwd=target_dir,
                stderr=subprocess.STDOUT,
                text=True
            )
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to install mermaid-cli, you will not be able to render ERD's on DBT docs. Please ensure you have installed Node.js v14+\n" + e.output)

setup(
    cmdclass={
        'install': PostInstallCommand,
    }
)