#  Проект Foodgram

Ознакомится с проектом можно здесь:  [Foodrgam](https://foodgrampetrevich.hopto.org, 89.169.163.125) 

## Используемые технологии

<img src="https://img.shields.io/badge/Python-FFFFFF?style=for-the-badge&logo=python&logoColor=3776AB"/><img src="https://img.shields.io/badge/django-FFFFFF?style=for-the-badge&logo=django&logoColor=082E08"/><img src="https://img.shields.io/badge/Django REST Framework-FFFFFF?style=for-the-badge&logo=&logoColor=361508"/><img src="https://img.shields.io/badge/PostgreSQL-FFFFFF?style=for-the-badge&logo=PostgreSQL&logoColor=4169E1"/><img src="https://img.shields.io/badge/Nginx-FFFFFF?style=for-the-badge&logo=Nginx&logoColor=009639"/><img src="https://img.shields.io/badge/GitHub Actions-FFFFFF?style=for-the-badge&logo=GitHub Actions&logoColor=2088FF"/><img src="https://img.shields.io/badge/Docker-FFFFFF?style=for-the-badge&logo=Docker&logoColor=2496ED"/>


## О проекте

Социальная сеть «Фудграм» для любителей готовить и пробовать новые рецепты.
На сайте пользователи могут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд. Для каждого рецепта можно получить прямую короткую ссылку, которая не меняется после редактирования рецепта.

---

## Как ознакомиться с проектом

Клонируем репозиторий:
```yaml
git clone git@github.com:PetrevichEV/foodgram.git
```

Переходим в папку с проектом:
```yaml
cd foodgram
```

Установлеваем Docker:
Скачиваем установочный файл Docker Desktop. 
Дополнительно к Docker устанавливаем утилиту Docker Compose:
```yaml
sudo apt install docker-compose-plugin
```

Создаем в рабочей директории проекта файл .env со своими секретами:
```yaml
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
DB_NAME=
SECRET_KEY=
```

Из директории с docker-compose файлом выполните команду:
```yaml
sudo docker-compose -f docker-compose.yml up -d 
```

Выполните миграции и соберите статические данные:
```yaml
sudo docker-compose -f docker-compose.yml exec backend python manage.py makemigrations
sudo docker-compose -f docker-compose.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```

Заполните базу ингредиентами:
```yaml
sudo docker compose -f docker-compose.yml exec backend python manage.py load_data
```

Создайте суперпользователя:
```yaml
sudo docker compose -f docker-compose.yml exec backend python manage.py createsuperuser
```
