# cloud.py
# -*- coding: utf-8 -*-
"""
Application entry point (main).
This file initializes and displays the login screen before entering the main window.
"""
import sys
import nest_asyncio
nest_asyncio.apply()
from PySide6.QtWidgets import QApplication, QMessageBox, QDialog
from pathlib import Path
from dotenv import load_dotenv
import os
# Import necessary windows
from ui.main_window_3d_enhanced import Enhanced3DConveyorWindow
from ui.login_dialog import LoginDialog
from core.licensing import is_activated
from ui.activation_dialog import ActivationDialog
from core.specs import VERSION
import logging
from core.utils.paths import get_log_path
import os.path
import traceback

# Import visualization 3D module
try:
    from ui.visualization_3d.enhanced_widget import EnhancedVisualization3DWidget
    from ui.visualization_3d.core.animation_engine import ConveyorAnimationEngine
    from ui.visualization_3d.core.component_builder import ComponentBuilderManager
    from ui.visualization_3d.core.physics_simulator import ConveyorPhysicsSimulator
    from ui.visualization_3d.core.model_generator import ConveyorModelGenerator
    print("✅ Module visualization 3D đã được import thành công")
    HAS_3D_VISUALIZATION = True
except ImportError as e:
    print(f"⚠️ Không thể import module visualization 3D: {e}")
    print("Module visualization 3D sẽ hoạt động ở chế độ giới hạn")
    HAS_3D_VISUALIZATION = False

