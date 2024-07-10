"""
Программа: Выполнение запросов к backend и обработка ответов
Версия: 0.3.1
"""
import os
import requests
import joblib
import io
import streamlit as st
import pandas as pd
from http.client import responses
from typing import Text, Any
from .get_data import read_config, dtypes_convert


def get_endpoint(url_suffix: str) -> str:
    """
    Загрузка конфигурационного файла проекта
    :param url_suffix: суффикс целевой страницы
    :return: строка с URL-адресом для запроса
    """
    config = read_config()
    host_aliases = config['host_aliases']

    train_host = os.getenv(host_aliases['train']['host']['alias'], host_aliases['train']['host']['default'])
    train_port = os.getenv(host_aliases['train']['port']['alias'], host_aliases['train']['port']['default'])
    predict_host = os.getenv(host_aliases['predict']['host']['alias'], host_aliases['predict']['host']['default'])
    predict_port = os.getenv(host_aliases['predict']['port']['alias'], host_aliases['predict']['port']['default'])

    if url_suffix in config['endpoints']['train']:
        return f'http://{train_host}:{train_port}/{url_suffix}'
    else:
        return f'http://{predict_host}:{predict_port}/{url_suffix}'


def http_request(kind: str,
                 service: str,
                 exit_on_error: bool = True,
                 timeout: int = 3000,
                 param_name: str = None,
                 json: Any = None,
                 files: dict = None) -> requests.Response:
    """
    Выполнение HTTP-запроса и обработка ошибок
    :param kind: тип запроса ['get', 'post']
    :param service: суффикс в адресе запрашиваемого сервиса (endpoint)
    :param exit_on_error: прерывание программы при возникновении ошибки на стороне backend
    :param timeout: время ожидания ответа
    :param param_name: имя опционального параметра name в запросе
    :param json: опциональный json-параметр запроса
    :param files: словарь из файлов, передаваемых в запросе
    """
    if kind == 'get':
        request = requests.get
    else:
        request = requests.post
    endpoint = get_endpoint(service)
    try:
        if param_name is not None:
            response = request(endpoint, params={'name': param_name}, timeout=timeout)
        elif json is not None:
            response = request(endpoint, json=json, timeout=timeout)
        elif files is not None:
            response = request(endpoint, files=files, timeout=timeout)
        else:
            response = request(endpoint, timeout=timeout)
        code = response.status_code
        if code == 202 or code == 200:
            return response
        elif code == 404:
            st.error(f'Адрес {endpoint} недоступен. Код ответа: {code} ({responses[code]})')
            if exit_on_error:
                exit()
        elif code == 500:
            st.error(f'Ошибка обработки данных в {endpoint}. Код ответа: {code} ({responses[code]})')
            if exit_on_error:
                exit()
    except Exception as ex:
        st.error(f'Нет ответа от {endpoint}. Подробности: {ex}')
        if exit_on_error:
            exit()


def request_dataset(dataset_name: str) -> pd.DataFrame:
    """
    Получение датасета из бэкэнда по имени датасета
    :param dataset_name: путь к файлу
    :return: датасет
    """
    response = http_request(kind='get', service='dataset', param_name=dataset_name)
    df = pd.DataFrame.from_dict(response.json(), orient='columns')
    df = dtypes_convert(df.set_index(df.columns[0]))

    return df


def request_config(config_name: Text) -> dict:
    """
    Получение словаря с конфигурацией проекта
    :param config_name: путь к файлу
    :return: датасет
    """
    response = http_request(kind='get', service=f'{config_name}_config')
    config = response.json()

    return config


def request_json(json_name: Text) -> dict:
    """
    Получение JSON из бэкэнда
    :param json_name: путь к файлу
    :return: датасет
    """
    response = http_request(kind='get', service=json_name)
    config = response.json()['result']

    return config


def request_joblib(joblib_name: Text) -> joblib:
    """
    Получение данных обучения модели
    :param joblib_name: путь к файлу
    :return: объект joblib.load()
    """
    response = http_request(kind='get', service='joblib', param_name=joblib_name)
    buf = io.BytesIO(response.content)
    result = joblib.load(buf)

    return result


def check_backend_health(service: str):
    response = http_request(kind='get', service=f'{service}_health', exit_on_error=False)
    if response is not None:
        health = response.json()
        if not health['database']:
            st.error(f'Ошибка связи с БД сервиса {service}')
            return False
        else:
            return True
    return False
