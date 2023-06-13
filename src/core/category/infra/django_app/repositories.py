# pylint: disable=no-member
from typing import List
from core.__seedwork.domain.value_objects import UniqueEntityId
from core.category.domain.entities import Category
from core.category.domain.repositories import CategoryRepository
from core.category.infra.django_app.models import CategoryModel

class CategoryDjangoRepository(CategoryRepository):

    def insert(self, entity: Category) -> None:
        CategoryModel.objects.create(**entity.to_dict())

    def find_by_id(self, entity_id: str | UniqueEntityId) -> Category:
        raise NotImplementedError()

    def find_all(self) -> List[Category]:
        raise NotImplementedError()

    def update(self, entity: Category) -> None:
        raise NotImplementedError()

    def delete(self, entity_id: str | UniqueEntityId) -> None:
        raise NotImplementedError()
    
    def search(self, input_params: CategoryRepository.SearchParams) -> CategoryRepository.SearchResult:
        raise NotImplementedError()
    
