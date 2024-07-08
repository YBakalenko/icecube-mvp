"""
Программа: Тренировка данных и сборный конвейер для тренировки модели
Версия: 0.3.1
"""
import os
from sklearn.model_selection import train_test_split
from catboost import CatBoostRegressor, sum_models
from sklearn.model_selection import KFold
import pandas as pd
import optuna
from optuna import Study
from typing import Tuple
import joblib
from ..data.split_dataset import get_train_test_data
from ..train.metrics import save_metrics, get_metrics
from ..data.get_data import read_config, get_batch
from ..data.database_interface import query_joblib, insert_file, insert_data
from ..transform.transform import pipeline_preprocess_train


class TrainStatus:
    def __init__(self, stage: str = 'Not running', progress: float = 0, result: dict = {}):
        self.stage = stage
        self.progress = progress
        self.result = result

    def update(self, stage: str, progress_delta: float, result: dict = None):
        self.stage = stage
        self.progress += progress_delta
        self.result = result

    def get(self):
        status = {
            'stage': self.stage,
            'progress': self.progress,
            'result': self.result
        }
        return status

    def reset(self):
        self.stage = 'Not running'
        self.progress = 0.0
        self.result = {}


train_status = TrainStatus()


def train_batch(x_train: pd.DataFrame,
                y_train: pd.DataFrame,
                x_val: pd.DataFrame,
                y_val: pd.DataFrame,
                model_parameters) -> type(CatBoostRegressor):
    """
    Обучение модели CatBoostRegressor для одного батча
    :param x_train: датафрейм с признаками для обучения
    :param y_train: датафрейм с таргетами для обучения
    :param x_val: датафрейм с признаками для проверки
    :param y_val: датафрейм с таргетами для проверки
    :param model_parameters: гиперпараметры модели CatBoostRegressor
    """
    train_cfg = read_config()['train']
    clf = CatBoostRegressor(allow_writing_files=False,
                            loss_function='MultiRMSE',
                            eval_metric='MultiRMSE',
                            random_state=train_cfg['random_state'],
                            **model_parameters)
    eval_set = [(x_val, y_val)]
    clf.fit(x_train,
            y_train,
            eval_set=eval_set,
            verbose=False,
            early_stopping_rounds=100)

    return clf


def train_cv(n_folds: int = 5, **model_parameters) -> Tuple[type(CatBoostRegressor), dict, dict]:
    """
    Обучение модели CatBoostRegressor для всех батчей с кросс-валидацией
    :param n_folds: количество фолдов для кросс-валидации
    :param model_parameters: гиперпараметры модели CatBoostRegressor
    :return: обученная модель класса CatBoostRegressor, словари метрик на train и test
    """
    config = read_config()
    preproc_cfg = config['preprocessing']
    train_cfg = config['train']
    cv = KFold(n_splits=n_folds,
               shuffle=True,
               random_state=train_cfg['random_state'])

    filepath = train_cfg['file_dirs']['processed_batches_sample']['local_dir']
    filename = train_cfg['file_dirs']['processed_batches_sample']['filename']
    path = filepath + filename

    # Обрабатываем batch-файл с кросс-валидацией
    batch_data = get_batch(path)
    x_train, x_test, y_train, y_test = get_train_test_data(batch_data, preproc_cfg['test_size'])
    cv_models = []
    for idx, (train_idx, test_idx) in enumerate(cv.split(x_train, y_train)):
        x_train_, x_val = x_train.iloc[train_idx], x_train.iloc[test_idx]
        y_train_, y_val = y_train.iloc[train_idx], y_train.iloc[test_idx]
        model = train_batch(x_train_, y_train_, x_val, y_val, model_parameters)
        cv_models.append(model)

    # находим среднее моделей с кросс-валидацией
    models_cv_avg = sum_models(cv_models, weights=[1.0 / len(cv_models)] * len(cv_models))
    score_test = get_metrics(y_test,
                             models_cv_avg.predict(x_test),
                             x_test)
    score_train = get_metrics(y_train,
                              models_cv_avg.predict(x_train),
                              x_train)

    return models_cv_avg, score_train, score_test


def objective(trial,
              n_folds: int = 5,
              n_estimators: int = 1000,
              learning_rate: float = 0.01) -> float:
    """
    Целевая функция оптимизации всех основных гиперпараметров, кроме шага (learning_rate)
    и числа базовых алгоритмов (n_estimators)
    :param trial: номер итерации
    :param n_folds: количество выборок при выполнении кросс-валидации
    :param n_estimators: количество базовых алгоритмов
    :param learning_rate: шаг обучения
    """
    params = {
        'n_estimators': trial.suggest_categorical('n_estimators', [n_estimators]),
        'learning_rate': trial.suggest_categorical('learning_rate', [learning_rate]),
        'max_depth': trial.suggest_int('max_depth', 3, 12),
        'colsample_bylevel': trial.suggest_float('colsample_bylevel', 0.5, 1.0),
        'l2_leaf_reg': trial.suggest_uniform('l2_leaf_reg', 1e-5, 1e2),
        'random_strength': trial.suggest_uniform('random_strength', 10, 50),
        'bootstrap_type': trial.suggest_categorical('bootstrap_type',
                                                    ['Bayesian', 'Bernoulli', 'MVS', 'No']),
        'border_count': trial.suggest_categorical('border_count', [128, 254]),
        'grow_policy': trial.suggest_categorical('grow_policy',
                                                 ['SymmetricTree', 'Depthwise', 'Lossguide']),
        'od_wait': trial.suggest_int('od_wait', 500, 2000),
        'leaf_estimation_iterations': trial.suggest_int('leaf_estimation_iterations', 1, 15),
        'use_best_model': trial.suggest_categorical('use_best_model', [True])
    }

    if params['bootstrap_type'] == 'Bayesian':
        params['bagging_temperature'] = trial.suggest_float('bagging_temperature', 0, 100)
    elif params['bootstrap_type'] == 'Bernoulli':
        params['subsample'] = trial.suggest_float('subsample', 0.1, 1, log=True)

    model, score_train, score_test = train_cv(n_folds=n_folds, **params)

    return score_test['angular_distance']


