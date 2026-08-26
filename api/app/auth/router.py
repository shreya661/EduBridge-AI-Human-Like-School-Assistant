# backend/app/auth/router.py
from fastapi import APIRouter, Depends, HTTPException, Response, Request, status, Query
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from ..session.models import Identity, Role
from ..session.store import identity_store
from ..session.session_manager import session_store
from ..session.dependencies import require_authenticated_identity
from ..domain import (
    student_repo, parent_repo, teacher_repo, class_repo,
    parent_student_repo, teacher_class_repo, school_domain_service
)
from ..domain.models import Student, Parent, Teacher, Class, ParentStudent, TeacherClass
from ..domain.database import SessionLocal
from ..domain.sql_models import SQLUser
from .security import (
    hash_password, verify_password, generate_role_id,
    validate_role_id_format, detect_role_from_id,
    ROLE_PREFIXES, ROLE_DISPLAY_NAMES
)


class LoginRequest(BaseModel):
    user_id: str
    password: Optional[str] = None


class SignUpRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Full name of user")
    role: str = Field(..., description="Role: STUDENT, TEACHER, PARENT, or PRINCIPAL")
    password: str = Field(..., min_length=6, description="Password (at least 6 characters)")
    user_id: Optional[str] = Field(None, description="Custom 10-char ID matching role format (auto-generated if omitted)")
    email: Optional[str] = None
    class_id: Optional[str] = "10-A"
    child_id: Optional[str] = None


class LoginResponse(BaseModel):
    success: bool = True
    user: Dict[str, Any]
    message: Optional[str] = None


class CurrentUserResponse(BaseModel):
    user: Dict[str, Any]


class GenerateIdResponse(BaseModel):
    user_id: str
    role: str
    prefix: str
    format_hint: str


router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


@router.get("/generate-id", response_model=GenerateIdResponse)
async def generate_id_endpoint(
    role: str = Query("STUDENT", description="Role: STUDENT, TEACHER, PARENT, PRINCIPAL")
) -> GenerateIdResponse:
    """Generate a unique valid 10-character mixed alphanumeric ID for the specified role."""
    try:
        role_enum = Role(role.upper())
    except ValueError:
        role_enum = Role.STUDENT

    generated_id = generate_role_id(role_enum)
    prefix = ROLE_PREFIXES.get(role_enum, "STU")
    
    return GenerateIdResponse(
        user_id=generated_id,
        role=role_enum.value.lower(),
        prefix=prefix,
        format_hint=f"10 characters: '{prefix}' followed by 7 alphanumeric characters (e.g. {generated_id})"
    )


@router.post("/signup", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
async def signup(response: Response, signup_req: SignUpRequest) -> LoginResponse:
    """
    Register a new user with 10-character alphanumeric ID and hashed password.
    """
    # 1. Parse and validate role
    try:
        role_enum = Role(signup_req.role.upper())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role '{signup_req.role}'. Allowed roles: STUDENT, TEACHER, PARENT, PRINCIPAL."
        )

    # 2. Determine and validate user_id
    if signup_req.user_id and signup_req.user_id.strip():
        user_id = signup_req.user_id.strip().upper()
        is_valid, err_msg = validate_role_id_format(user_id, role_enum)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=err_msg
            )
    else:
        user_id = generate_role_id(role_enum)

    # 3. Check for duplicates in SQLUser database
    if SessionLocal:
        try:
            with SessionLocal() as session:
                existing_user = session.query(SQLUser).filter(
                    SQLUser.user_id == user_id
                ).first()
                if existing_user:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"An account with ID '{user_id}' already exists. Please choose another ID or login."
                    )
        except HTTPException:
            raise
        except Exception:
            pass

    # 4. Hash password with secure salt
    password_hash, salt = hash_password(signup_req.password)

    # 5. Insert into SQLUser table
    if SessionLocal:
        try:
            with SessionLocal() as session:
                sql_user = SQLUser(
                    user_id=user_id,
                    name=signup_req.name.strip(),
                    email=signup_req.email.strip() if signup_req.email else None,
                    role=role_enum.value,
                    password_hash=password_hash,
                    salt=salt
                )
                session.merge(sql_user)
                session.commit()
        except Exception as exc:
            pass

    # 6. Create domain-level records for immediate application access
    try:
        class_target = signup_req.class_id or "10-A"
        if role_enum == Role.STUDENT:
            student_repo.create_student(Student(
                student_id=user_id,
                name=signup_req.name.strip(),
                class_id=class_target
            ))
        elif role_enum == Role.TEACHER:
            teacher_repo.create_teacher(Teacher(
                teacher_id=user_id,
                name=signup_req.name.strip(),
                subject="Academics"
            ))
            teacher_class_repo.create_relationship(TeacherClass(
                teacher_id=user_id,
                class_id=class_target
            ))
        elif role_enum == Role.PARENT:
            parent_repo.create_parent(Parent(
                parent_id=user_id,
                name=signup_req.name.strip(),
                email=signup_req.email
            ))
            if signup_req.child_id:
                parent_student_repo.create_relationship(ParentStudent(
                    parent_id=user_id,
                    student_id=signup_req.child_id.strip()
                ))
    except Exception:
        pass

    # 7. Create identity and establish session
    identity = Identity(
        user_id=user_id,
        role=role_enum,
        name=signup_req.name.strip(),
        student_id=user_id if role_enum == Role.STUDENT else None
    )
    identity_store.add_identity(identity)
    session_id = session_store.create_session(identity)

    # 8. Set HttpOnly cookie for session
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=3600
    )

    return LoginResponse(
        success=True,
        message=f"Successfully signed up as {role_enum.value.title()} with ID: {user_id}",
        user={
            "user_id": user_id,
            "role": role_enum.value.lower(),
            "name": signup_req.name.strip()
        }
    )


