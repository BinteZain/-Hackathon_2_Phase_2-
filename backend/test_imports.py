import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    print("Testing individual imports...")
    
    from sqlmodel import SQLModel, Field
    print("[OK] SQLModel imported successfully")
    
    from datetime import datetime
    print("[OK] datetime imported successfully")
    
    from typing import TYPE_CHECKING, Optional
    print("[OK] typing imports successful")
    
    import uuid
    print("[OK] uuid imported successfully")
    
    print("\nTesting model imports...")
    from src.models.user import User
    print("[OK] User model imported successfully")
    
    from src.models.task import Task
    print("[OK] Task model imported successfully")
    
    print("\nAll imports successful!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()