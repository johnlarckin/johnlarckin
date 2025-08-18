import enum
from datetime import datetime
from sqlalchemy import (Column, Integer, String, DateTime, Enum, ForeignKey, Text,
                        Boolean, CheckConstraint)
from sqlalchemy.orm import relationship, validates
from slugify import slugify
from app import db

class TimestampMixin:
    """Миксин для добавления полей created_at и updated_at."""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class StatusEnum(enum.Enum):
    draft = "draft"
    published = "published"
    archived = "archived"

class Category(TimestampMixin, db.Model):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    slug = Column(String(255), unique=True, nullable=False)
    title_ru = Column(String(255), nullable=False)
    title_en = Column(String(255), nullable=True)
    status = Column(Enum(StatusEnum), default=StatusEnum.draft, nullable=False)
    position = Column(Integer, default=0, nullable=False)

    subcategories = relationship('Subcategory', back_populates='category', cascade='all, delete-orphan')
    blocks = relationship('Block', back_populates='category', cascade='all, delete-orphan')
    faq_items = relationship('FaqItem', back_populates='category', cascade='all, delete-orphan')

    def __init__(self, *args, **kwargs):
        if 'title_ru' in kwargs and 'slug' not in kwargs:
            kwargs['slug'] = slugify(kwargs['title_ru'])
        super().__init__(*args, **kwargs)

    @validates('title_ru')
    def update_slug(self, key, title_ru):
        self.slug = slugify(title_ru)
        return title_ru

    def __repr__(self):
        return f'<Category {self.title_ru}>'

class Subcategory(TimestampMixin, db.Model):
    __tablename__ = 'subcategories'
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.id', ondelete='CASCADE'), nullable=False)
    slug = Column(String(255), nullable=False)
    title_ru = Column(String(255), nullable=False)
    title_en = Column(String(255), nullable=True)
    status = Column(Enum(StatusEnum), default=StatusEnum.draft, nullable=False)
    position = Column(Integer, default=0, nullable=False)

    category = relationship('Category', back_populates='subcategories')
    blocks = relationship('Block', back_populates='subcategory', cascade='all, delete-orphan')
    faq_items = relationship('FaqItem', back_populates='subcategory', cascade='all, delete-orphan')

    def __init__(self, *args, **kwargs):
        if 'title_ru' in kwargs and 'slug' not in kwargs:
            kwargs['slug'] = slugify(kwargs['title_ru'])
        super().__init__(*args, **kwargs)

    @validates('title_ru')
    def update_slug(self, key, title_ru):
        self.slug = slugify(title_ru)
        return title_ru

    def __repr__(self):
        return f'<Subcategory {self.title_ru}>'

class Block(TimestampMixin, db.Model):
    __tablename__ = 'blocks'
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    subcategory_id = Column(Integer, ForeignKey('subcategories.id'), nullable=True)
    name = Column(String(255), nullable=False) # Служебное имя
    position = Column(Integer, default=0, nullable=False)
    status = Column(Enum(StatusEnum), default=StatusEnum.draft, nullable=False)

    category = relationship('Category', back_populates='blocks')
    subcategory = relationship('Subcategory', back_populates='blocks')
    cards = relationship('Card', back_populates='block', cascade='all, delete-orphan', order_by='Card.card_index')

    __table_args__ = (
        CheckConstraint(
            '(category_id IS NOT NULL AND subcategory_id IS NULL) OR '
            '(category_id IS NULL AND subcategory_id IS NOT NULL)',
            name='chk_block_parent'
        ),
    )


    def __repr__(self):
        return f'<Block {self.name}>'

class CardMediaTypeEnum(enum.Enum):
    image = "image"
    animation = "animation"

class CardAnimationModeEnum(enum.Enum):
    css_snippet = "css_snippet"
    css_file = "css_file"
    json_config = "json_config"

class Card(TimestampMixin, db.Model):
    __tablename__ = 'cards'
    id = Column(Integer, primary_key=True)
    block_id = Column(Integer, ForeignKey('blocks.id', ondelete='CASCADE'), nullable=False)
    card_index = Column(Integer, nullable=False, default=0) # 0 - большая, 1-4 - малые

    title_ru = Column(String(255), nullable=False)
    title_en = Column(String(255), nullable=True)
    subtitle_ru = Column(Text, nullable=True)
    subtitle_en = Column(Text, nullable=True)

    link_url = Column(String(2048), nullable=True)
    open_in_new_tab = Column(Boolean, default=False, nullable=False)

    media_type = Column(Enum(CardMediaTypeEnum), default=CardMediaTypeEnum.image, nullable=False)
    image_path = Column(String(1024), nullable=True)

    animation_mode = Column(Enum(CardAnimationModeEnum), nullable=True)
    animation_payload = Column(Text, nullable=True)
    animation_file_path = Column(String(1024), nullable=True)

    alt_ru = Column(String(255), nullable=True)
    alt_en = Column(String(255), nullable=True)

    status = Column(Enum(StatusEnum), default=StatusEnum.draft, nullable=False)
    position = Column(Integer, default=0, nullable=False)

    block = relationship('Block', back_populates='cards')

    __table_args__ = (
        CheckConstraint('card_index >= 0 AND card_index <= 4', name='chk_card_index'),
    )

    def __repr__(self):
        return f'<Card {self.title_ru}>'

class FaqItem(TimestampMixin, db.Model):
    __tablename__ = 'faq_items'
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    subcategory_id = Column(Integer, ForeignKey('subcategories.id'), nullable=True)

    title_ru = Column(String(255), nullable=False)
    title_en = Column(String(255), nullable=True)
    subtitle_ru = Column(Text, nullable=True)
    subtitle_en = Column(Text, nullable=True)
    question_ru = Column(Text, nullable=False)
    question_en = Column(Text, nullable=True)
    answer_ru = Column(Text, nullable=False)
    answer_en = Column(Text, nullable=True)

    status = Column(Enum(StatusEnum), default=StatusEnum.draft, nullable=False)
    position = Column(Integer, default=0, nullable=False)

    category = relationship('Category', back_populates='faq_items')
    subcategory = relationship('Subcategory', back_populates='faq_items')

    __table_args__ = (
        CheckConstraint(
            '(category_id IS NOT NULL AND subcategory_id IS NULL) OR '
            '(category_id IS NULL AND subcategory_id IS NOT NULL)',
            name='chk_faq_item_parent'
        ),
    )

    def __repr__(self):
        return f'<FaqItem {self.question_ru}>'
