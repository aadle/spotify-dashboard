import json
import logging
import logging.config
import pathlib
from datetime import datetime

def get_current_filename():
    import inspect
    caller_file = inspect.stack()[1].filename
    return pathlib.Path(caller_file).stem

def setup_logging(current_filename:str):
    """
    current_file_path: use os.path.basename(__file__).split(".")[0] to get
    the filename of the file you want to log (without file extension).
    """
    config_file = pathlib.Path("../logging_config/config.json")

    current_date = datetime.today().strftime("%Y-%m-%d")
    with open(config_file) as f_in:
        config = json.load(f_in)
        config["handlers"]["file"]["filename"] = f"logs/{current_filename}_{current_date}.log"
        # config["handlers"]["file"]["filename"] = f"logs/{os.path.basename(__file__)}_{current_date}.log"

    logging.config.dictConfig(config)

