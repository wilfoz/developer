from django.urls import path

from django_app import container
from .api import CategoryResource


# class CategoryInMemoryRepositoryFactory:

#     repo: CategoryInMemoryRepository = None

#     @classmethod
#     def create(cls):
#         if not cls.repo:
#             cls.repo = CategoryInMemoryRepository()
#         return cls.repo


# class CreateCategoryUseCaseFactory:

#     @staticmethod
#     def create():
#         repo = CategoryInMemoryRepositoryFactory.create()
#         return CreateCategoryUseCase(repo)

def __init_category_resource():
    return {
        'create_use_case': container.use_case_category_create_category,
        'list_use_case': container.use_case_category_list_category,
        'get_use_case': container.use_case_category_get_category,
        'update_use_case': container.use_case_category_update_category,
        'delete_use_case': container.use_case_category_delete_category,
    }    


urlpatterns = [
    path('categories/', CategoryResource.as_view(
        **__init_category_resource()
    )),
    path('categories/<uuid:id>/', CategoryResource.as_view(
        **__init_category_resource()
    )),
]