# Blogicum
Платформа для блогов. Позволяет вести собственный блог и читать блоги других пользователей.
## Стек:
- Python
- Django
## Запуск отладочного сервера
### Windows
1. Создание виртуального окружения:
   ```bash
   python -m venv venv
   ```
2. Активация виртуального окружения:
   ```bash
   venv\Scripts\activate
   ```
3. Установка зависимостей:
   ```bash
   pip install -r requirements.txt
   ```
4. Запуск сервера:
   ```bash
   cd blogicum
   python manage.py runserver
   ```
### Linux/macOS
1. Создание виртуального окружения:
   ```bash
   python3 -m venv venv
   ```
2. Активация виртуального окружения:
   ```bash
   source venv/bin/activate
   ```
3. Установка зависимостей:
   ```bash
   pip install -r requirements.txt
   ```
4. Запуск сервера:
   ```bash
   cd blogicum
   python3 manage.py runserver
   ```
