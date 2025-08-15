import json
from flask import Flask, render_template, redirect, url_for, request, g
from markupsafe import Markup # Изменено здесь

app = Flask(__name__)

# --- Конфигурация языков ---
SUPPORTED_LANGUAGES = ['ru', 'en']
DEFAULT_LANGUAGE = 'ru'
app.config['SUPPORTED_LANGUAGES'] = SUPPORTED_LANGUAGES
app.config['DEFAULT_LANGUAGE'] = DEFAULT_LANGUAGE
# --------------------------

# --- Загрузка переводов ---
translations = {}
try:
    # Убедитесь, что файл translations.json находится в той же папке, что и app.py
    # или укажите правильный путь к нему
    with open('translations.json', 'r', encoding='utf-8') as f:
        translations = json.load(f)
except FileNotFoundError:
    print("ОШИБКА: Файл translations.json не найден!")
except json.JSONDecodeError:
    print("ОШИБКА: Не удалось декодировать translations.json!")
# --------------------------

# --- Выбор языка перед каждым запросом ---
@app.before_request
def before_request():
    lang_code = request.view_args.get('lang_code') if request.view_args else None
    if lang_code not in SUPPORTED_LANGUAGES:
        lang_code = DEFAULT_LANGUAGE
    g.lang_code = lang_code
# ---------------------------------------

# --- Контекстный процессор для передачи переводов в шаблон ---
@app.context_processor
def inject_translations():
    def get_text(key):
        # Используем g.lang_code, установленный в before_request
        locale_translations = translations.get(g.lang_code, translations.get(DEFAULT_LANGUAGE, {}))
        # Применяем Markup к результату
        return Markup(locale_translations.get(key, key))

    return dict(
        _=get_text,
        current_lang=g.lang_code,
        supported_langs=SUPPORTED_LANGUAGES
    )
# ------------------------------------------------------------

# --- Маршрут для корневого URL -> редирект на язык по умолчанию ---
@app.route('/')
def root():
    return redirect(url_for('index', lang_code=DEFAULT_LANGUAGE))
# ------------------------------------------------------------

# --- Основной маршрут с кодом языка ---
@app.route('/<lang_code>/')
def index(lang_code):
    if lang_code not in SUPPORTED_LANGUAGES:
        return redirect(url_for('index', lang_code=DEFAULT_LANGUAGE))
    # Шаблон index.html будет отрендерен с доступом к _(), current_lang, supported_langs
    return render_template('index.html')
# -------------------------------------

# --- Маршрут для /backend/ -> редирект на язык по умолчанию ---
@app.route('/backend/')
def backend_root():
    return redirect(url_for('backend', lang_code=DEFAULT_LANGUAGE))
# ------------------------------------------------------------

# --- Маршрут для страницы бэкенда с кодом языка ---
@app.route('/<lang_code>/backend/')
def backend(lang_code):
    if lang_code not in SUPPORTED_LANGUAGES:
        return redirect(url_for('backend', lang_code=DEFAULT_LANGUAGE))
    return render_template('backend.html')
# --------------------------------------------------

# --- Запуск приложения (если это главный файл) ---
if __name__ == '__main__':
    app.run(debug=True)
# -----------------------------------------------