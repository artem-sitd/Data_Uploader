import os
from flask import Blueprint, render_template, request, redirect, url_for, current_app
from .models import Dataset
from .utils import import_dataset_from_excel, calculate_statistics, detect_peaks, build_plot
import pandas as pd

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    datasets = Dataset.query.all()
    return render_template("index.html", datasets=datasets)


@bp.route("/dataset/<int:dataset_id>")
def view_dataset(dataset_id):
    dataset = Dataset.query.get_or_404(dataset_id)
    df = pd.DataFrame([{
        "timestamp": dp.timestamp,
        "angle": dp.angle
    } for dp in dataset.datapoints])

    stats = calculate_statistics(df)
    peaks = detect_peaks(df)
    plot_div = build_plot(df)

    return render_template("dataset.html", stats=stats, peaks=peaks,
                           plot_div=plot_div, dataset=dataset)


@bp.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    name = request.form["name"]
    save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], file.filename)
    file.save(save_path)

    import_dataset_from_excel(save_path, name)

    return redirect(url_for("main.index"))
