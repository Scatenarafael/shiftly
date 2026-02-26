from datetime import datetime, timezone

import pytest

from src.domain.entities.company import Company
from src.domain.entities.user import User
from src.domain.entities.user_company_role import UserCompanyRole
from src.domain.entities.user_company_requests import UserCompanyRequestStatus, UserCompanyRequests
from src.domain.errors import AlreadyExistsError, PermissionDeniedError
from src.interfaces.types.user_types import CompaniesRolesFromUser, CompanyDTO
from src.usecases.user_company_requests.approve_user_company_request_usecase import ApproveUserCompanyRequestUseCase
from src.usecases.user_company_requests.create_user_company_request_usecase import CreateUserCompanyRequestUseCase


class FakeUsersRepo:
    def __init__(self, users: dict[str, User]):
        self.users = users

    async def get_by_id(self, id: str):
        return self.users.get(id)


class FakeCompaniesRepo:
    def __init__(self, companies: dict[str, Company]):
        self.companies = companies

    async def get_by_id(self, id: str):
        return self.companies.get(id)


class FakeUserCompanyRolesRepo:
    def __init__(self):
        self.links: dict[str, list[CompaniesRolesFromUser]] = {}

    async def list_companies_and_roles_by_user(self, user_id: str):
        return self.links.get(user_id, [])

    async def list_users_and_roles_by_company(self, company_id: str):
        return []

    async def assign_user_and_role_to_company(self, user_id: str, company_id: str, role_id: str | None):
        self.links.setdefault(user_id, []).append(CompaniesRolesFromUser(company=CompanyDTO(id=company_id, name=""), role=None))

    async def remove_user_company_role_register(self, register_id: str):
        return None


class FakeUserCompanyRequestsRepo:
    def __init__(self):
        self.requests: dict[str, UserCompanyRequests] = {}
        self.counter = 1

    async def create(self, user_id: str, company_id: str):
        request_id = str(self.counter)
        self.counter += 1
        request = UserCompanyRequests(
            id=request_id,
            user_id=user_id,
            company_id=company_id,
            status=UserCompanyRequestStatus.PENDING,
            accepted=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.requests[request_id] = request
        return request

    async def get_by_id(self, request_id: str):
        return self.requests.get(request_id)

    async def get_pending_by_user_and_company(self, user_id: str, company_id: str):
        for request in self.requests.values():
            if request.user_id == user_id and request.company_id == company_id and request.status == UserCompanyRequestStatus.PENDING:
                return request
        return None

    async def list_by_company(self, company_id: str, status: UserCompanyRequestStatus | None = None):
        return []

    async def approve(self, request_id: str, role_id: str | None):
        request = self.requests[request_id]
        request.status = UserCompanyRequestStatus.APPROVED
        request.accepted = True
        return request

    async def reject(self, request_id: str):
        request = self.requests[request_id]
        request.status = UserCompanyRequestStatus.REJECTED
        request.accepted = False
        return request


@pytest.mark.asyncio
async def test_create_company_request_success():
    users_repo = FakeUsersRepo(
        {
            "user-1": User(
                id="user-1",
                first_name="A",
                last_name="B",
                email="user@b.com",
                hashed_password="hashed",
                active=True,
                created_at=datetime.now(timezone.utc),
                companies_roles=[],
            )
        }
    )
    companies_repo = FakeCompaniesRepo({"company-1": Company(id="company-1", name="Company")})
    roles_repo = FakeUserCompanyRolesRepo()
    requests_repo = FakeUserCompanyRequestsRepo()

    usecase = CreateUserCompanyRequestUseCase(requests_repo, users_repo, companies_repo, roles_repo)
    result = await usecase.execute(user_id="user-1", company_id="company-1")

    assert result.status == UserCompanyRequestStatus.PENDING
    assert result.accepted is False


@pytest.mark.asyncio
async def test_create_company_request_duplicate_pending():
    users_repo = FakeUsersRepo(
        {
            "user-1": User(
                id="user-1",
                first_name="A",
                last_name="B",
                email="user@b.com",
                hashed_password="hashed",
                active=True,
                created_at=datetime.now(timezone.utc),
                companies_roles=[],
            )
        }
    )
    companies_repo = FakeCompaniesRepo({"company-1": Company(id="company-1", name="Company")})
    roles_repo = FakeUserCompanyRolesRepo()
    requests_repo = FakeUserCompanyRequestsRepo()

    usecase = CreateUserCompanyRequestUseCase(requests_repo, users_repo, companies_repo, roles_repo)
    await usecase.execute(user_id="user-1", company_id="company-1")

    with pytest.raises(AlreadyExistsError):
        await usecase.execute(user_id="user-1", company_id="company-1")


@pytest.mark.asyncio
async def test_approve_request_requires_owner():
    non_owner = User(
        id="owner-1",
        first_name="Owner",
        last_name="User",
        email="owner@b.com",
        hashed_password="hashed",
        active=True,
        created_at=datetime.now(timezone.utc),
        companies_roles=[],
    )
    users_repo = FakeUsersRepo({"owner-1": non_owner})
    roles_repo = FakeUserCompanyRolesRepo()
    requests_repo = FakeUserCompanyRequestsRepo()
    request = await requests_repo.create(user_id="user-2", company_id="company-1")

    usecase = ApproveUserCompanyRequestUseCase(requests_repo, users_repo, roles_repo)

    with pytest.raises(PermissionDeniedError):
        await usecase.execute(request_id=request.id, owner_id="owner-1")


@pytest.mark.asyncio
async def test_approve_request_success():
    owner = User(
        id="owner-1",
        first_name="Owner",
        last_name="User",
        email="owner@b.com",
        hashed_password="hashed",
        active=True,
        created_at=datetime.now(timezone.utc),
        companies_roles=[
            UserCompanyRole(
                id="ucr-1",
                user_id="owner-1",
                company_id="company-1",
                role_id=None,
                is_owner=True,
                company=None,
                role=None,
            )
        ],
    )
    users_repo = FakeUsersRepo({"owner-1": owner})
    roles_repo = FakeUserCompanyRolesRepo()
    requests_repo = FakeUserCompanyRequestsRepo()
    request = await requests_repo.create(user_id="user-2", company_id="company-1")

    usecase = ApproveUserCompanyRequestUseCase(requests_repo, users_repo, roles_repo)
    result = await usecase.execute(request_id=request.id, owner_id="owner-1")

    assert result.status == UserCompanyRequestStatus.APPROVED
    assert result.accepted is True
