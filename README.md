в .env.template присутствуют переменные, при необходимости можно указать свои

- FLASK_ENV=development # для авторестартов
- DATABASE_URL=postgresql+psycopg2://postgres:123@localhost:5432/emg_db
- UPLOAD_FOLDER=data/uploads # - путь для складирования загружаемых файлов с массивом данных
- SECRET_KEY=123 # Защита сессий и cookie

> Запуск: клонируем, далее .env.template перейминовываем в .env, при необходимости регулируем адрес / пользователя / пароль к базе.
> создаем виртуальное окружение, и устанавливаем pip install -r requirements.txt.
> точка входа main.py.
