import configparser
import os

def load_config(config_path='config.ini'):
    config = configparser.ConfigParser()
    if os.path.exists(config_path):
        config.read(config_path)
    else:
        print(f"[WARNING] Configuration file '{config_path}' not found. Using default values.")
    return config
