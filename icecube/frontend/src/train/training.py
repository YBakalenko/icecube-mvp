"""
Программа: Тренировка модели на backend, отображение метрик и
графиков обучения на экране
Версия: 0.3.1
"""
import time
import streamlit as st
import numpy as np
from optuna.visualization import plot_optimization_history, plot_param_importances
from ..data.requester import http_request, request_json, request_joblib


def get_training_status() -> dict:
    """
    Получение текущего статуса во время обучения модели
    :return: словарь-ответ формата {'stage', 'progress', 'result'}
    """
    response = http_request(kind='get', service='train_status')

    return response.json()


def start_train() -> None:
    """
    Тренировка модели с выводом результатов
    """
    # Last metrics
    old_metrics = request_json('metrics')
    if old_metrics is None:
        # если до этого не обучали модель и нет прошлых значений метрик
        old_metrics = {
            'mae': 0,
            'mse': 0,
            'rmse': 0,
            'r2_adjusted': 0,
            'mape': 0,
            'angular_distance': np.pi
        }
    # Train
    http_request(kind='post', service='train')
    progressbar = st.progress(0, text='Обучение модели')
    with progressbar:
        while True:
            training_status = get_training_status()
            progress = min(training_status['progress'], 1)
            stage = training_status['stage']
            progressbar.progress(progress, f'{stage}... {progress * 100:.0f}%')
            if progress >= 1 or stage == 'Завершено':
                new_metrics = training_status['result']
                progressbar.empty()
                break
            else:
                time.sleep(5)
    st.success('Success!')
    # diff metrics
    mae, mse, rmse, r2_adjusted, mape, angular_distance = st.columns(6)
    mae.metric(
        'MAE',
        new_metrics['mae'],
        f"{new_metrics['mae'] - old_metrics['mae']:.2f}",
        delta_color='inverse'
    )
    mse.metric(
        'MSE',
        new_metrics['mse'],
        f"{new_metrics['mse'] - old_metrics['mse']:.2f}",
        delta_color='inverse'
    )
    rmse.metric(
        'RMSE',
        new_metrics['rmse'],
        f"{new_metrics['rmse'] - old_metrics['rmse']:.2f}",
        delta_color='inverse'
    )
    r2_adjusted.metric(
        'R2 adjusted', new_metrics['r2_adjusted'],
        f"{new_metrics['r2_adjusted']-old_metrics['r2_adjusted']:.2f}"
    )
    mape.metric(
        'MAPE',
        new_metrics['mape'],
        f"{new_metrics['mape']-old_metrics['mape']:.2f}",
        delta_color='inverse'
    )
    angular_distance.metric(
        'Angular distance',
        new_metrics['angular_distance'],
        f"{new_metrics['angular_distance'] - old_metrics['angular_distance']:.2f}",
        delta_color='inverse'
    )

    # plot study
    study = request_joblib('study')

    fig_imp = plot_param_importances(study)
    fig_history = plot_optimization_history(study)

    st.plotly_chart(fig_imp, use_container_width=True)
    st.plotly_chart(fig_history, use_container_width=True)
