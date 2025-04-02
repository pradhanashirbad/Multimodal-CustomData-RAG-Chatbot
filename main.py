import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Load environment variables
load_dotenv()

def check_environment():
    """Check if all required environment variables and directories exist"""
    required_env = ['OPENAI_API_KEY']
    missing_env = [env for env in required_env if not os.getenv(env)]
    if missing_env:
        print(f"Error: Missing environment variables: {', '.join(missing_env)}")
        print("Please check your .env file")
        return False

    required_dirs = [
        'data/raw',
        'data/images/images_electronics',
        'data/images/user_uploads',
        'database_chroma/text',
        'database_chroma/images'
    ]
    missing_dirs = [dir for dir in required_dirs if not os.path.exists(dir)]
    if missing_dirs:
        print(f"Creating missing directories: {', '.join(missing_dirs)}")
        for dir in missing_dirs:
            os.makedirs(dir, exist_ok=True)

    return True

def main():
    """Main entry point for the application"""
    print("Checking environment...")
    if not check_environment():
        return

    print("Starting Electronics Product Assistant...")
    from ui.app import main as start_app
    start_app()


if __name__ == "__main__":
    main() 