def trial_func(trial) -> float:
    """
    Вызов функции поиска целевых значений оптимизации
    :param trial: итератор модели optuna
    """
    train_cfg = read_config()['train']

    return objective(trial=trial,
                     n_folds=train_cfg['n_folds'],
                     n_estimators=train_cfg['n_estimators'],
                     learning_rate=train_cfg['learning_rate'])


class TrialCounterCallback:
    """
    Расчет прогресса задачи оптимизации гиперпараметров
    """
    def __init__(self, trials: int):
        self.trials = trials
        self._trial_id = 0

    def __call__(self, study: optuna.study.Study, trial: optuna.trial.FrozenTrial) -> None:
        self._trial_id += 1
        train_status.update('Оптимизация гиперпараметров', 1 / self.trials * 0.8)


def params_optimizer() -> Study:
    """
    Pipeline для оптимизации гиперпараметров модели
    :return: [CatBoostRegressor tuning study result]
    """
    train_cfg = read_config()['train']
    study = query_joblib('study')
    if study is None:
        study = optuna.create_study(direction='minimize', study_name='CatBoost_main')
        optuna.logging.set_verbosity(optuna.logging.WARNING)
        study_cb = TrialCounterCallback(train_cfg['n_trials'])
        study.optimize(func=trial_func,
                       n_trials=train_cfg['n_trials'],
                       callbacks=[study_cb],
                       show_progress_bar=True,
                       n_jobs=-1)
    return study


def train(model_parameters) -> Tuple[type(CatBoostRegressor), dict, dict]:
    """
    Обучение модели CatBoostRegressor для всех батчей
    :param model_parameters: гиперпараметры модели CatBoostRegressor
    :return: обученная модель класса CatBoostRegressor, словари метрик на train и test
    """
    config = read_config()
    train_cfg = config['train']
    preproc_cfg = config['preprocessing']

    filepath = train_cfg['file_dirs']['processed_batches_sample']['local_dir']
    filename = train_cfg['file_dirs']['processed_batches_sample']['filename']
    path = filepath + filename
    # Проверяем наличие batch-файла
    check_file = os.path.isfile(path)
    assert check_file, f'Batch file {path} is missing.'
    # Обрабатываем batch-файл
    batch_data = get_batch(path)
    x_train, x_test, y_train, y_test = get_train_test_data(batch_data, preproc_cfg['test_size'])
    x_train_, x_val, y_train_, y_val = train_test_split(
        x_train,
        y_train,
        test_size=0.16,
        shuffle=True,
        random_state=train_cfg['random_state'])
    model = train_batch(x_train_, y_train_, x_val, y_val, model_parameters)
    score_test = get_metrics(y_test, model.predict(x_test), x_test)
    score_train = get_metrics(y_train, model.predict(x_train), x_train)

    # сохраняем метрики в файл
    save_metrics(score_test)

    return model, score_train, score_test


def pipeline_train() -> None:
    """
    Полный цикл получения данных, обработки данных и тренировки модели
    """
    # get params
    config = read_config()
    db_cfg = config['database']
    preproc_cfg = config['preprocessing']
    train_cfg = config['train']

    train_status.reset()

    # preprocessing
    stage = 'Подготовка данных для обучения'
    train_status.update(stage, 0)
    pipeline_preprocess_train()
    train_status.update(stage, 0.05)

    # find optimal params
    stage = 'Оптимизация гиперпараметров'
    train_status.update(stage, 0)
    study = params_optimizer()

    # train with optimal params
    stage = 'Обучение с оптимальными гиперпараметрами'
    train_status.update(stage, 0)
    clf, score_train, score_test = train(study.best_params)
    train_status.update(stage, 0.1)

    # save result (study, model)
    train_status.update('Сохранение результатов', 0)
    joblib.dump(clf, os.path.join(train_cfg['model_path']))
    joblib.dump(study, os.path.join(train_cfg['study_path']))

    # save result to mongo and also save config to mongo
    insert_file(db_cfg['fs']['model'], train_cfg['model_path'], replace=True)
    insert_file(db_cfg['fs']['study'], train_cfg['study_path'], replace=True)

    # save config to mongo
    insert_data(db_cfg['collection'], db_cfg['objects']['train_config'], train_cfg, replace=True)
    insert_data(db_cfg['collection'], db_cfg['objects']['preprocess_config'], preproc_cfg, replace=True)

    train_status.update('Завершено', 0.05, score_test)
