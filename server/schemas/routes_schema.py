from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional


class StationInfo(BaseModel):
    """FeaturedRouteCard.jsx / RouteCard.jsx 의 StationRow가 기대하는 형태"""
    name: str
    available: int
    total: int


class ElevationPoint(BaseModel):
    km: float
    elevation: float


class RouteOut(BaseModel):
    id: str
    name: str
    region: str
    region_tag: Optional[str] = Field(default=None, alias="regionTag")
    difficulty: Optional[str] = None
    bike_type: str = Field(alias="bikeType")

    distance: str
    duration: str

    rating: Optional[float] = None
    review_count: Optional[int] = Field(default=None, alias="reviewCount")

    image: str
    tags: List[str] = []
    free: Optional[bool] = None

    # 따릉이 루트만 값이 채워짐. 개인 루트는 None -> 프론트에서 typeof !== "object" 로 정상 분기됨.
    departure: Optional[StationInfo] = None
    destination: Optional[StationInfo] = None

    elevation_gain: Optional[str] = Field(default=None, alias="elevationGain")
    max_elevation: Optional[str] = Field(default=None, alias="maxElevation")
    completion_rate: Optional[int] = Field(default=None, alias="completionRate")
    participants: Optional[int] = None
    season: Optional[str] = None

    description: Optional[str] = None
    safety_tips: Optional[List[str]] = Field(default=None, alias="safetyTips")
    elevation_profile: Optional[List[ElevationPoint]] = Field(default=None, alias="elevationProfile")

    model_config = ConfigDict(populate_by_name=True)