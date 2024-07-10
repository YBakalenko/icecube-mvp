"""
Программа: Модель для предсказания направления возникновения лучей нейтрино
аппарата IceCube на основе метаданных прошлых исследований
Версия: 1.3
"""
import prometheus_client as pc
import warnings
import optuna
import pandas as pd
import uvicorn
from fastapi import FastAPI, File, UploadFile, Request, Response

from src.evaluate.evaluate import pipeline_evaluate
from src.data.get_data import read_config
from src.data.database_interface import query_json, check_db_connection

warnings.filterwarnings('ignore')
optuna.logging.set_verbosity(optuna.logging.WARNING)

# Define your metrics
REQUEST_COUNT = pc.Counter('request_count_value', 'Total number of requests')
REQUEST_LATENCY = pc.Histogram('request_latency_seconds', 'Request latency in seconds')

app = FastAPI()


@app.get('/evaluate_config')
def provide_preproc_config() -> dict:
    """
    Получение данных конфигурации датасетов, для Evaluate
    :return: словарь c конфигурацией
    """
    config = read_config()

    return config['evaluate']


@app.get('/predict')
def prediction(file: UploadFile = File(...)):
    """
    Предсказание модели по батч-данным из файла
    """
    result = pipeline_evaluate(batch_path=file.file)
    assert isinstance(result, pd.DataFrame), 'Результат не соответствует типу pandas.DataFrame'
    return {'result': result.head().to_json()}


@app.get('/predict_input')
async def prediction_input(request: Request):
    """
    :param request: тело запроса
    Предсказание модели по батч-данным, введенным вручную
    """
    # get config
    db_cfg = read_config()['database']
    preproc_cfg = query_json(db_cfg['collection'], db_cfg['objects']['preprocess_config'])
    data = await request.json()
    batch_df = pd.read_json(data, orient='columns')
    batch_df.set_index(preproc_cfg['event_column'], drop=True, inplace=True)
    result_df = pipeline_evaluate(batch_df=batch_df)
    assert isinstance(result_df, pd.DataFrame), 'Результат не соответствует типу pandas.DataFrame'
    return {'result': result_df.head().to_json()}


@app.get('/predict_health')
def provide_health_status() -> dict:
    """
    Предоставление статуса здоровья бэкэнда и его соединения с БД
    :return: словарь со статусом здоровья бэкэнда и базы
    """

    return {'backend': True, 'database': check_db_connection()}


# Prometheus endpoint
@app.get('/metrics')
def metrics():
    return Response(pc.generate_latest(),
                    media_type=pc.CONTENT_TYPE_LATEST)


if __name__ == '__main__':
    # Запустите сервер, используя заданный хост и порт
    uvicorn.run(app, host='127.0.0.1', port=9940)
