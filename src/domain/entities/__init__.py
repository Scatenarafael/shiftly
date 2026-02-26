# This imports all model definitions, ensuring they are loaded.
from .company import Company
from .refresh_token import RefreshToken
from .role import Role
from .user import User
from .user_company_requests import UserCompanyRequests
from .user_company_role import UserCompanyRole
from .work_day import WorkDay
from .work_shift import WorkShift

# # src/domain/entities/__init__.py

# from src.domain.entities.company import Company
# from src.domain.entities.role import Role
# from src.domain.entities.user import User
# from src.domain.entities.user_company_role import UserCompanyRole
# from src.domain.entities.work_day import WorkDay
# from src.domain.entities.work_shift import WorkShift

# __all__ = [
#     "User",
#     "Company",
#     "Role",
#     "WorkDay",
#     "WorkShift",
#     "UserCompanyRole",
# ]
