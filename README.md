# foodgram - дипломный проект бекэнд разработчика python

### Как запустить проект:

Установить docker на боевой сервер

```
# Установка утилиты для скачивания файлов
sudo apt install curl
# Эта команда скачает скрипт для установки докера
curl -fsSL https://get.docker.com -o get-docker.sh
# Эта команда запустит его
sh get-docker.sh
```

Клонировать репозиторий на боевой сервер и перейти в него в командной строке:

```
git clone git@github.com:Falken565/foodgram-project-react.git
```

```
cd foodgram-project-react/backend
```

Cоздать файл с переменными окружения .env:

```
# блок базы данных
DB_ENGINE=django.db.backends.postgresql_psycopg2 # указываем бд, с которой работаем
POSTGRES_DB=foodgram_db # имя бд 
POSTGRES_USER=vasya666 # логин для подключения к бд (укажите свой)
POSTGRES_PASSWORD=123321 # пароль для подключения к бд (укажите свой)
DB_HOST=db # название контейнера
DB_PORT=5432 # порт для подключения к БД
# секретики для settings.py
SECRET_KEY=<super-secret-key>
```

Заглянуть в nginx и указать адрес сервера:

```
cd nginx
nano nginx.conf

server_name 127.0.0.1; # указать внешний ip сервера
```

Запуск приложения в контейнерах:

```
docker-compose up -d --build
```

Выполнить миграции:

```
docker-compose exec web python manage.py migrate
```

Создаем пользователя:

```
docker-compose exec web python manage.py createsuperuser
```

Собираем статику:

```
docker-compose exec web python manage.py collectstatic --no-input
```

Заполняем базу ингридиентов:

```
docker-compose exec web python manage.py load_data
```

### Где искать:
проект развернут в облаке по адресу: 
```
www.falken.gq
```

### Информация о проекте:

- Проект работает с СУБД PostgreSQL.
- Проект запущен на сервере в Яндекс.Облаке в трёх контейнерах: nginx, PostgreSQL и Django+Gunicorn. Заготовленный контейнер с фронтендом используется для сборки файлов.
- В nginx настроена раздача статики, запросы с фронтенда переадресуются в контейнер с Gunicorn. Джанго-админка работает напрямую через Gunicorn.
- Данные сохраняются в volumes.
