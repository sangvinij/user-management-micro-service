import logging

logger = logging.getLogger("logger")
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler("info.log")
fh.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
fh.setFormatter(formatter)

logger.addHandler(fh)
