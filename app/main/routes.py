from flask import render_template, redirect, url_for, current_app
from sqlalchemy.orm import joinedload
from app.main import bp
from app.models import Block, Category, Subcategory, StatusEnum

@bp.route('/<lang_code>/')
def index(lang_code):
    if lang_code not in current_app.config['SUPPORTED_LANGUAGES']:
        # Fallback to default language if the provided one is not supported
        return redirect(url_for('main.index', lang_code=current_app.config['DEFAULT_LANGUAGE']))

    # Query all published blocks and eager-load their cards
    blocks = Block.query.options(
        joinedload(Block.cards)
    ).filter_by(
        status=StatusEnum.published
    ).order_by(
        Block.position
    ).all()

    return render_template('index.html', blocks=blocks)


@bp.route('/<lang_code>/<category_slug>/')
def category(lang_code, category_slug):
    if lang_code not in current_app.config['SUPPORTED_LANGUAGES']:
        return redirect(url_for('main.category', lang_code=current_app.config['DEFAULT_LANGUAGE'], category_slug=category_slug))

    # Fetch the specific category and its content
    current_category = Category.query.filter_by(slug=category_slug, status=StatusEnum.published).first_or_404()

    # Fetch all categories for the navigation menu
    all_categories = Category.query.options(
        joinedload(Category.subcategories)
    ).filter_by(status=StatusEnum.published).order_by(Category.position).all()

    return render_template('category.html', category=current_category, all_categories=all_categories)

@bp.route('/<lang_code>/<category_slug>/<subcategory_slug>/')
def subcategory(lang_code, category_slug, subcategory_slug):
    if lang_code not in current_app.config['SUPPORTED_LANGUAGES']:
        return redirect(url_for('main.subcategory', lang_code=current_app.config['DEFAULT_LANGUAGE'], category_slug=category_slug, subcategory_slug=subcategory_slug))

    # Fetch the specific subcategory
    current_subcategory = Subcategory.query.join(Category).filter(
        Category.slug == category_slug,
        Subcategory.slug == subcategory_slug,
        Subcategory.status == StatusEnum.published
    ).first_or_404()

    # Fetch all categories for the navigation menu
    all_categories = Category.query.options(
        joinedload(Category.subcategories)
    ).filter_by(status=StatusEnum.published).order_by(Category.position).all()

    return render_template('subcategory.html', subcategory=current_subcategory, all_categories=all_categories)
