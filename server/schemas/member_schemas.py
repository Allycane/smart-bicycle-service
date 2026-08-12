from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import List
from datetime import datetime

class Member(BaseModel):
    nickname : str
    email : str

    password : str
    passwordConfirm : str

    riding_styles : list[str] = Field(
        alias="ridingStyles"
    )

    agree_required: bool = Field(
        alias="agreeRequired"
    )

    agree_marketing: bool = Field(
        alias="agreeMarketing"
    )

    role : str
    created_id : datetime

    @model_validator(mode="after")
    def validate_user(self):
        if len(self.password) < 8:
            raise ValueError(
                "비밀번호는 8자 이상이어야 합니다."
            )

        if self.password != self.passwordConfirm:
            raise ValueError(
                "비밀번호가 일치하지 않습니다."
            )

        if not self.agree_required:
            raise ValueError(
                "필수 약관에 동의해주세요."
            )
        
        return self

class MemberItem(BaseModel):
    nickname : str
    password : str

    model_config = ConfigDict(
        json_schema_extra={
            "examples" : [
                {
                    "nickname" : "hong",
                    "password" : "pw000000"
                }
            ]
        }
    )