# pylint: disable=no-member
from os import name
import unittest
import datetime
import pytest
from django.utils import timezone
from model_bakery import baker
from model_bakery.recipe import seq
from core.category.domain.repositories import CategoryRepository
from core.__seedwork.domain.exceptions import NotFoundException
from core.__seedwork.domain.value_objects import UniqueEntityId
from core.category.domain.entities import Category
from core.category.infra.django_app.models import CategoryModel
from core.category.infra.django_app.repositories import CategoryDjangoRepository
from core.category.infra.django_app.mappers import CategoryModelMapper

@pytest.mark.django_db
class TestCategoryDjangoRepositoryInt(unittest.TestCase):
    
    repo: CategoryDjangoRepository

    def setUp(self):
        self.repo = CategoryDjangoRepository()

    def test_insert(self):
        category = Category(
            name='Movie'
        )
        self.repo.insert(category)
        
        model = CategoryModel.objects.get(pk=category.id)
        self.assertEqual(str(model.id), category.id)
        self.assertEqual(model.name, category.name)
        self.assertIsNone(model.description)
        self.assertTrue(model.is_active)
        self.assertEqual(model.created_at, category.created_at)
    
        category =  Category(
            name='Movie2',
            description='Movie description',
            is_active=False
        )

        self.repo.insert(category)
        model = CategoryModel.objects.get(pk=category.id)
        self.assertEqual(str(model.id), category.id)
        self.assertEqual(model.name, 'Movie2')
        self.assertEqual(model.description, 'Movie description')
        self.assertFalse(model.is_active)
        self.assertEqual(model.created_at, category.created_at)
    
    def test_throw_not_found_exception_in_find_by_id(self):
        with self.assertRaises(NotFoundException) as assert_error:
            self.repo.find_by_id('fake_id')
        self.assertEqual(
            assert_error.exception.args[0], "Entity not found using ID 'fake_id'")

        unique_entity_id = UniqueEntityId(
            '1593f488-63cf-4bac-aef6-50db3d47f3c0')

        with self.assertRaises(NotFoundException) as assert_error:
            self.repo.find_by_id(unique_entity_id)
        self.assertEqual(
            assert_error.exception.args[0], "Entity not found using ID '1593f488-63cf-4bac-aef6-50db3d47f3c0'")

    def test_find_by_id(self):

        category = Category(
            name='Movie'
        )
        self.repo.insert(category)

        category_found = self.repo.find_by_id(category.id)
        self.assertEqual(category_found, category)

        category_found = self.repo.find_by_id(category.unique_entity_id)
        self.assertEqual(category_found, category)

    def test_to_find_all(self):
        models = baker.make(CategoryModel, _quantity=2)
        categories = self.repo.find_all()

        print([vars(model) for model in CategoryModel.objects.all()])
        self.assertEqual(len(categories), 2)
        self.assertEqual(categories[0], CategoryModelMapper.to_entity(models[0]))
        self.assertEqual(categories[1], CategoryModelMapper.to_entity(models[1]))

    def test_throw_not_found_expception_in_update(self):
        entity = Category(name='Movie')
        with self.assertRaises(NotFoundException) as assert_error:
            self.repo.update(entity)
        self.assertEqual(
            assert_error.exception.args[0], f"Entity not found using ID '{entity.id}'")

    def test_update(self):
        category = Category(name='Movie')
        self.repo.insert(category)

        category.update(name='Movie changed', description='description changed')
        self.repo.update(category)

        model = CategoryModel.objects.get(pk=category.id)
        self.assertEqual(str(model.id), category.id)
        self.assertEqual(model.name, 'Movie changed')
        self.assertEqual(model.description, 'description changed')
        self.assertTrue(model.is_active)
        self.assertEqual(model.created_at, category.created_at)

    def test_throw_not_found_exception_in_delete(self):
        with self.assertRaises(NotFoundException) as assert_error:
            self.repo.delete('fake_id')
        self.assertEqual(
            assert_error.exception.args[0], "Entity not found using ID 'fake_id'")

        unique_entity_id = UniqueEntityId(
            '1593f488-63cf-4bac-aef6-50db3d47f3c0')

        with self.assertRaises(NotFoundException) as assert_error:
            self.repo.delete(unique_entity_id)
        self.assertEqual(
            assert_error.exception.args[0], "Entity not found using ID '1593f488-63cf-4bac-aef6-50db3d47f3c0'")

    def test_delete(self):
        category = Category(name='Movie')
        self.repo.insert(category)

        self.repo.delete(category.id)

        # try:
        #     self.repo.find_by_id(category.id)
        #     self.fail('The entity was not deleted')
        # except CategoryModel.DoesNotExist:
        #     self.assertTrue(True)

        with self.assertRaises(NotFoundException):
            self.repo.find_by_id(category.id)

        category = Category(name='Movie')
        self.repo.insert(category)

        self.repo.delete(category.unique_entity_id)
        
        with self.assertRaises(NotFoundException):
            self.repo.find_by_id(category.id)

    def test_search_when_params_is_empty(self):
        models = baker.make(
                CategoryModel,
                _quantity=16,
                created_at=seq(datetime.datetime.now(), datetime.timedelta(days=1))
            )
        models.reverse()

        search_result = self.repo.search(CategoryRepository.SearchParams())
        print(list(models))
        self.assertIsInstance(search_result, CategoryRepository.SearchResult)
        self.assertEqual(
            search_result,
            CategoryRepository.SearchResult(
                items=[
                    CategoryModelMapper.to_entity(model) for model in models[:15]
                ],
                total=16,
                current_page=1,
                per_page=15,
                sort=None,
                sort_dir=None,
                filter=None,
            ),
        )
    
    def test_search_applying_filter_and_paginate(self):
        default_props = {
            'description': None,
            'is_active': True,
            'created_at': timezone.now()
        }

        models = CategoryModel.objects.bulk_create([
            CategoryModel(
                id=UniqueEntityId().id,
                name='test',
                **default_props
            ),
            CategoryModel(
                id=UniqueEntityId().id,
                name='a',
                **default_props
            ),
            CategoryModel(
                id=UniqueEntityId().id,
                name='TEst',
                **default_props
            ),
        ])

        search_params = CategoryRepository.SearchParams(
            page=1,
            per_page=2,
            filter='E'
        )

        search_result = self.repo.search(search_params)
        self.assertEqual(search_result, CategoryRepository.SearchResult(
            items=[
                CategoryModelMapper.to_entity(models[0]),
                CategoryModelMapper.to_entity(models[2]),
            ],
            total=2,
            current_page=1,
            per_page=2,
            sort=None,
            filter='E'
        ))
    
    def test_search_applying_paginate_and_sort(self):
        default_props = {
            'description': None,
            'is_active': True,
            'created_at': timezone.now()
        }

        models = CategoryModel.objects.bulk_create([
            CategoryModel(
                id=UniqueEntityId().id,
                name='b',
                **default_props
            ),
            CategoryModel(
                id=UniqueEntityId().id,
                name='a',
                **default_props
            ),
            CategoryModel(
                id=UniqueEntityId().id,
                name='d',
                **default_props
            ),
            CategoryModel(
                id=UniqueEntityId().id,
                name='e',
                **default_props
            ),
            CategoryModel(
                id=UniqueEntityId().id,
                name='c',
                **default_props
            ),
        ])

        arrange_by_asc = [
            {
                'search_params': CategoryDjangoRepository.SearchParams(
                    per_page=2,
                    sort='name'
                ),
                'search_output': CategoryDjangoRepository.SearchResult(
                    items=[
                        CategoryModelMapper.to_entity(models[1]),
                        CategoryModelMapper.to_entity(models[0]),
                    ],
                    total=5,
                    current_page=1,
                    per_page=2,
                    sort='name',
                    sort_dir='asc',
                    filter=None
                ),
            },
            {
                'search_params': CategoryDjangoRepository.SearchParams(
                    page=2,
                    per_page=2,
                    sort='name'
                ),
                'search_output': CategoryDjangoRepository.SearchResult(
                    items=[
                        CategoryModelMapper.to_entity(models[4]),
                        CategoryModelMapper.to_entity(models[2]),
                    ],
                    total=5,
                    current_page=2,
                    per_page=2,
                    sort='name',
                    sort_dir='asc',
                    filter=None
                ),
            },        
        ]

        for index, item in enumerate(arrange_by_asc):
            search_output = self.repo.search(item['search_params'])
            self.assertEqual(
                search_output,
                item['search_output'],
                f"The output using sor_dir asc on index {index} is different"
            )

        
        arrange_by_desc = [
            {
                'search_params': CategoryDjangoRepository.SearchParams(
                    per_page=2,
                    sort='name',
                    sort_dir='desc'
                ),
                'search_output': CategoryDjangoRepository.SearchResult(
                    items=[
                        CategoryModelMapper.to_entity(models[3]),
                        CategoryModelMapper.to_entity(models[2]),
                    ],
                    total=5,
                    current_page=1,
                    per_page=2,
                    sort='name',
                    sort_dir='desc',
                    filter=None
                ),
            },
            {
                'search_params': CategoryDjangoRepository.SearchParams(
                    page=2,
                    per_page=2,
                    sort='name',
                    sort_dir='desc'
                ),
                'search_output': CategoryDjangoRepository.SearchResult(
                    items=[
                        CategoryModelMapper.to_entity(models[4]),
                        CategoryModelMapper.to_entity(models[0]),
                    ],
                    total=5,
                    current_page=2,
                    per_page=2,
                    sort='name',
                    sort_dir='desc',
                    filter=None
                ),
            },        
        ]

        for index, item in enumerate(arrange_by_desc):
            search_output = self.repo.search(item['search_params'])
            self.assertEqual(
                search_output,
                item['search_output'],
                f"The output using sor_dir desc on index {index} is different"
            )

    def test_search_applying_filter_sort_and_paginate(self):
        default_props = {
            'description': None,
            'is_active': True,
            'created_at': timezone.now()
        }

        models = CategoryModel.objects.bulk_create([
            CategoryModel(
                id=UniqueEntityId().id,
                name='test',
                **default_props
            ),
            CategoryModel(
                id=UniqueEntityId().id,
                name='a',
                **default_props
            ),
            CategoryModel(
                id=UniqueEntityId().id,
                name='TEST',
                **default_props
            ),
            CategoryModel(
                id=UniqueEntityId().id,
                name='e',
                **default_props
            ),
            CategoryModel(
                id=UniqueEntityId().id,
                name='TeSt',
                **default_props
            ),
        ])

        search_result = self.repo.search(CategoryRepository.SearchParams(
            page=1,
            per_page=2,
            sort='name',
            sort_dir='asc',
            filter='TEST'
        ))
        self.assertEqual(search_result, CategoryDjangoRepository.SearchResult(
            items=[
                CategoryModelMapper.to_entity(models[2]),
                CategoryModelMapper.to_entity(models[4]),
            ],
            total=3,
            current_page=1,
            per_page=2,
            sort='name',
            sort_dir='asc',
            filter='TEST'
        ))

        search_result = self.repo.search(CategoryRepository.SearchParams(
            page=2,
            per_page=2,
            sort='name',
            sort_dir='asc',
            filter='TEST'
        ))
        self.assertEqual(search_result, CategoryDjangoRepository.SearchResult(
            items=[
                CategoryModelMapper.to_entity(models[0]),
            ],
            total=3,
            current_page=2,
            per_page=2,
            sort='name',
            sort_dir='asc',
            filter='TEST'
        ))
