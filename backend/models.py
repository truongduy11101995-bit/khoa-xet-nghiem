from typing import Optional, List
from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    username: str
    password: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class ScheduleAssignRequest(BaseModel):
    work_date: str
    shift: str = Field(..., pattern="^(sang|chieu|truc)$")
    position_id: int
    user_id: Optional[int] = None
    note: Optional[str] = None

class ScheduleBatchAssignRequest(BaseModel):
    assignments: List[ScheduleAssignRequest]

class LeaveCreateRequest(BaseModel):
    leave_date: str
    leave_type: str = Field(..., pattern="^(phep_nam|nghi_bu|di_hoc|viec_rieng)$")
    shift: str = Field(default="all", pattern="^(all|sang|chieu)$")
    reason: str

class LeaveReviewRequest(BaseModel):
    status: str = Field(..., pattern="^(approved|rejected)$")
    review_note: Optional[str] = None

class ProfileUpdateRequest(BaseModel):
    phone: Optional[str] = None
    email: Optional[str] = None
    dob: Optional[str] = None
    cchn: Optional[str] = None
    cchn_date: Optional[str] = None
    cchn_scope: Optional[str] = None
    education: Optional[str] = None
    specialty: Optional[str] = None
