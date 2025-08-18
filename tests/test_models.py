import unittest
from app import create_app, db
from app.models import Category, Subcategory, Block, Card, FaqItem, StatusEnum
from tests.test_config import TestConfig
from sqlalchemy.exc import IntegrityError

class ModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_category_creation_and_slugification(self):
        c = Category(title_ru="Тестовая Категория")
        db.session.add(c)
        db.session.commit()
        self.assertEqual(c.slug, "testovaia-kategoriia")

    def test_block_parent_xor_constraint(self):
        # 1. Test with category_id only (should work)
        c = Category(title_ru="Cat")
        db.session.add(c)
        db.session.commit()
        b1 = Block(name="Block 1", category_id=c.id)
        db.session.add(b1)
        db.session.commit()
        self.assertIsNotNone(b1.id)

        # 2. Test with subcategory_id only (should work)
        sc = Subcategory(title_ru="Sub", category_id=c.id)
        db.session.add(sc)
        db.session.commit()
        b2 = Block(name="Block 2", subcategory_id=sc.id)
        db.session.add(b2)
        db.session.commit()
        self.assertIsNotNone(b2.id)

        # 3. Test with both category_id and subcategory_id (should fail)
        with self.assertRaises(IntegrityError):
            b3 = Block(name="Block 3", category_id=c.id, subcategory_id=sc.id)
            db.session.add(b3)
            db.session.commit()
        db.session.rollback()

        # 4. Test with neither (should fail)
        with self.assertRaises(IntegrityError):
            b4 = Block(name="Block 4")
            db.session.add(b4)
            db.session.commit()
        db.session.rollback()

    def test_faq_item_parent_xor_constraint(self):
        c = Category(title_ru="Cat")
        db.session.add(c)
        db.session.commit()

        # Test with category_id only (should work)
        faq1 = FaqItem(title_ru="T1", question_ru="Q1", answer_ru="A1", category_id=c.id)
        db.session.add(faq1)
        db.session.commit()
        self.assertIsNotNone(faq1.id)

        # Test with both (should fail)
        sc = Subcategory(title_ru="Sub", category_id=c.id)
        db.session.add(sc)
        db.session.commit()
        with self.assertRaises(IntegrityError):
            faq2 = FaqItem(question_ru="Q2", answer_ru="A2", category_id=c.id, subcategory_id=sc.id)
            db.session.add(faq2)
            db.session.commit()
        db.session.rollback()


if __name__ == '__main__':
    unittest.main()