@router.post("/login", response_model=LoginResponse)
async def login(response: Response, login_request: LoginRequest, request: Request) -> LoginResponse:
    """
    Login endpoint - validates user_id and password with role awareness and brute-force protection.
    """
    from app.security.rate_limiter import login_limiter, get_client_ip

    user_id_clean = login_request.user_id.strip()
    client_ip = get_client_ip(request)
    limiter_key = f"{client_ip}:{user_id_clean.upper()}"

    # 1. Check if key is currently locked out
    is_locked, rem = login_limiter.is_locked_out(limiter_key)
    if is_locked:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Account temporarily locked due to multiple failed login attempts. Please try again in {rem} seconds.",
            headers={"Retry-After": str(rem)}
        )
    
    # 2. Database user verification
    db_user = None
    if SessionLocal:
        try:
            with SessionLocal() as session:
                db_user = session.query(SQLUser).filter(
                    (SQLUser.user_id == user_id_clean) | 
                    (SQLUser.user_id == user_id_clean.upper()) | 
                    (SQLUser.email == user_id_clean)
                ).first()
        except Exception:
            db_user = None

    if db_user:
        # Check password if provided
        if login_request.password:
            if not verify_password(login_request.password, db_user.salt, db_user.password_hash):
                login_limiter.check_and_record(limiter_key, lockout_on_breach=300)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid password. Please check your credentials."
                )
        elif not identity_store.get_identity(user_id_clean):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is required to log in."
            )
        
        try:
            role_enum = Role(db_user.role.upper())
        except ValueError:
            role_enum = Role.STUDENT

        identity = Identity(
            user_id=db_user.user_id,
            role=role_enum,
            name=db_user.name,
            student_id=db_user.user_id if role_enum == Role.STUDENT else None
        )
    else:
        # Fallback to development identity store for legacy dev IDs / tests
        identity = identity_store.get_identity(user_id_clean)
        if not identity:
            login_limiter.check_and_record(limiter_key, lockout_on_breach=300)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"User '{user_id_clean}' not found. Please sign up or check your 10-character ID."
            )

    # Reset failed attempts on successful login
    login_limiter.reset(limiter_key)

    # 3. Create secure session
    session_id = session_store.create_session(identity)
    
    # 4. Set HttpOnly cookie for session
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=3600
    )
    
    return LoginResponse(
        success=True,
        message=f"Logged in as {identity.name} ({identity.role.value})",
        user={
            "user_id": identity.user_id,
            "role": identity.role.value.lower(),
            "name": identity.name
        }
    )


@router.get("/me", response_model=CurrentUserResponse)
async def get_current_user(identity: Identity = Depends(require_authenticated_identity)) -> CurrentUserResponse:
    """Get current authenticated user info from session"""
    return CurrentUserResponse(
        user={
            "user_id": identity.user_id,
            "role": identity.role.value.lower(),
            "name": identity.name
        }
    )


@router.post("/logout")
async def logout(request: Request, response: Response) -> Dict[str, str]:
    """Logout endpoint - invalidates current session"""
    session_id = None
    
    session_header = request.headers.get("X-Session-ID")
    if session_header:
        session_id = session_header
    else:
        session_cookie = request.cookies.get("session_id")
        if session_cookie:
            session_id = session_cookie
    
    if not session_id:
        raise HTTPException(status_code=401, detail="No session provided")
    
    session_data = session_store.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    session_store.invalidate_session(session_id)
    response.delete_cookie("session_id")
    
    return {"message": "Logged out successfully"}