def load_env_config(root_dir: Path):
    """Load environment configuration from .env or env_config.txt"""
    print(f"Loading config from root_dir: {root_dir}")
    
    # Determine the actual root directory (where env_config.txt is located)
    actual_root_dir = root_dir
    while actual_root_dir.parent != actual_root_dir:  # Find the root directory
        if (actual_root_dir / 'env_config.txt').exists():
            break
        actual_root_dir = actual_root_dir.parent
    
    print(f"Actual root directory: {actual_root_dir}")
    
    # Try multiple possible locations for .env file - prioritize the root directory
    possible_env_paths = [
        actual_root_dir / '.env',  # Root directory (highest priority)
        root_dir / '.env',  # Current directory
        root_dir / '..' / '.env',  # Parent directory
        root_dir / '_internal' / '.env',  # _internal subdirectory (lowest priority)
    ]
    
    # Declare possible_config_paths here to avoid scope errors
    possible_config_paths = [
        actual_root_dir / 'env_config.txt',  # Root directory (highest priority)
        root_dir / 'env_config.txt',  # Current directory
        root_dir / '..' / 'env_config.txt',  # Parent directory
        root_dir / '_internal' / 'env_config.txt',  # _internal subdirectory (lowest priority)
    ]
    
    env_loaded = False
    for env_path in possible_env_paths:
        if env_path.exists():
            print(f"Loading .env from: {env_path}")
            load_dotenv(dotenv_path=env_path)
            env_loaded = True
            break
    
    # If no .env file found, try to load from env_config.txt - prioritize the root directory
    if not env_loaded:
        for config_path in possible_config_paths:
            if config_path.exists():
                print(f"Loading config from: {config_path}")
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#') and '=' in line:
                                key, value = line.split('=', 1)
                                os.environ[key.strip()] = value.strip()
                                print(f"Set environment variable: {key.strip()}")
                    env_loaded = True
                    break
                except Exception as e:
                    print(f"Error reading config file: {e}")
    
    if not env_loaded:
        print("Warning: No .env or env_config.txt file found in any expected location")
        print("Available paths checked:")
        for env_path in possible_env_paths:
            print(f"  - {env_path}: {{'exists' if env_path.exists() else 'not found'}}")
        for config_path in possible_config_paths:
            print(f"  - {config_path}: {{'exists' if config_path.exists() else 'not found'}}")
    
    # Verify AI_API_KEY is set
    api_key = os.getenv('AI_API_KEY')
    if api_key:
        print(f"AI_API_KEY found: {api_key[:10]}...")
    else:
        print("AI_API_KEY not found - this will cause errors!")
        # Try to find and load from the config file again
        print("Attempting to find and load config files again...")
        for config_path in possible_config_paths:
            if config_path.exists():
                try:
                    print(f"Trying to load from: {config_path}")
                    with open(config_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#') and '=' in line:
                                key, value = line.split('=', 1)
                                os.environ[key.strip()] = value.strip()
                                print(f"Set environment variable: {key.strip()}")
                    
                    # Check again
                    api_key = os.getenv('AI_API_KEY')
                    if api_key:
                        print(f"AI_API_KEY found after retry: {api_key[:10]}...")
                        break
                except Exception as e:
                    print(f"Error reading config file during retry: {e}")
        
        if not api_key:
            print("AI_API_KEY still not found after retry!")

def main():
    try:
        # Determine the root directory correctly
        if getattr(sys, 'frozen', False):
            # Running from exe (PyInstaller)
            root_dir = Path(sys.executable).parent
            print(f"Running from exe, root_dir: {root_dir}")
        else:
            # Running from Python script
            root_dir = Path(__file__).parent.absolute()
            print(f"Running from script, root_dir: {root_dir}")
        
        # Find the actual root directory (where env_config.txt is located)
        actual_root_dir = root_dir
        while actual_root_dir.parent != actual_root_dir:  # Find the root directory
            if (actual_root_dir / 'env_config.txt').exists():
                break
            actual_root_dir = actual_root_dir.parent
        
        print(f"Actual root directory: {actual_root_dir}")
        
        # Load environment variables from .env file or env_config.txt
        load_env_config(actual_root_dir)
        
        # Set default INDEX_DIR if not provided - Try multiple possible locations
        if not os.getenv('INDEX_DIR'):
            possible_index_paths = [
                actual_root_dir / 'data' / 'index',  # Root directory (highest priority)
                root_dir / 'data' / 'index',  # Current directory
                root_dir / '_internal' / 'data' / 'index',  # _internal subdirectory
                root_dir / '..' / 'data' / 'index',  # Parent directory
            ]
            
            index_dir = None
            for idx_path in possible_index_paths:
                if idx_path.exists():
                    index_dir = idx_path
                    break
            
            if index_dir is None:
                # Create default index directory
                index_dir = actual_root_dir / 'data' / 'index'
                print(f"Creating default index directory: {index_dir}")
                index_dir.mkdir(parents=True, exist_ok=True)
            
            os.environ['INDEX_DIR'] = str(index_dir)
            print(f"Using INDEX_DIR: {os.environ['INDEX_DIR']}")
            
            # Check if chunks.faiss file exists
            faiss_file = index_dir / 'chunks.faiss'
            if not faiss_file.exists():
                print(f"Warning: chunks.faiss file not found in: {index_dir}")
                print("You may need to rebuild the index using: python scripts/rebuild_index.py")
            else:
                print(f"Found chunks.faiss at: {faiss_file}")
        
        print("Initializing QApplication...")
        app = QApplication(sys.argv)
        app.setApplicationName("Conveyor Calculator Professional")
        app.setApplicationVersion(VERSION)
        app.setOrganizationName("haingocson@gmail.com")
        print("QApplication initialized successfully")

        # --- [START CHANGES] ---
        # Step 1: Check for offline activation
        print("Checking activation status...")
        try:
            ok, _state = is_activated()
            print(f"Activation status: {ok}")
            if not ok:
                print("Showing activation dialog...")
                act_dialog = ActivationDialog()
                if act_dialog.exec() != QDialog.Accepted:
                    print("Activation cancelled by user")
                    return 0
        except Exception as e:
            print(f"Error checking activation: {e}")
            traceback.print_exc()
            # Continue running if there is an activation error

        # Step 2: Show the login screen before the main app
        print("Showing login dialog...")
        try:
            login_dialog = LoginDialog()
            result = login_dialog.exec()
            if result == QDialog.Accepted:
                print("Login successful, setting up logging...")
                # Setup logging in user's AppData directory
                try:
                    log_file = os.path.join(get_log_path(), 'conveyor_calculator.log')
                    logging.basicConfig(
                        level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s",
                        handlers=[
                            logging.FileHandler(log_file, encoding="utf-8", mode="a"),
                            logging.StreamHandler()  # Also log to console
                        ]
                    )
                    print(f"Logging setup complete: {log_file}")
                except Exception as e:
                    print(f"Warning: Could not setup file logging: {e}")
                    # Fallback to console logging only
                    logging.basicConfig(
                        level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s",
                        handlers=[logging.StreamHandler()]
                    )

                try:
                    print("Creating main window...")
                    # Create and show the main application window
                    main_window = Enhanced3DConveyorWindow()
                    main_window.show()
                    print("Main window displayed successfully")
                    return app.exec()
                except Exception as e:
                    error_msg = f"Cannot start main application:\n{e}"
                    print(f"Error: {error_msg}")
                    print("Traceback:")
                    traceback.print_exc()
                    QMessageBox.critical(None, "Startup Error", error_msg)
                    logging.error(f"Error starting main window: {e}", exc_info=True)
                    return 1
            else:
                # If the user closes the login window or login fails, exit.
                print("Login cancelled or failed by user")
                return 0
        except Exception as e:
            error_msg = f"Error displaying login screen:\n{e}"
            print(f"Error: {error_msg}")
            print("Traceback:")
            traceback.print_exc()
            QMessageBox.critical(None, "Login Error", error_msg)
            return 1
        # --- [END CHANGES] ---
        
    except Exception as e:
        error_msg = f"Application initialization error:\n{e}"
        print(f"Critical error: {error_msg}")
        print("Traceback:")
        traceback.print_exc()
        
        # Try to show a message box if possible
        try:
            app = QApplication(sys.argv)
            QMessageBox.critical(None, "Critical Error", error_msg)
        except:
            pass
        
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Unhandled exception in main: {e}")
        traceback.print_exc()
        sys.exit(1)