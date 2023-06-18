from ast import mod
import unittest
import pytest
from django.utils import timezone
from model_bakery import baker
from core.category.application.dto import CategoryOutput, CategoryOutputMapper
from core.category.infra.django_app.mappers import CategoryModelMapper
from core.category.infra.django_app.models import CategoryModel
from core.__seedwork.domain.exceptions import NotFoundException
from core.category.application.use_cases import (
    CreateCategoryUseCase,
    DeleteCategoryUseCase,
    GetCategoryUseCase,
    ListCategoriesUseCase,
    UpdateCategoryUseCase
)
from core.category.infra.django_app.repositories import CategoryDjangoRepository

@pytest.mark.django_db
class TestCreateCategoryUseInt(unittest.TestCase):
    use_case: CreateCategoryUseCase
    repo: CategoryDjangoRepository

    def setUp(self) -> None:
        self.repo = CategoryDjangoRepository()
        self.use_case = CreateCategoryUseCase(self.repo)

    def test_execute(self):
        input_param = CreateCategoryUseCase.Input(name='Movie-1')
        output = self.use_case.execute(input_param)
        entity = self.repo.find_by_id(output.id)
        self.assertEqual(output, CreateCategoryUseCase.Output(
            id=entity.id,
            name='Movie-1',
            description=None,
            is_active=True,
            created_at=entity.created_at
        ))
        self.assertEqual(entity.name, 'Movie-1')
        self.assertIsNone(entity.description)
        self.assertTrue(entity.is_active)

        input_param = CreateCategoryUseCase.Input(name='Movie-2', description='Some description', is_active=False)
        output = self.use_case.execute(input_param)
        entity = self.repo.find_by_id(output.id)
        self.assertEqual(output, CreateCategoryUseCase.Output(
            id=entity.id,
            name='Movie-2',
            description='Some description',
            is_active=False,
            created_at=entity.created_at
        ))
        self.assertEqual(entity.name, 'Movie-2')
        self.assertEqual(entity.description, 'Some description')
        self.assertFalse(entity.is_active)

@pytest.mark.django_db
class TestGetCategoryUseInt(unittest.TestCase):
    use_case: GetCategoryUseCase
    repo: CategoryDjangoRepository

    def setUp(self) -> None:
        self.repo = CategoryDjangoRepository()
        self.use_case = GetCategoryUseCase(self.repo)

    def test_throws_exception_when_category_not_found(self):
        input_param = GetCategoryUseCase.Input('fake id')
        with self.assertRaises(NotFoundException) as assert_error:
            self.use_case.execute(input_param)
        self.assertEqual(
            assert_error.exception.args[0], "Entity not found using ID 'fake id'")

    def test_execute(self):
        model = baker.make(CategoryModel)
        input_param = GetCategoryUseCase.Input(model.id)
        output = self.use_case.execute(input_param)
        self.assertEqual(output, GetCategoryUseCase.Output(
            id=str(model.id),
            name=model.name,
            description=model.description,
            is_active=model.is_active,
            created_at=model.created_at
        ))

@pytest.mark.django_db
class TestListCategoriesUseCaseInt(unittest.TestCase):
    use_case: ListCategoriesUseCase
    repo: CategoryDjangoRepository

    def setUp(self) -> None:
        self.repo = CategoryDjangoRepository()
        self.use_case = ListCategoriesUseCase(self.repo)

    def test_execute_using_empty_search_params(self):
        models = [
            baker.make(CategoryModel, created_at=timezone.now()),
            baker.make(CategoryModel, created_at=timezone.now()),
        ]
        input_param = ListCategoriesUseCase.Input()
        output = self.use_case.execute(input_param)
        self.assertEqual(output, ListCategoriesUseCase.Output(
            items=[
                self.from_model_to_output(models[1]),
                self.from_model_to_output(models[0]),
            ],
            total=2,
            current_page=1,
            per_page=15,
            last_page=1
        ))

    def test_execute_using_pagination_and_sort_and_filter(self):
        models = [
            baker.make(CategoryModel, name='a'),
            baker.make(CategoryModel, name='AAA'),
            baker.make(CategoryModel, name='AaA'),
            baker.make(CategoryModel, name='b'),
            baker.make(CategoryModel, name='c'),
        ]
        input_param = ListCategoriesUseCase.Input(
            page=1,
            per_page=2,
            sort='name',
            sort_dir='asc',
            filter='a'
        )

        output = self.use_case.execute(input_param)
        self.assertEqual(output, ListCategoriesUseCase.Output(
            items=[
                self.from_model_to_output(models[1]),
                self.from_model_to_output(models[2]),
            ],
            total=3,
            current_page=1,
            per_page=2,
            last_page=2
        ))

        input_param = ListCategoriesUseCase.Input(
            page=2,
            per_page=2,
            sort='name',
            sort_dir='asc',
            filter='a'
        )

        output = self.use_case.execute(input_param)
        self.assertEqual(output, ListCategoriesUseCase.Output(
            items=[
                self.from_model_to_output(models[0]),
            ],
            total=3,
            current_page=2,
            per_page=2,
            last_page=2
        ))

        input_param = ListCategoriesUseCase.Input(
            page=2,
            per_page=2,
            sort='name',
            sort_dir='desc',
            filter='a'
        )

        output = self.use_case.execute(input_param)
        self.assertEqual(output, ListCategoriesUseCase.Output(
            items=[
                self.from_model_to_output(models[1]),
            ],
            total=3,
            current_page=2,
            per_page=2,
            last_page=2
        ))

    def from_model_to_output(self, model: CategoryModel) -> CategoryOutput:
        entity = CategoryModelMapper.to_entity(model)  
        return CategoryOutputMapper.without_child().to_output(entity)  

