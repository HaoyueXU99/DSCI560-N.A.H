"""
config.py

Initializes the configuration for the expedition bot.
This function loads the environment variables from a .env file using the dotenv library.
It can be called at the beginning of the program to ensure that the necessary configuration is set up.
"""

from dotenv import load_dotenv

def initialize_config():

    load_dotenv()
    # Any other configuration initialization
