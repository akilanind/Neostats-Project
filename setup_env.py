import subprocess
import sys
import os

def check_and_install():
    """Checks for required packages and installs them if missing."""
    required_packages = [
        "python-dotenv",
        "streamlit",
        "groq",
        "sentence-transformers",
        "chromadb",
        "pypdf",
        "duckduckgo-search",
        "torch"
    ]
    
    print("--- CitizenHelp Dependency Checker ---")
    
    for pkg in required_packages:
        try:
            # Handle cases where package name != import name
            import_name = pkg.replace("-", "_")
            if pkg == "python-dotenv":
                import_name = "dotenv"
            
            __import__(import_name)
            print(f"[OK] {pkg} is already installed.")
        except ImportError:
            print(f"[..] {pkg} not found. Installing...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
                print(f"[DONE] {pkg} installed successfully.")
            except Exception as e:
                print(f"[ERROR] Failed to install {pkg}: {e}")

    print("\n--- Environment Path Information ---")
    print(f"Python Executable: {sys.executable}")
    print(f"Python sys.path:")
    for path in sys.path:
        print(f"  - {path}")

    # Create dummy .env if it doesn't exist
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write("GROQ_API_KEY=your_key_here\n")
        print("\n[NOTE] Created a template .env file. Please add your GROQ_API_KEY.")

if __name__ == "__main__":
    check_and_install()
