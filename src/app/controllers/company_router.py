from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel

from src.app.controllers.schemas.pydantic.update_company_dto import PayloadUpdateCompanyDTO
from src.app.controllers.schemas.pydantic.user_schemas import CompanyResponse
from src.app.dependencies import get_companies_repository
from src.domain.errors import NotFoundError
from src.interfaces.icompanies_repository import ICompaniesRepository
from src.usecases.companies.create_company_usecase import CreateCompanyUseCase
from src.usecases.companies.delete_company_usecase import DeleteCompanyUseCase
from src.usecases.companies.list_companies_usecase import ListCompaniesUseCase
from src.usecases.companies.update_companies_usecase import UpdateCompaniesUsecase

router = APIRouter(tags=["companies"], prefix="/companies")


def get_create_company_usecase(companies_repository: ICompaniesRepository = Depends(get_companies_repository)):
    return CreateCompanyUseCase(companies_repository)


def get_list_company_usecase(companies_repository: ICompaniesRepository = Depends(get_companies_repository)):
    return ListCompaniesUseCase(companies_repository)


def get_update_company_usecase(companies_repository: ICompaniesRepository = Depends(get_companies_repository)):
    return UpdateCompaniesUsecase(companies_repository)


def get_delete_company_usecase(companies_repository: ICompaniesRepository = Depends(get_companies_repository)):
    return DeleteCompanyUseCase(companies_repository)


class CreateCompanyRequestBody(BaseModel):
    name: str


@router.get("", response_model=list[CompanyResponse])
async def list_companies(list_companies_usecase: ListCompaniesUseCase = Depends(get_list_company_usecase)):
    try:
        companies = await list_companies_usecase.execute()
        return [CompanyResponse(**asdict(company)) for company in companies]
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Could not list companies") from exc


@router.post("/create", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(request: Request, body: CreateCompanyRequestBody, create_company_usecase: CreateCompanyUseCase = Depends(get_create_company_usecase)):
    try:
        user_id = getattr(request.state, "user_id", None)
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access not provided")

        new_company = await create_company_usecase.execute(name=body.name, owner_id=user_id)
        return CompanyResponse(**asdict(new_company))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token is not valid") from exc


@router.patch("/{company_id}", response_model=CompanyResponse)
async def update_company(company_id: str, payload: PayloadUpdateCompanyDTO, update_companies_usecase: UpdateCompaniesUsecase = Depends(get_update_company_usecase)):
    try:
        company = await update_companies_usecase.execute(id=company_id, name=payload.name)
        if not company:
            raise NotFoundError("Company not found")
        return CompanyResponse(**asdict(company))
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(company_id: str, delete_company_usecase: DeleteCompanyUseCase = Depends(get_delete_company_usecase)):
    try:
        await delete_company_usecase.execute(company_id=company_id)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
