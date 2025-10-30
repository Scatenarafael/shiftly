from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.app.repositories.user_company_roles_repository import UserCompanyRolesRepository
from src.usecases.link_users_to_companies.assign_user_role_to_company_usecase import AssignUserRoleToCompanyUseCase
from src.usecases.link_users_to_companies.delete_user_role_to_company_usecase import DeleteUserRoleToCompanyUseCase
from src.usecases.link_users_to_companies.list_companies_roles_by_user_usecase import ListCompaniesAndRolesByUserUseCase
from src.usecases.link_users_to_companies.list_user_roles_by_company_usecase import ListUserAndRolesByCompanyUseCase

router = APIRouter(tags=["link"], prefix="/link")


def get_list_users_usecase():
    return ListUserAndRolesByCompanyUseCase(UserCompanyRolesRepository())


def get_list_companies_usecase():
    return ListCompaniesAndRolesByUserUseCase(UserCompanyRolesRepository())


def get_assign_user_role_to_company_usecase():
    return AssignUserRoleToCompanyUseCase(UserCompanyRolesRepository())


def get_delete_user_role_to_company_usecase():
    return DeleteUserRoleToCompanyUseCase(UserCompanyRolesRepository())


class LinkUserToCompanyRequest(BaseModel):
    user_id: str
    company_id: str
    role_id: str


@router.get("/by-company/{company_id}")
async def list_user_company_links_by_company(company_id: str, list_users_by_company_usecase: ListUserAndRolesByCompanyUseCase = Depends(get_list_users_usecase)):
    return await list_users_by_company_usecase.execute(company_id)


@router.get("/by-user/{user_id}")
async def list_user_company_links_by_user(user_id: str, list_users_by_company_usecase: ListCompaniesAndRolesByUserUseCase = Depends(get_list_companies_usecase)):
    return await list_users_by_company_usecase.execute(user_id)


@router.post("/user_to_company")
async def link_user_to_company(payload: LinkUserToCompanyRequest, assign_user_role_to_company_usecase: AssignUserRoleToCompanyUseCase = Depends(get_assign_user_role_to_company_usecase)):
    await assign_user_role_to_company_usecase.execute(payload.user_id, payload.company_id, payload.role_id)


@router.delete("/remove/{register_id}")
async def remove_user_company_links_by_user(register_id: str, delete_user_role_to_company_usecase: DeleteUserRoleToCompanyUseCase = Depends(get_delete_user_role_to_company_usecase)):
    await delete_user_role_to_company_usecase.execute(register_id)
