from fastapi import APIRouter, Depends, HTTPException, status, security, Response
from schemas.member_schemas import Member, MemberItem
from models.member_model import MemberModel
from sqlalchemy.orm import Session
from database.connection import get_db
# 입력된 패스워드를 암호화 하여 저장하도록 하는 라이브러리 추가 설치
from core.security import hash_password, verify_password, create_access_token, create_refresh_token

member_router = APIRouter()

REFRESH_COOKIE_NAME = "refreshToken"
REFRESH_COOKIE_MAX_AGE = 60 * 60 * 24 * 7 # 7일

# signin
@member_router.post('/signin')
async def signin(member_item:Member, db:Session = Depends(get_db)) -> dict:
    # db 연동 로직
    member_model = MemberModel(
        nickname = member_item.nickname,
        email = member_item.email,
        password = hash_password(member_item.password),
        riding_styles = member_item.riding_styles,
        agree_required = member_item.agree_required,
        agree_marketing = member_item.agree_marketing,
        role = member_item.role,
        created_id = member_item.created_id
    )

    db.add(member_model)
    db.commit()
    db.refresh(member_model)

    return {
        "message" : "회원가입에 성공하였습니다!!",
        "isSignup" : True
    }

@member_router.post('/login')
async def login(login_item:MemberItem, response: Response, db:Session = Depends(get_db)) -> dict:
    member_model = db.get(MemberModel, login_item.nickname)

    # 등록된 닉네임이 없을 경우, 로그인 거부
    if member_model is None:
        return {
            "isLogin" : False,
            "message" : '등록되지 않은 닉네임 입니다.'
        }

    # 비밀번호가 일치하는지에 대한 결과를 result 변수로 입력
    result = verify_password(login_item.password, member_model.password)

    # 비밀번호가 일치하지 않을 경우, 로그인 거부
    if not result:
        return {
            "isLogin" : False,
            "message" : '잘못된 비밀번호 입니다.'
        }

    # 비밀번호가 일치할 경우, 로그인 승인
    if result:
        access_token = create_access_token(member_model.nickname, member_model.role)
        refresh_token = create_refresh_token(member_model.nickname, member_model.role)

        response.set_cookie(
            key=REFRESH_COOKIE_NAME,
            value=refresh_token,
            httponly=True,
            secure=False,
            max_age=REFRESH_COOKIE_MAX_AGE
        )
    return {
        "message" : "로그인에 성공하였습니다!",
        "isLogin" : True,
        "role" : member_model.role,
        "accessToken" : access_token
    }

@member_router.post('/logout')
async def logout(response: Response) -> dict:
    response.delete_cookie(REFRESH_COOKIE_NAME)
    return {
        "isLogout" : True,
        "message" : "로그아웃이 완료되었습니다."
    }