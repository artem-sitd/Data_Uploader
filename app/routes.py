import os
from flask import Blueprint, render_template, request, redirect, url_for, current_app
from .models import Dataset
from .utils import import_dataset_from_excel


bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    datasets = Dataset.query.all()
    return render_template("index.html", datasets=datasets)


@bp.route("/dataset/<int:dataset_id>")
def view_dataset(dataset_id):
    dataset = Dataset.query.get_or_404(dataset_id)
    if not dataset.stats:
        return "Статистика ещё не рассчитана", 400

    return render_template(
        "dataset.html",
        dataset=dataset,
        stats={
            "mean": dataset.stats.mean,
            "max": dataset.stats.max,
            "std": dataset.stats.std
        },
        peaks=dataset.stats.peaks,
        plot_div=dataset.stats.plot_html
    )


@bp.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    name = request.form["name"]
    save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], f'{name}_{file.filename}')
    file.save(save_path)

    import_dataset_from_excel(save_path, name)
    return redirect(url_for("main.index"))
