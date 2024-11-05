
import logging
from datetime import datetime

from elasticsearch import Elasticsearch

from user_management.config import config

elasticsearch_client = Elasticsearch(f"{config.ELASTICSEARCH_HOST}:{config.ELASTICSEARCH_PORT}")
if not elasticsearch_client.ping():
    raise ValueError("Elasticsearch connection failed")


class ElasticsearchHandler(logging.Handler):
    def __init__(self, es_client, index_name):
        super().__init__()
        self.es_client = es_client
        self.index_name = index_name

    def emit(self, record):
        timestamp = datetime.now().isoformat()

        doc = {
            "@timestamp": timestamp,
            "log.level": record.levelname,
            "message": record.msg,
            "name": record.name,
        }
        self.es_client.index(index=self.index_name, body=doc)


logger = logging.getLogger("logger")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

fh = logging.FileHandler("info.log")
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

es_handler = ElasticsearchHandler(elasticsearch_client, index_name="fastapi-logs")
es_handler.setLevel(logging.DEBUG)
es_handler.setFormatter(formatter)

logger.addHandler(es_handler)
logger.addHandler(fh)
