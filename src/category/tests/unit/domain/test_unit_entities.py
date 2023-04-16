from dataclasses import FrozenInstanceError, is_dataclass
from datetime import datetime
import unittest
from category.domain.entities import Category


class TestCategory(unittest.TestCase):

    def test_if_is_a_dataclass(self):
        self.assertTrue(is_dataclass(Category))

    def test_constructor(self):
        category = Category(name='Movie')
        self.assertEqual(category.name, 'Movie')
        self.assertEqual(category.description, None)
        self.assertEqual(category.is_active, True)
        self.assertIsInstance(category.created_at, datetime)

        created_at = datetime.now()
        category = Category(
            name='Movie2',
            description='some description',
            is_active=True,
            created_at=created_at
        )
        self.assertEqual(category.name, 'Movie2')
        self.assertEqual(category.description, 'some description')
        self.assertEqual(category.is_active, True)
        self.assertIsInstance(category.created_at, datetime)

    def test_if_created_at_is_generated_in_constructor(self):

        category1 = Category(name='Movie 1')
        category2 = Category(name='Movie 2')
        self.assertNotEqual(
            category1.created_at.timestamp(),
            category2.created_at.timestamp()
        )

    def test_is_immutable(self):
        with self.assertRaises(FrozenInstanceError):
            value_object = Category(name='test')
            value_object.name = 'fake name'