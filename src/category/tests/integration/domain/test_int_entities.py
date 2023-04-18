import unittest
from __seedwork.domain.exceptions import ValidationException

from category.domain.entities import Category


class TestCategoryIntegration(unittest.TestCase):
    def test_create_with_invalid_cases_for_name_props(self):
        with self.assertRaises(ValidationException) as assert_error:
            Category(name=None)
        self.assertEqual(assert_error.exception.args[0], 'The name is required')

        with self.assertRaises(ValidationException) as assert_error:
            Category(name='')
        self.assertEqual(assert_error.exception.args[0], 'The name is required')

        with self.assertRaises(ValidationException) as assert_error:
            Category(name=5)
        self.assertEqual(assert_error.exception.args[0], 'The name must be a string')

        with self.assertRaises(ValidationException) as assert_error:
            Category(name="t" * 256)
        self.assertEqual(assert_error.exception.args[0], 'The name must be less than 255 characters')

    def test_create_with_invalid_cases_for_description_props(self):
        with self.assertRaises(ValidationException) as assert_error:
            Category(name='Movie', description=5)
        self.assertEqual(assert_error.exception.args[0], 'The description must be a string')

    
    def test_create_with_invalid_cases_for_active_props(self):
        with self.assertRaises(ValidationException) as assert_error:
            Category(name='Movie', is_active=5)
        self.assertEqual(assert_error.exception.args[0], 'The is_active must be a boolean')


    def test_create_with_valid_cases(self):

        try:
            Category(name="Movie")
            Category(name="Movie", description=None)
            Category(name="Movie", description="")
            Category(name="Movie", is_active=True)
            Category(name="Movie", is_active=False)
            Category(name="Movie", description="some description", is_active=False)
        except ValidationException as exception:
            self.fail(f'Some prop is not valid. Error: {exception.args[0]}')

    def test_update_with_invalid_cases_for_name_props(self):
        category = Category(name='Movie')
        with self.assertRaises(ValidationException) as assert_error:
            category.update(name=None, description=None)
        self.assertEqual(assert_error.exception.args[0], 'The name is required')

        with self.assertRaises(ValidationException) as assert_error:
            category.update(name='', description=None)
        self.assertEqual(assert_error.exception.args[0], 'The name is required')

        with self.assertRaises(ValidationException) as assert_error:
            category.update(name=5, description=None)
        self.assertEqual(assert_error.exception.args[0], 'The name must be a string')

        with self.assertRaises(ValidationException) as assert_error:
            category.update(name='t' * 256, description=None)
        self.assertEqual(assert_error.exception.args[0], 'The name must be less than 255 characters')

    def test_update_with_invalid_cases_for_description_props(self):
        category = Category(name='Movie')
        with self.assertRaises(ValidationException) as assert_error:
            category.update(name='Movie', description=5)
        self.assertEqual(assert_error.exception.args[0], 'The description must be a string')


    def test_update_with_valid_cases(self):
        category = Category(name="Movie")

        try:
            category.update(name="Movie1", description=None)
            category.update(name="Movie1", description="")
            category.update(name="Movie1", description="some description")
        except ValidationException as exception:
            self.fail(f'Some prop is not valid. Error: {exception.args[0]}')