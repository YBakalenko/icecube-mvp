"""
Программа: Модель для предсказания направления возникновения лучей нейтрино
аппарата IceCube на основе метаданных прошлых исследований
Версия: 0.3.1
"""
import prometheus_client as pc
import warnings
import optuna
import joblib
import io
import uvicorn
from http import HTTPStatus
from fastapi import FastAPI, Response, BackgroundTasks, Request
from src.data.get_data import read_config, get_dataset
from src.data.database_interface import query_joblib, check_db_connection
from src.train.metrics import load_metrics
import src.train.train as train


warnings.filterwarnings('ignore')
optuna.logging.set_verbosity(optuna.logging.WARNING)

# Define your metrics
REQUEST_COUNT = pc.Counter('train_request_count', 'Total number of requests')
REQUEST_LATENCY = pc.Histogram('train_request_latency', 'Request latency in seconds')

app = FastAPI()


@app.get('/train_status')
async def train_status() -> dict:
    """
    Статус обучения модели в реальном времени для отслеживания в Frontend
    :return: словарь с текущим статусом обучения модули
    """
    training_status = train.train_status.get()

    return training_status


@app.post('/train', status_code=HTTPStatus.ACCEPTED)
async def training(background_tasks: BackgroundTasks) -> dict:
    """
    Обучение модели, логирование метрик
    :return: словарь с метриками модели
    """
    background_tasks.add_task(train.pipeline_train)
    training_status = train.train_status.get()

    return training_status


@app.get('/score')
def provide_metrics() -> dict:
    """
    Предоставление метрик прошлого обучения модули
    :return: словарь с метриками модели
    """
    metrics = load_metrics()

    return {'result': metrics}


@app.get('/dataset')
async def provide_dataset(name: str) -> dict:
    """
    Получение датасета, на котором будет тренироваться модель, для Exploratory
    :param name: имя датасета
    :return: датасет
    """
    df = get_dataset(name)
    result = df.reset_index().to_dict()

    return result


@app.get('/preprocessing_config')
def provide_preproc_config() -> dict:
    """
    Получение данных конфигурации датасетов, для Evaluate
    :return: словарь c конфигурацией
    """
    config = read_config()

    return config['preprocessing']


@app.get('/train_config')
def provide_train_config() -> dict:
    """
    Получение данных конфигурации проекта, в котором будет тренироваться модель, для Evaluate
    :return: словарь c конфигурацией
    """
    config = read_config()

    return config['train']


@app.get('/verify')
def is_trained() -> dict:
    """
    Получение информации о том, обучена ли модель
    :return: словарь с булевой переменной о наличии обученной модели
    """
    db_config = read_config()['database']
    if query_joblib(db_config['fs']['model']):
        return {'result': True}
    else:
        return {'result': False}


@app.get('/joblib')
async def provide_joblib(name: str) -> Response:
    # Load the Optuna study
    db_cfg = read_config()['database']
    study = query_joblib(db_cfg['fs'][name])
    # Serialize the study object
    buf = io.BytesIO()
    joblib.dump(study, buf)
    buf.seek(0)

    return Response(content=buf.getvalue(), media_type="application/octet-stream")


@app.get('/train_health')
def provide_health_status() -> dict:
    """
    Предоставление статуса здоровья бэкэнда и его соединения с БД
    :return: словарь со статусом здоровья бэкэнда и базы
    """
    return {'backend': True, 'database': check_db_connection()}


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    REQUEST_COUNT.inc()
    with REQUEST_LATENCY.time():
        response = await call_next(request)
    return response


# Prometheus endpoint
@app.get('/metrics')
def metrics():
    return Response(pc.generate_latest(),
                    media_type=pc.CONTENT_TYPE_LATEST)


if __name__ == '__main__':
    # Запустите сервер, используя заданный хост и порт
    uvicorn.run(app, host='127.0.0.1', port=18507)
