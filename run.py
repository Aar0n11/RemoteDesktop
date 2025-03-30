import uvicorn
import json

CONFIG_FILE = "config.json"

def load_config():
    try:
        with open(CONFIG_FILE, "r") as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        print(f"Error: {CONFIG_FILE} not found. Make sure it's in the same directory as run.py.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error: {CONFIG_FILE} is not a valid JSON file. Please check its format.")
        exit(1)

if __name__ == "__main__":
    config = load_config()
    
    print(f"Starting Quick Remote Desktop on port {config['port']}...")

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=config["port"],
        reload=config.get("debug", False),
        log_level="info"
    )
