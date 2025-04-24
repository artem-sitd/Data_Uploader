import pandas as pd
import numpy as np
import plotly.graph_objs as go
from plotly.offline import plot
from .models import Dataset
from .db import db
import io


# здесь используется нумпи, потому что массив данных большой,
# средствами питона будет выполняться дольше, чем нумпи, написанный на С
def calculate_statistics(df):
    angle = df["angle"].values
    return {
        "mean": np.mean(angle),
        "max": np.max(angle),
        "std": np.std(angle)
    }


# алгоритм счетчика пиков
def detect_peaks(df):
    angles = df["angle"].values
    peaks = 0
    last_min = angles[0]

    for angle in angles[1:]:
        if abs(angle - last_min) > 20:
            peaks += 1
            last_min = angle
        if angle < last_min:
            last_min = angle

    return peaks


# построение графика plotly
def build_plot(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["angle"], mode='lines', name='Angle'))
    fig.update_layout(title='График угла', xaxis_title='Timestamp', yaxis_title='Angle')
    return plot(fig, output_type='div', include_plotlyjs="cdn")


# сохранение файла в свое хранилище (можно переделать в S3), создание записи в БД Dataset
# парсинг ексель файла, приведение типов для быстрой вставки в БД
# следом рассчет необходимых показателей и вставка их в БД, чтобы не выполнять каждый раз рассчеты при доступе к эндпойнту
def import_dataset_from_excel(path: str, name: str):
    df = pd.read_excel(path)

    # создаём запись о наборе данных
    new_ds = Dataset(name=name)
    db.session.add(new_ds)
    db.session.commit()

    # анализируем до записи в базу
    df["dataset_id"] = new_ds.id
    df = df.astype({
        "timestamp": "int32", "emg1": "int32", "emg2": "int32",
        "emg3": "int32", "emg4": "int32", "angle": "int32", "dataset_id": "int32"
    })

    stats = calculate_statistics(df)
    peaks = detect_peaks(df)
    plot_html = build_plot(df)

    # сохраняем статистику в отдельную таблицу, для обращения в БД,
    # вместо вычисления при обращении к ручке
    from .models import DatasetStats
    stats_entry = DatasetStats(
        dataset_id=int(new_ds.id),
        mean=float(stats["mean"]),
        max=int(stats["max"]),
        std=float(stats["std"]),
        peaks=int(peaks),
        plot_html=plot_html
    )

    db.session.add(stats_entry)
    db.session.commit()

    # преобразовываем массив в CSV формат,
    # и используем низкоуровневый bulk загрузчик

    # создаем поток для чтения файла из оперативной памяти
    buffer = io.StringIO()

    # преобразовываем pandas dataframe в формат CSV + храним его в RAM
    df.to_csv(buffer, index=False, header=False)

    # ставим "курсор в начало"
    buffer.seek(0)

    # открываем транзакцию для низкоуровнегой записи
    # db.engine - хранит данные о подключении из конфига)
    connection = db.engine.raw_connection()
    try:
        with connection.cursor() as cursor:
            cursor.copy_expert("""
                COPY datapoints (timestamp, emg1, emg2, emg3, emg4, angle, dataset_id)
                FROM STDIN WITH CSV
            """, buffer)
        connection.commit()
    except Exception as e:
        print(f'ошибка в бд: {e}')
    finally:
        connection.close()
