import asyncio

from src.app.repositories.user_company_roles_repository import UserCompanyRolesRepository
from src.infra.settings.logging_config import app_logger


def test_list_users_and_roles_by_company():
    repository = UserCompanyRolesRepository()
    company_id = "4dfe1aa9-8be2-4a70-ab01-d67f3fa8d90e"

    users_roles = asyncio.run(repository.list_users_and_roles_by_company(company_id))

    assert users_roles is not None
    assert isinstance(users_roles, list)


def test_list_companies_and_roles_by_user():
    repository = UserCompanyRolesRepository()
    user_id = "43b6bc62-5a7b-4125-a9ce-80c3650233a5"

    users_roles = asyncio.run(repository.list_companies_and_roles_by_user(user_id))

    app_logger.info(f"[test_list_companies_and_roles_by_user] users_roles: {users_roles}")

    assert users_roles is not None
    assert isinstance(users_roles, list)
