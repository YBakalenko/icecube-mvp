"""
Программа: Подключение к БД, чтение и запись данных
Версия: 1.3
"""
import os
import gridfs
import json
import joblib
import io
from typing import Text
from pymongo import MongoClient, errors
import pymongo.database

from .get_data import read_config


def db_connection() -> pymongo.database.Database:
    """
    Подключение к базе данных MongoDb
    :return: экземпляр базы данных IceCube
    """
    config = read_config()
    host_aliases = config['host_aliases']
    db_config = config['database']

    db_host = os.getenv(host_aliases['database']['host']['alias'], host_aliases['database']['host']['default'])
    db_port = os.getenv(host_aliases['database']['port']['alias'], host_aliases['database']['port']['default'])
    db_user = db_config['username']
    db_password = db_config['password']

    db_url = f'mongodb://{db_user}:{db_password}@{db_host}:{db_port}/'

    client = MongoClient(db_url, serverSelectionTimeoutMS=1000)
    db_name = db_config['name']
    db = client[db_name]

    return db


def check_db_connection():
    db = db_connection()
    client = db.client

    try:
        # The ping command is cheap and does not require auth.
        client.admin.command('ping')
        return True
    except errors.ConnectionFailure:
        return False


def query_json(collection_name: Text, object_name: Text):
    """
    Чтение данных формата JSON из БД Mongo
    :param collection_name: имя коллекции в БД
    :param object_name: наименование объекта
    :return: запрашиваемые данные в формате dict
    """
    db = db_connection()
    filter_criteria = {'type': object_name}
    collection = db[collection_name]
    result = collection.find_one(filter_criteria)

    if result:
        return json.loads(result['contents'])
    else:
        return None


def query_joblib(filename: Text):
    """
    Чтение данных формата JSON из БД Mongo
    :param filename: имя запрашиваемого
    :return: объект joblib с обученной моделью
    """
    db = db_connection()
    fs = gridfs.GridFS(db)
    file_data = fs.find_one({'filename': filename})

    if file_data:
        file_buffer = io.BytesIO(file_data.read())
        loaded_object = joblib.load(file_buffer)
        return loaded_object
    else:
        return None
