from time import time
import pandas as pd
import numpy as np
from scipy.signal import find_peaks
import plotly.graph_objs as go
from plotly.offline import plot
from .models import Dataset
from .db import db
import io


def calculate_statistics(df):
    angle = df["angle"].values
    return {
        "mean": np.mean(angle),
        "max": np.max(angle),
        "std": np.std(angle)
    }


def detect_peaks(df):
    peaks, _ = find_peaks(df["angle"].values, height=20)
    return len(peaks)


def build_plot(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["angle"], mode='lines', name='Angle'))
    fig.update_layout(title='График угла', xaxis_title='Timestamp', yaxis_title='Angle')
    return plot(fig, output_type='div', include_plotlyjs=False)


def import_dataset_from_excel(path: str, name: str):
    start = time()
    print(f'начало pd.read_excel(path)')

    df = pd.read_excel(path)
    print(f'конец pd.read_excel(path) {time() - start}')

    # Шаг 2: создаём запись о наборе данных
    start = time()
    print(f'начало new_ds = Dataset(name=name)')

    new_ds = Dataset(name=name)
    db.session.add(new_ds)
    db.session.commit()
    print(f'конец new_ds = Dataset(name=name) {time() - start}')

    # Шаг 3: добавляем колонку dataset_id
    start = time()
    print(f' добавление dataset_id')
    df["dataset_id"] = new_ds.id
    print(f'конец dataset_id {time() - start}')

    # Приводим типы для совместимости
    start = time()
    print(f'начало df = df.astype(')
    df = df.astype({
        "timestamp": "int32",
        "emg1": "int32",
        "emg2": "int32",
        "emg3": "int32",
        "emg4": "int32",
        "angle": "int32",
        "dataset_id": "int32"
    })
    print(f'конец df = df.astype( {time() - start} )')

    # Шаг 4: сериализация в память (StringIO)
    start = time()
    print(f'начало buffer = io.StringIO()')
    buffer = io.StringIO()
    df.to_csv(buffer, index=False, header=False)
    buffer.seek(0)
    print(f'конец buffer = io.StringIO() {time() - start}')

    # Шаг 5: прямое подключение к PostgreSQL
    start = time()
    print(f'начало connection = db.engine.raw_connection()')
    connection = db.engine.raw_connection()
    cursor = connection.cursor()

    cursor.copy_expert(
        """
        COPY datapoints (timestamp, emg1, emg2, emg3, emg4, angle, dataset_id)
        FROM STDIN WITH CSV
        """,
        buffer
    )

    connection.commit()
    cursor.close()
    connection.close()
    print(f'конец connection = db.engine.raw_connection() {time() - start}')
