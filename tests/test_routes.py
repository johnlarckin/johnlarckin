import unittest
from app import create_app, db
from app.models import Category, Subcategory, Block, Card, FaqItem, StatusEnum
from tests.test_config import TestConfig

class RouteTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        # Create some test data
        c1 = Category(title_ru="Дизайн", status=StatusEnum.published)
        sc1 = Subcategory(title_ru="Веб", category=c1, status=StatusEnum.published)
        b1 = Block(name="Тестовый блок", category=c1, status=StatusEnum.published)
        card1 = Card(title_ru="Карточка 1", block=b1, card_index=0, status=StatusEnum.published)
        db.session.add_all([c1, sc1, b1, card1])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get('/ru/')
        self.assertEqual(response.status_code, 200)
        response_text = response.data.decode('utf-8')
        # The block name is for admin only, we should see the card's title
        self.assertIn('Карточка 1', response_text)

    def test_category_page(self):
        response = self.client.get('/ru/dizain/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Дизайн', response.data.decode('utf-8'))

    def test_subcategory_page(self):
        response = self.client.get('/ru/dizain/veb/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Веб', response.data.decode('utf-8'))

    def test_language_redirect(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302) # Redirect
        self.assertTrue('/ru/' in response.location or '/en/' in response.location)

    def test_404_not_found(self):
        response = self.client.get('/ru/non-existent-category/')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
