from dataclasses import FrozenInstanceError, is_dataclass
from datetime import datetime
import unittest
from unittest.mock import patch
from category.domain.entities import Category


class TestCategory(unittest.TestCase):

    def test_if_is_a_dataclass(self):
        self.assertTrue(is_dataclass(Category))

    def test_constructor(self):
        with patch.object(Category, 'validate') as mock_validate_method:
            category = Category(name='Movie')
            mock_validate_method.assert_called_once()
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
        with patch.object(Category, 'validate'):
            category1 = Category(name='Movie 1')
            category2 = Category(name='Movie 2')
            self.assertNotEqual(
                category1.created_at.timestamp(),
                category2.created_at.timestamp()
            )

    def test_is_immutable(self):
        with patch.object(Category, 'validate'):
            with self.assertRaises(FrozenInstanceError):
                value_object = Category(name='test')
                value_object.name = 'fake name'
    
    def test_update(self):
        with patch.object(Category, 'validate'):
            category = Category(name="Movie", description="Some description")
            category.update('Documentary', 'New description')
            self.assertEqual(category.name, 'Documentary')
            self.assertEqual(category.description, 'New description')
    
    def test_activate(self):
        with patch.object(Category, 'validate'):
            category = Category(name="Movie", is_active=False)
            category.activate()
            self.assertTrue(category.is_active)
    
    def test_deactivate(self):
        with patch.object(Category, 'validate'):
            category = Category(name="Movie")
            category.deactivate()
            self.assertFalse(category.is_active)