@pytest.mark.django_db
class TestUpdateCategoriesUseCaseInt(unittest.TestCase):
    use_case: UpdateCategoryUseCase
    repo: CategoryDjangoRepository

    def setUp(self) -> None:
        self.repo = CategoryDjangoRepository()
        self.use_case = UpdateCategoryUseCase(self.repo)

    def test_throw_exception_when_category_not_found(self):
        request = UpdateCategoryUseCase.Input(id='not_found', name='test')
        with self.assertRaises(NotFoundException) as assert_error:
            self.use_case.execute(request)
        self.assertEqual(assert_error.exception.args[0], "Entity not found using ID 'not_found'")

    def test_execute(self):
        model = baker.make(CategoryModel)
        request = UpdateCategoryUseCase.Input(
            id=model.id,
            name='test 1'
        )

        response = self.use_case.execute(request)
        self.assertEqual(response, UpdateCategoryUseCase.Output(
            id=str(model.id),
            name='test 1',
            description=None,
            is_active=True,
            created_at=model.created_at
        ))

        arrange = [
            {
                'input': {
                    'id': str(model.id),
                    'name': 'test 2',
                    'description': 'test description'
                },
                'expected': {
                    'id': str(model.id),
                    'name': 'test 2',
                    'description': 'test description',
                    'is_active': True,
                    'created_at': model.created_at
                },
            },
            {
                'input': {
                    'id': str(model.id),
                    'name': 'test',
                },
                'expected': {
                    'id': str(model.id),
                    'name': 'test',
                    'description': None,
                    'is_active': True,
                    'created_at': model.created_at
                },
            },
            {
                'input': {
                    'id': str(model.id),
                    'name': 'test 2',
                    'description': None,
                    'is_active': False
                },
                'expected': {
                    'id': str(model.id),
                    'name': 'test 2',
                    'description': None,
                    'is_active': False,
                    'created_at': model.created_at
                },
            }
        ]

        for i in arrange:
            input_param = i['input']
            expected = i['expected']
            request = UpdateCategoryUseCase.Input(**input_param)
            response = self.use_case.execute(request)
            self.assertEqual(
                response,
                UpdateCategoryUseCase.Output(**expected)
            )
            category = self.repo.find_by_id(expected['id'])
            # pylint: disable=expression-not-assigned
            self.assertEqual(category.name, expected['name']),
            self.assertEqual(category.description, expected['description']),
            self.assertEqual(category.is_active, expected['is_active']),
            self.assertEqual(category.created_at, expected['created_at']),


@pytest.mark.django_db
class TestDeleteCategoryUseCase(unittest.TestCase):

    use_case: DeleteCategoryUseCase
    repo: CategoryDjangoRepository

    def setUp(self) -> None:
        self.repo = CategoryDjangoRepository()
        self.use_case = DeleteCategoryUseCase(self.repo)

    def test_throw_exception_when_category_not_found(self):
        request = DeleteCategoryUseCase.Input(id='not_found')
        with self.assertRaises(NotFoundException) as assert_error:
            self.use_case.execute(request)
        self.assertEqual(
            assert_error.exception.args[0], "Entity not found using ID 'not_found'"
        )

    def test_execute(self):
        model = baker.make(CategoryModel)
        request = DeleteCategoryUseCase.Input(id=str(model.id))
        self.use_case.execute(request)
        with self.assertRaises(NotFoundException):
            self.repo.find_by_id(str(model.id))