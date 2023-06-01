import unittest
from rest_framework import serializers
from __seedwork.domain.validators import DRFValidator, StrictBooleanField, StrictCharField


class StubSerializer(serializers.Serializer):
    name = serializers.CharField()
    price = serializers.IntegerField()


class TestDRFValidatorIntegration(unittest.TestCase):
    def test_validation_whith_error(self):
        validator = DRFValidator()
        serializer = StubSerializer(data={})
        is_valid = validator.validate(serializer)
        self.assertFalse(is_valid)
        self.assertDictEqual(
            validator.errors,
            {
                'name': ['This field is required.'],
                'price': ['This field is required.']
            }
        )

    def test_validate_without_error(self):
        validator = DRFValidator()
        serializer = StubSerializer(data={
            'name': 'Test',
            'price': 5
        })
        is_valid = validator.validate(serializer)
        self.assertTrue(is_valid)
        self.assertDictEqual(
            validator.validated_date,
            {
                'name': 'Test',
                'price': 5
            }
        )


class TestStrictCharFieldUnit(unittest.TestCase):

    def test_if_is_invalid_when_not_str_values(self):
        class StubStrictCharfieldSerializer(serializers.Serializer):
            name = StrictCharField()

        serializer = StubStrictCharfieldSerializer(data={'name': 5})
        serializer.is_valid()
        self.assertEqual(serializer.errors, {
            'name': [serializers.ErrorDetail(string='Not a valid string.', code='invalid')]
        })

        serializer = StubStrictCharfieldSerializer(data={'name': True})
        serializer.is_valid()
        self.assertEqual(serializer.errors, {
            'name': [serializers.ErrorDetail(string='Not a valid string.', code='invalid')]
        })

    def test_none_value_is_valid(self):
        class StubStrictCharfieldSerializer(serializers.Serializer):
            name = StrictCharField(required=False, allow_null=True)

        serializer = StubStrictCharfieldSerializer(data={'name': None})
        self.assertTrue(serializer.is_valid())

    def test_is_valid(self):
        class StubStrictCharfieldSerializer(serializers.Serializer):
            name = StrictCharField(required=False, allow_null=True)

        serializer = StubStrictCharfieldSerializer(data={'name': 'some value'})
        self.assertTrue(serializer.is_valid())


class TestStrictBooleanFieldUnit(unittest.TestCase):

    def test_if_is_invalid_when_not_str_values(self):
        class StubStrictBooleanfieldSerializer(serializers.Serializer):
            active = StrictBooleanField()

        message_error = 'Must be a valid boolean.'
        serializer = StubStrictBooleanfieldSerializer(data={'active': 0})
        serializer.is_valid()
        self.assertEqual(serializer.errors, {
            'active': [serializers.ErrorDetail(string=message_error, code='invalid')]
        })

        serializer = StubStrictBooleanfieldSerializer(data={'active': 1})
        serializer.is_valid()
        self.assertEqual(serializer.errors, {
            'active': [serializers.ErrorDetail(string=message_error, code='invalid')]
        })

        serializer = StubStrictBooleanfieldSerializer(data={'active': 'False'})
        serializer.is_valid()
        self.assertEqual(serializer.errors, {
            'active': [serializers.ErrorDetail(string=message_error, code='invalid')]
        })

        serializer = StubStrictBooleanfieldSerializer(data={'active': 'True'})
        serializer.is_valid()
        self.assertEqual(serializer.errors, {
            'active': [serializers.ErrorDetail(string=message_error, code='invalid')]
        })

    def test_is_valid(self):
        class StubStrictBooleanfieldSerializer(serializers.Serializer):
            name = StrictBooleanField(allow_null=True)

        serializer = StubStrictBooleanfieldSerializer(data={'name': None})
        self.assertTrue(serializer.is_valid())

        serializer = StubStrictBooleanfieldSerializer(data={'name': True})
        self.assertTrue(serializer.is_valid())

        serializer = StubStrictBooleanfieldSerializer(data={'name': False})
        self.assertTrue(serializer.is_valid())
