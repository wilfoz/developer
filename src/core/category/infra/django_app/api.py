from dataclasses import asdict, dataclass
from typing import Callable
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework import status as http
from core.category.application.use_cases import (
    CreateCategoryUseCase,
    DeleteCategoryUseCase, 
    GetCategoryUseCase, 
    ListCategoriesUseCase, 
    UpdateCategoryUseCase
)


@dataclass(slots=True)
class CategoryResource(APIView):

    create_use_case: Callable[[], CreateCategoryUseCase]
    list_use_case: Callable[[], ListCategoriesUseCase]
    get_use_case: Callable[[], GetCategoryUseCase]
    update_use_case: Callable[[], UpdateCategoryUseCase]
    delete_use_case: Callable[[], DeleteCategoryUseCase]

    def post(self, request: Request):
        print(request.data)
        input_param = CreateCategoryUseCase.Input(**request.data)
        output = self.create_use_case().execute(input_param)
        return Response(asdict(output), status=http.HTTP_201_CREATED)
    
    def get(self, request: Request, id: str = None): # pylint: disable=redefined-builtin, invalid-name
        if id:
            return self.get_object(id)

        input_param = ListCategoriesUseCase.Input(**request.query_params.dict())
        output = self.list_use_case().execute(input_param)
        return Response(asdict(output))
    
    def get_object(self, id: str): # pylint: disable=redefined-builtin, invalid-name
        input_param = GetCategoryUseCase.Input(id)
        outuput = self.get_use_case().execute(input_param)
        return Response(asdict(outuput))
    
    def put(self, request: Request, id: str): # pylint: disable=redefined-builtin, invalid-name
        input_param = UpdateCategoryUseCase.Input(**{'id': id, **request.data})
        output = self.update_use_case().execute(input_param)
        return Response(asdict(output))

    def delete(self, _request: Request, id: str): # pylint: disable=redefined-builtin, invalid-name
        input_param = DeleteCategoryUseCase.Input(id)
        self.delete_use_case().execute(input_param)
        return Response(status=http.HTTP_204_NO_CONTENT)




# @api_view(['POST'])
# def hello_world(request: Request):
#     create_use_case = CreateCategoryUseCase(CategoryInMemoryRepository())
#     input_param = CreateCategoryUseCase.Input(request.data['name'])
#     output = create_use_case.execute(input_param)
#     return Response(asdict(output))