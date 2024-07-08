"""
Программа: Отрисовка слайдеров и кнопок для ввода данных
с дальнейшим получением предсказания на основании введенных значений
Версия: 0.3.1
"""
import pandas as pd
import streamlit as st
from ..data.get_data import read_config
from ..data.requester import http_request, request_config


def evaluate_input() -> None:
    """
    Получение входных данных путем ввода в UI -> вывод результата
    """
    preprocess_cfg = request_config('preprocessing')

    frontend_cfg = read_config()['frontend']
    path = frontend_cfg['template_batch']['local_dir'] + frontend_cfg['template_batch']['filename']
    batch_template = pd.read_parquet(path)

    # для ввода данных используем шаблон батч-датафрейма
    edited_df = st.data_editor(batch_template, num_rows='dynamic')

    # evaluate and return prediction (text)
    button_ok = st.button('Predict', key='input')
    if button_ok:
        edited_df[preprocess_cfg['aux_column']].fillna(False, inplace=True)
        # отправляем файл в backend
        with st.spinner('Получаем результаты от модели...'):
            response = http_request(kind='get', service='predict_input', json=edited_df.reset_index().to_json())
            st.success('Success!')
            predictions = pd.read_json(response.json()['result'], orient='columns')
            st.write(predictions.head())


def evaluate_from_file(files: dict):
    """
    Получение входных данных в качестве файла -> вывод результата в виде таблицы
    :param files: файлы с батч-данными для предсказания
    """
    button_pred = st.button('Predict', key='file')
    if button_pred:
        with st.spinner('Получаем результаты от модели...'):
            response = http_request(kind='get', service='predict', files=files)
            predictions = pd.read_json(response.json()['result'], orient='columns')
            st.success('Success!')
            st.write('Predicted angles:')
            st.write(predictions.head())
