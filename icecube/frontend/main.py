"""
Программа: Frontend часть проекта
Версия: 0.3.1
"""
#import time
#import prometheus_client as pc
import socket
import streamlit as st
from random import sample
from src.data.get_data import load_data
from src.data.requester import http_request, request_dataset, check_backend_health
from src.evaluate.evaluate import evaluate_input, evaluate_from_file
from src.plotting.charts import sensors_3d, plot_meta, plot_charge_hist, barplot_aux, histplot_time, event_plot
from src.train.training import start_train


# def is_port_in_use(port):
#     """
#     Проверка того, что Prometheus HTTP Server уже запущен
#     :param port: номер порта
#     :retun: порт занят
#     """
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
#         return sock.connect_ex(('localhost', port)) == 0


# Start Prometheus HTTP server
# prometheus_port = 9501
# print(f'Attempting to start Prometheus HTTP server')
# if not is_port_in_use(prometheus_port):
#     pc.start_http_server(prometheus_port)
#     print(f'Prometheus HTTP server started at port {prometheus_port}')


def main_page():
    """
    Страница с описанием проекта
    """
    st.markdown("# Описание проекта")
    st.title("IceCube - Neutrinos in Deep Ice ❄️💫")
    check_backend_health('train')
    check_backend_health('predict')
    st.markdown(
        """
        <b>IceCube</b> — нейтринная обсерватория, построенная на антарктической станции Амундсен-Скотт.
        IceCube расположен глубоко в толще антарктического льда. На глубине от 1450 до 2450 м помещены прочные «нити»
        с прикреплёнными оптическими детекторами (фотоумножителями). Каждая «нить» имеет 60 фотоумножителей - всего
        5160 сенсоров. Оптическая система регистрирует излучение мюонов высокой энергии, движущихся в направлении вверх
        (то есть из-под земли). Эти мюоны могут рождаться только при взаимодействии мюонных нейтрино, прошедших сквозь
        Землю, с электронами и нуклонами льда (и слоя грунта подо льдом, толщиной порядка 1 км).<br><br>
        """,
        unsafe_allow_html=True
    )
    st.image(
        "https://storage.googleapis.com/kaggle-media/competitions/IceCube/icecube_detector.jpg",
        width=600,
    )
    st.markdown(
        """
        Необходимо определить, с какого направления пришли нейтрино, обнаруженные нейтринной обсерваторией IceCube
        на основании информации от фотодетекторов, зафиксировавших излучение. В качестве исходных данных имеются
        координаты фотодатчиков обсерватории (<b>sensor_geometry.csv</b>), результаты прошлых исследований с расчетом
        сферических координат векторов движения нейтрино (<b>train_meta.parquet, batch_N.parquet</b>)
        """,
        unsafe_allow_html=True
    )
    with st.expander('Описание исходных данных'):
        st.markdown(
            """
            <b>Данные для обучения:</b></br>
            <u><b>sensor_geometry.csv</b></u> - информация с координатами фотодатчиков обсерватории:<br>
            <ul>
                <li><b>sensor_id</b> - идентификатор фотодатчика</li>
                <li><b>x, y, z</b> - координаты фотодатчиков в декартовой системе в метрах</li>
            </ul>
            <u><b>batch_N.parquet</b></u> - наблюдения последовательностями фиксаций лучей нейтрино фотодатчиками,
            объединенные в пакетные датасеты (batch). N ∈ [1, 660]:<br>
            <ul>
                <li><b>event_id</b> - идентификатор события. В каждое событие входит несколько строк по числу
                фотодатчиков, обнаруживших излучение </li>
                <li><b>sensor_id</b> - идентификатор фотодатчика, зафиксировавшего излучение (импульс)</li>
                <li><b>time</b> - момент времени импульса в наносекундах в рамках текущего события
                (относительное время)</li>
                <li><b>charge</b> - величина импульса нейтрино</li>
                <li><b>auxiliary</b> - флаг того, что измерение не было полностью оцифровано и имеет низкое
                качество или соответствует шуму</li>
            </ul>
            <u><b>train_meta.parquet</b></u> / <u><b>test_meta.parquet</b></u> - сводная таблица наблюдений,
            каждая строка которой представляет одно наблюдение из датасетов <b>batch_N.parquet</b> с расчетом
            направления луча нейтрино:<br>
            <ul>
                <li><b>batch_id</b> - идентификатор пакета событий. Соотносится с номером <b>N</b> файлов
                <b>batch_N.parquet</b></li>
                <li><b>event_id</b> - идентификатор события. В каждое событие входит несколько строк по числу
                фотодатчиков, обнаруживших излучение </li>
                <li><b>first_pulse_index</b> - сквозной номер первой фиксации излучения нейтрино (импульс)
                в рамках одного события <b>(event_id)</b></li>
                <li><b>last_pulse_index</b> - сквозной номер последней фиксации излучения нейтрино (импульс)
                в рамках одного события <b>(event_id)</b></li>
                <li><b>azimuth (𝜙)</b> - расчетный угол азимута луча появления нейтрино в радианах [0, 2𝜋],
                отсутствует в <b>test_meta.parquet</b></li>
                <li><b>zenith (𝜃)</b> - расчетный угол зенита луча появления нейтрино в радианах [0, 𝜋],
                отсутствует в <b>test_meta.parquet</b></li>

            <b>azimuth, zenith</b> - целевые переменные
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            """
            <b>Данные для теста:</b></br>
            <u><b>batch_661.parquet</b></u> - пакет событий № 661 - тестовый, формат аналогичен
            предыдущим датасетам.
            Метаданные содержатся в <b>test_meta.parquet</b>
            """,
            unsafe_allow_html=True
        )


@st.cache_data(show_spinner=False)
def data_loader():
    """
    Загрузка в память датафреймов метаданных и геометрии оптических нитей
    :return: геометрии оптических нитей, датафреймы метаданных, батч-данных и список номеров событий
    """
    datasets = ['sensor_geometry', 'train_meta_sample', 'train_batches_sample']
    dfs = []
    download_bar = st.progress(0, text='Загрузка метаданных...')

    for i in range(len(datasets)):
        # load datasets
        download_bar.progress(i/len(datasets), text=f'Загрузка метаданных... {datasets[i]}')
        dfs.append(request_dataset(datasets[i]))

    download_bar.progress(100, 'Загрузка метаданных завершена')

    return dfs


def exploratory():
    """
    Exploratory data analysis
    """
    st.markdown('# Exploratory data analysis')
    train_healthy = check_backend_health('train')
    if train_healthy:
        sensor_geometry, train_meta_sample, batches_sample = data_loader()
        event_ids = sorted(sample(list(set(batches_sample.index)), 100))
        st.write(f'Batch data:')
        st.write(batches_sample.head())
        st.write('Train meta')
        st.write(train_meta_sample.head())
        st.write('Sensor geometry')
        st.write(sensor_geometry.head())

        # plotting with checkbox
        sensors_3d_cb = st.sidebar.checkbox('Геометрия оптических нитей IceCube')
        plot_meta_cb = st.sidebar.checkbox('Статистика направлений лучей нейтрино')
        plot_charge_hist_cb = st.sidebar.checkbox('Статистика величин импульсов нейтрино')
        barplot_aux_cb = st.sidebar.checkbox('Статистика импульсов с признаком auxiliary')
        histplot_time_cb = st.sidebar.checkbox('Признак auxiliary - величина импульсов')
        event_plot_cb = st.sidebar.checkbox('3D-график импульсов и расчетного вектора события')

        if sensors_3d_cb:
            st.plotly_chart(
                sensors_3d(
                    sensor_geometry=sensor_geometry
                )
            )
        if plot_meta_cb:
            st.pyplot(
                plot_meta(
                    train_meta=train_meta_sample
                )
            )
        if plot_charge_hist_cb:
            st.pyplot(
                plot_charge_hist(
                    batch_df=batches_sample
                )
            )
        if barplot_aux_cb:
            st.pyplot(
                barplot_aux(
                    batch_df=batches_sample
                )
            )
        if histplot_time_cb:
            st.pyplot(
                histplot_time(
                    batch_df=batches_sample
                )
            )
        if event_plot_cb:
            event_id = st.selectbox('Выберите event_id', event_ids)
            st.plotly_chart(
                event_plot(
                    event_id=event_id,
                    batch_data=batches_sample,
                    sensor_geometry=sensor_geometry,
                    train_meta=train_meta_sample
                )
            )


def train():
    """
    Тренировка модели
    """
    st.markdown('# Train model CatBoost')
    train_healthy = check_backend_health('train')
    if train_healthy:
        if st.button('Start training'):
            start_train()


def prediction():
    """
    Получение предсказаний путем ввода данных
    """
    st.markdown('# Prediction')
    predict_healthy = check_backend_health('predict')
    if predict_healthy:
        # проверка на наличие сохраненной модели
        response = http_request(kind='get', service='verify')
        is_model_trained = bool(response.json()['result'])
        if is_model_trained:
            evaluate_input()
        else:
            st.error('Сначала обучите модель')


def prediction_from_file():
    """
    Получение предсказаний из файла с данными
    """
    st.markdown('# Prediction')
    predict_healthy = check_backend_health('predict')
    if predict_healthy:
        upload_file = st.file_uploader(label='Upload a test file',
                                       type=['parquet'],
                                       accept_multiple_files=False)
        # проверка загружен ли файл
        if upload_file:
            with st.spinner('Загружаем датафрейм...'):
                dataset_df, files = load_data(data_path=upload_file, data_type='Test')
            # проверка на наличие сохраненной модели
            response = http_request(kind='get', service='verify')
            is_model_trained = bool(response.json()['result'])
            if is_model_trained:
                evaluate_from_file(files=files)
            else:
                st.error('Сначала обучите модель')


def main():
    """
    Сборка пайплайна в одном блоке
    """
    st.set_page_config(page_title='IceCube neutrinos', page_icon='❄️')
    page_names_to_funcs = {
        'Project description': main_page,
        'Exploratory data analysis': exploratory,
        'Training model': train,
        'Prediction from file': prediction_from_file,
        'Prediction': prediction,
    }
    st.sidebar.caption(f'Hostname: {socket.gethostname()}')
    selected_page = st.sidebar.selectbox('Выберите пункт', page_names_to_funcs.keys())
    page_names_to_funcs[selected_page]()
    # REQUEST_COUNT.inc()


if __name__ == '__main__':
    main()
