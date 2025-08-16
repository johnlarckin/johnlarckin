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
    return render_template('index.html', page='index')
# ------------------------------------------------------------

# --- Маршрут для /ceo/ -> редирект на язык по умолчанию ---
@app.route('/ceo/')
def ceo_root():
    return redirect(url_for('ceo', lang_code=DEFAULT_LANGUAGE))
# ------------------------------------------------------------

# --- Маршрут для страницы CEO с кодом языка ---
@app.route('/<lang_code>/ceo/')
def ceo(lang_code):
    if lang_code not in SUPPORTED_LANGUAGES:
        return redirect(url_for('ceo', lang_code=DEFAULT_LANGUAGE))
    return render_template('ceo.html', page='ceo')
# --------------------------------------------------

# --- Маршрут для /cfo/ -> редирект на язык по умолчанию ---
@app.route('/cfo/')
def cfo_root():
    return redirect(url_for('cfo', lang_code=DEFAULT_LANGUAGE))
# ------------------------------------------------------------

# --- Маршрут для страницы CFO с кодом языка ---
@app.route('/<lang_code>/cfo/')
def cfo(lang_code):
    if lang_code not in SUPPORTED_LANGUAGES:
        return redirect(url_for('cfo', lang_code=DEFAULT_LANGUAGE))
    return render_template('cfo.html', page='cfo')
# --------------------------------------------------

# --- Маршрут для /cto/ -> редирект на язык по умолчанию ---
@app.route('/cto/')
def cto_root():
    return redirect(url_for('cto', lang_code=DEFAULT_LANGUAGE))
# ------------------------------------------------------------

# --- Маршрут для страницы CTO с кодом языка ---
@app.route('/<lang_code>/cto/')
def cto(lang_code):
    if lang_code not in SUPPORTED_LANGUAGES:
        return redirect(url_for('cto', lang_code=DEFAULT_LANGUAGE))
    return render_template('cto.html', page='cto')
# --------------------------------------------------
# -------------------------------------

# --- Маршрут для /design/ -> редирект на язык по умолчанию ---
@app.route('/design/')
def design_root():
    return redirect(url_for('design', lang_code=DEFAULT_LANGUAGE))
# ------------------------------------------------------------

# --- Маршрут для страницы дизайна с кодом языка ---
@app.route('/<lang_code>/design/')
def design(lang_code):
    if lang_code not in SUPPORTED_LANGUAGES:
        return redirect(url_for('design', lang_code=DEFAULT_LANGUAGE))
    return render_template('design.html', page='design')
# --------------------------------------------------

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
    return render_template('backend.html', page='backend')
# --------------------------------------------------

# --- Маршрут для /ai/ -> редирект на язык по умолчанию ---
@app.route('/ai/')
def ai_root():
    return redirect(url_for('ai', lang_code=DEFAULT_LANGUAGE))
# ------------------------------------------------------------

# --- Маршрут для страницы ИИ с кодом языка ---
@app.route('/<lang_code>/ai/')
def ai(lang_code):
    if lang_code not in SUPPORTED_LANGUAGES:
        return redirect(url_for('ai', lang_code=DEFAULT_LANGUAGE))
    return render_template('ai.html', page='ai')
# --------------------------------------------------

# --- Маршрут для /security/ -> редирект на язык по умолчанию ---
@app.route('/security/')
def security_root():
    return redirect(url_for('security', lang_code=DEFAULT_LANGUAGE))
# ------------------------------------------------------------

# --- Маршрут для страницы безопасности с кодом языка ---
@app.route('/<lang_code>/security/')
def security(lang_code):
    if lang_code not in SUPPORTED_LANGUAGES:
        return redirect(url_for('security', lang_code=DEFAULT_LANGUAGE))
    return render_template('security.html', page='security')
# --------------------------------------------------

# --- Маршрут для /frontend/ -> редирект на язык по умолчанию ---
@app.route('/frontend/')
def frontend_root():
    return redirect(url_for('frontend', lang_code=DEFAULT_LANGUAGE))
# ------------------------------------------------------------

# --- Маршрут для страницы фронтенда с кодом языка ---
@app.route('/<lang_code>/frontend/')
def frontend(lang_code):
    if lang_code not in SUPPORTED_LANGUAGES:
        return redirect(url_for('frontend', lang_code=DEFAULT_LANGUAGE))
    return render_template('frontend.html', page='frontend')
# --------------------------------------------------

# --- Маршрут для /mobile/ -> редирект на язык по умолчанию ---
@app.route('/mobile/')
def mobile_root():
    return redirect(url_for('mobile', lang_code=DEFAULT_LANGUAGE))
# ------------------------------------------------------------

# --- Маршрут для страницы мобильных приложений с кодом языка ---
@app.route('/<lang_code>/mobile/')
def mobile(lang_code):
    if lang_code not in SUPPORTED_LANGUAGES:
        return redirect(url_for('mobile', lang_code=DEFAULT_LANGUAGE))
    return render_template('mobile.html', page='mobile')
# --------------------------------------------------

# --- Запуск приложения (если это главный файл) ---
if __name__ == '__main__':
    app.run(debug=True)
# -----------------------------------------------