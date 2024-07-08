"""
Программа: Получение предсказания на основе обученной модели
Версия: 1.3
"""

import numpy as np
import pandas as pd
from typing import Union, BinaryIO
from ..data.get_data import read_config, get_batch
from ..data.database_interface import query_json, query_joblib
from ..transform.transform import pipeline_preprocess_evaluate, dtypes_convert


def cartesian_to_spherical(cart: np.ndarray) -> np.ndarray:
    """
    Обратное преобразование векторов декартовых координат в сферическую систему
    :param cart: массив векторов в декартовых координатах в формате [x, y, z]
    :return: массив векторов в сферических координатах в формате [azimuth, zenith]
    """
    x = cart[:, 0]
    y = cart[:, 1]
    z = cart[:, 2]
    rxy_sq = x**2 + y**2
    zenith = np.arctan2(np.sqrt(rxy_sq), z)
    zenith = np.where(zenith < 0, zenith + 2 * np.pi, zenith)
    azimuth = np.arctan2(y, x)
    azimuth = np.where(azimuth < 0, azimuth + 2 * np.pi, azimuth)

    return np.transpose(np.array([azimuth, zenith], dtype='float32'))


def pipeline_evaluate(batch_df: pd.DataFrame = None, batch_path: Union[str, BinaryIO] = None) -> pd.DataFrame:
    """
    Обработка входных данных и получение предсказаний
    :param batch_df: датасет батч-файла
    :param batch_path: путь до батч-файла с данными
    :return: датафрейм предсказаний
    """
    # get params
    db_cfg = read_config()['database']
    preprocess_cfg = query_json(db_cfg['collection'], db_cfg['objects']['preprocess_config'])

    # preprocessing
    if batch_path:
        batch_df = dtypes_convert(get_batch(batch_path=batch_path))
    batch_df = pipeline_preprocess_evaluate(data=batch_df)

    model = query_joblib(db_cfg['fs']['model'])

    prediction = model.predict(batch_df)
    prediction = cartesian_to_spherical(prediction)
    cols = preprocess_cfg['target_columns']
    result_df = pd.DataFrame(prediction, columns=cols, index=batch_df.index, dtype=float)

    return result_df
