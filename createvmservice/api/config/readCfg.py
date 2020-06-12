from configparser import ConfigParser
import os

def read_config(cfg_files):
    if(cfg_files != None):
        config = ConfigParser()

        # merges all files into a single config
        for i, cfg_file in enumerate(cfg_files):
            if(os.path.exists(cfg_file)):
                config.read(cfg_file)

        return config