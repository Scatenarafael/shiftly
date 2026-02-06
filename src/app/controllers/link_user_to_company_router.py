from dataclasses import asdict

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from src.app.controllers.schemas.pydantic.user_schemas import CompaniesRolesFromUserResponse, UsersRolesFromCompanyResponse
from src.app.dependencies import get_user_company_roles_repository
from src.interfaces.iuser_company_roles_repository import IUserCompanyRolesRepository
from src.usecases.link_users_to_companies.assign_user_role_to_company_usecase import AssignUserRoleToCompanyUseCase
from src.usecases.link_users_to_companies.delete_user_role_to_company_usecase import DeleteUserRoleToCompanyUseCase
from src.usecases.link_users_to_companies.list_companies_roles_by_user_usecase import ListCompaniesAndRolesByUserUseCase
from src.usecases.link_users_to_companies.list_user_roles_by_company_usecase import ListUserAndRolesByCompanyUseCase

router = APIRouter(tags=["link"], prefix="/link")


def get_list_users_usecase(user_company_roles_repository: IUserCompanyRolesRepository = Depends(get_user_company_roles_repository)):
    return ListUserAndRolesByCompanyUseCase(user_company_roles_repository)


def get_list_companies_usecase(user_company_roles_repository: IUserCompanyRolesRepository = Depends(get_user_company_roles_repository)):
    return ListCompaniesAndRolesByUserUseCase(user_company_roles_repository)


def get_assign_user_role_to_company_usecase(user_company_roles_repository: IUserCompanyRolesRepository = Depends(get_user_company_roles_repository)):
    return AssignUserRoleToCompanyUseCase(user_company_roles_repository)


def get_delete_user_role_to_company_usecase(user_company_roles_repository: IUserCompanyRolesRepository = Depends(get_user_company_roles_repository)):
    return DeleteUserRoleToCompanyUseCase(user_company_roles_repository)


class LinkUserToCompanyRequest(BaseModel):
    user_id: str
    company_id: str
    role_id: str


@router.get("/by-company/{company_id}", response_model=list[UsersRolesFromCompanyResponse])
async def list_user_company_links_by_company(company_id: str, list_users_by_company_usecase: ListUserAndRolesByCompanyUseCase = Depends(get_list_users_usecase)):
    results = await list_users_by_company_usecase.execute(company_id)
    return [UsersRolesFromCompanyResponse(**asdict(item)) for item in results]


@router.get("/by-user/{user_id}", response_model=list[CompaniesRolesFromUserResponse])
async def list_user_company_links_by_user(user_id: str, list_users_by_company_usecase: ListCompaniesAndRolesByUserUseCase = Depends(get_list_companies_usecase)):
    results = await list_users_by_company_usecase.execute(user_id)
    return [CompaniesRolesFromUserResponse(**asdict(item)) for item in results]


@router.post("/user_to_company", status_code=status.HTTP_201_CREATED)
async def link_user_to_company(payload: LinkUserToCompanyRequest, assign_user_role_to_company_usecase: AssignUserRoleToCompanyUseCase = Depends(get_assign_user_role_to_company_usecase)):
    await assign_user_role_to_company_usecase.execute(payload.user_id, payload.company_id, payload.role_id)
    return None


@router.delete("/remove/{register_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user_company_links_by_user(register_id: str, delete_user_role_to_company_usecase: DeleteUserRoleToCompanyUseCase = Depends(get_delete_user_role_to_company_usecase)):
    await delete_user_role_to_company_usecase.execute(register_id)
    return None
