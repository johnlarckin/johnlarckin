import json
from flask import Flask, g, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_babel import Babel, get_locale
from markupsafe import Markup
from config import Config

db = SQLAlchemy()
migrate = Migrate()
babel = Babel()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    def localeselector():
        # Try to get lang_code from the view args first
        lang_code = request.view_args.get('lang_code') if request.view_args else None
        if lang_code in app.config['SUPPORTED_LANGUAGES']:
            return lang_code
        # Then from the global context 'g'
        lang = g.get('lang_code')
        if lang in app.config['SUPPORTED_LANGUAGES']:
            return lang
        # Otherwise, use the best match from browser headers
        best_match = request.accept_languages.best_match(app.config['SUPPORTED_LANGUAGES'])
        # Finally, fallback to default language
        return best_match or app.config['DEFAULT_LANGUAGE']

    babel.init_app(app, locale_selector=localeselector)
    app.jinja_env.add_extension('jinja2.ext.do')

    # --- Загрузка переводов (Временно, будет заменено данными из БД) ---
    # Этот механизм будет изменен, когда мы перейдем на модели.
    # Пока что оставим его для совместимости с существующими шаблонами.
    try:
        with open('translations.json', 'r', encoding='utf-8') as f:
            app.translations = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        app.translations = {}
    # --------------------------------------------------------------------

    # --- Инициализация Admin Panel ---
    from app.admin import init_admin
    init_admin(app)
    # -----------------------------

    # --- Регистрация Blueprints ---
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    # --------------------------

    @app.before_request
    def before_request_locale():
        # Логика выбора языка из URL
        lang_code = request.view_args.get('lang_code') if request.view_args else None
        if lang_code in app.config['SUPPORTED_LANGUAGES']:
            g.lang_code = lang_code
        else:
            g.lang_code = localeselector()

    @app.context_processor
    def inject_global_vars():
        return dict(
            current_lang=g.get('lang_code', app.config['DEFAULT_LANGUAGE']),
            supported_langs=app.config['SUPPORTED_LANGUAGES']
        )

    # This context processor is no longer needed for translations,
    # as the logic will be handled in the templates.
    # We only need to provide the current language.
    @app.context_processor
    def inject_global_vars():
        return dict(
            current_lang=g.get('lang_code', app.config['DEFAULT_LANGUAGE']),
            supported_langs=app.config['SUPPORTED_LANGUAGES']
        )

    @app.route('/')
    def root():
        # Редирект на язык браузера или на язык по умолчанию
        lang_code = localeselector()
        return redirect(url_for('main.index', lang_code=lang_code))

    return app
