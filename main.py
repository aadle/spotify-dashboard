import logging
import logging.config
import pathlib
import json


def setup_logging():
    config_file = pathlib.Path("logging_config/config.json")
    with open(config_file) as f_in:
        config = json.load(f_in)
    logging.config.dictConfig(config)

def main():
    setup_logging()
    print("Hello from spotify-dashboard!")
    logging.debug("poop")
    logging.info("poop")
    logging.warning("poop")
    logging.critical("poop")


if __name__ == "__main__":
    main()
