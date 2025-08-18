from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, BaseView, expose
from app.models import Category, Subcategory, Block, Card, FaqItem, StatusEnum
from app import db

# Базовый класс для всех наших админ-видов, чтобы задать общие настройки
class CustomModelView(ModelView):
    # Настройки для всех видов
    page_size = 20
    column_exclude_list = ['created_at', 'updated_at'] # Скрываем системные поля

# Класс для управления Категориями
class CategoryAdminView(CustomModelView):
    # Отображаемые колонки в списке
    column_list = ['position', 'title_ru', 'title_en', 'slug', 'status']
    # Колонки, по которым можно делать поиск
    column_searchable_list = ['title_ru', 'title_en', 'slug']
    # Колонки, по которым можно делать фильтрацию
    column_filters = ['status']
    # Поля, которые отображаются в форме создания/редактирования
    form_columns = ['title_ru', 'title_en', 'slug', 'status', 'position']
    # Кастомные метки для полей
    form_args = {
        'title_ru': {'label': 'Название (RU)'},
        'title_en': {'label': 'Название (EN)'},
        'slug': {'label': 'URL (slug)'},
        'status': {'label': 'Статус'},
        'position': {'label': 'Позиция'}
    }
    # Разрешить сортировку по позиции
    column_sortable_list = ['position']

# Класс для управления Подкатегориями
class SubcategoryAdminView(CustomModelView):
    column_list = ['position', 'category', 'title_ru', 'title_en', 'slug', 'status']
    column_searchable_list = ['title_ru', 'title_en', 'slug']
    column_filters = ['status', 'category']
    form_columns = ['category', 'title_ru', 'title_en', 'slug', 'status', 'position']
    form_args = {
        'category': {'label': 'Родительская категория'},
        'title_ru': {'label': 'Название (RU)'},
        'title_en': {'label': 'Название (EN)'},
        'slug': {'label': 'URL (slug)'},
        'status': {'label': 'Статус'},
        'position': {'label': 'Позиция'}
    }
    column_sortable_list = ['position']

# Класс для управления Блоками
class BlockAdminView(CustomModelView):
    column_list = ['position', 'name', 'category', 'subcategory', 'status']
    column_filters = ['status', 'category', 'subcategory']
    # Валидация, чтобы можно было выбрать только категорию или подкатегорию, не оба
    form_columns = ['name', 'category', 'subcategory', 'status', 'position']
    form_ajax_refs = {
        'category': {
            'fields': ('title_ru', 'slug'),
            'placeholder': 'Начните вводить для поиска категории...',
            'page_size': 10,
        },
        'subcategory': {
            'fields': ('title_ru', 'slug'),
            'placeholder': 'Начните вводить для поиска подкатегории...',
            'page_size': 10,
        }
    }
    form_args = {
        'name': {'label': 'Служебное имя блока'},
        'category': {'label': 'Привязка к категории'},
        'subcategory': {'label': 'Привязка к подкатегории'},
        'status': {'label': 'Статус'},
        'position': {'label': 'Позиция'}
    }
    column_sortable_list = ['position']

# Класс для управления Карточками
class CardAdminView(CustomModelView):
    column_list = [
        'card_index', 'block', 'title_ru', 'subtitle_ru',
        'media_type', 'status'
    ]
    column_filters = ['status', 'media_type', 'block']
    form_columns = [
        'block', 'card_index', 'title_ru', 'title_en', 'subtitle_ru', 'subtitle_en',
        'link_url', 'open_in_new_tab', 'media_type', 'image_path',
        'animation_mode', 'animation_payload', 'animation_file_path',
        'alt_ru', 'alt_en', 'status', 'position'
    ]
    # Тут можно добавить много кастомных меток для всех полей
    form_args = {
        'block': {'label': 'Родительский блок'},
        'card_index': {'label': 'Индекс (0 - большая)'},
        'title_ru': {'label': 'Заголовок (RU)'},
        'title_en': {'label': 'Заголовок (EN)'},
        'subtitle_ru': {'label': 'Подзаголовок (RU)'},
        'subtitle_en': {'label': 'Подзаголовок (EN)'},
    }
    column_sortable_list = ['card_index', 'position']

# Класс для управления FAQ
class FaqItemAdminView(CustomModelView):
    column_list = ['position', 'question_ru', 'category', 'subcategory', 'status']
    column_searchable_list = ['question_ru', 'answer_ru']
    column_filters = ['status', 'category', 'subcategory']
    form_columns = [
        'category', 'subcategory', 'title_ru', 'title_en', 'subtitle_ru', 'subtitle_en',
        'question_ru', 'question_en', 'answer_ru', 'answer_en', 'status', 'position'
    ]
    form_ajax_refs = {
        'category': {
            'fields': ('title_ru', 'slug'),
            'placeholder': 'Начните вводить для поиска категории...',
            'page_size': 10,
        },
        'subcategory': {
            'fields': ('title_ru', 'slug'),
            'placeholder': 'Начните вводить для поиска подкатегории...',
            'page_size': 10,
        }
    }
    form_args = {
        'category': {'label': 'Привязка к категории'},
        'subcategory': {'label': 'Привязка к подкатегории'},
        'question_ru': {'label': 'Вопрос (RU)'},
        'answer_ru': {'label': 'Ответ (RU)'},
    }
    column_sortable_list = ['position']

# Инициализация админ-панели
def init_admin(app):
    admin = Admin(app, name='CMS', template_mode='bootstrap4', url='/admin')

    # Добавляем все виды в админку
    admin.add_view(CategoryAdminView(Category, db.session, name='Категории', category='Контент'))
    admin.add_view(SubcategoryAdminView(Subcategory, db.session, name='Подкатегории', category='Контент'))
    admin.add_view(BlockAdminView(Block, db.session, name='Блоки', category='Контент'))
    admin.add_view(CardAdminView(Card, db.session, name='Карточки', category='Контент'))
    admin.add_view(FaqItemAdminView(FaqItem, db.session, name='Вопросы-Ответы', category='Контент'))
