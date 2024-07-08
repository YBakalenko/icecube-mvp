"""
Программа: Получение сырых данных для обучения модели
Версия: 1.3
"""
import os
import yaml
import pandas as pd
from typing import Text


def read_config() -> dict:
    """
    Чтение конфигурационного файла проекта
    :return: словарь настроек
    """

    config_path = './config/params.yml'
    config = yaml.load(open(config_path), Loader=yaml.FullLoader)

    return config


def get_batch(batch_path: Text) -> pd.DataFrame:
    """
    Получение данных из батч-файла по заданному пути
    :param batch_path: путь к батч-файлу
    :return: датасет
    """
    return pd.read_parquet(batch_path)


def read_dataset(dataset_path: Text) -> pd.DataFrame:
    """
    Получение данных из файла датасета по заданному пути и преобразование размерностей для экономии ресурсов
    :param dataset_path: путь к файлу
    :return: датасет
    """
    src_check_file = os.path.isfile(dataset_path)
    assert src_check_file, f'Dataframe file {dataset_path} is missing.'
    _, file_extension = os.path.splitext(dataset_path)
    if file_extension == '.parquet':
        df = pd.read_parquet(dataset_path)
    else:
        df = pd.read_csv(dataset_path)
    return df


def get_dataset(dataset_name: str) -> pd.DataFrame:
    """
    Загрузка в память датафрейма
    :param dataset_name: имя запрашиваемого датасета без расширения
    :return: датафрейм
    """
    config = read_config()
    preproc_cfg = config['preprocessing']

    # load datasets
    path = preproc_cfg['file_dirs'][dataset_name]['local_dir'] + preproc_cfg[
        'file_dirs'][dataset_name]['filename']
    df = read_dataset(dataset_path=path)

    return df
