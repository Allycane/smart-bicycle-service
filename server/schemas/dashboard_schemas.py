from pydantic import BaseModel, ConfigDict, Field
from typing import Any, List, Optional


class DashboardUser(BaseModel):
    name: str
    level: str
    handle: str
    joined_days: int = Field(alias="joinedDays")
    streak: int

    model_config = ConfigDict(populate_by_name=True)


class DashboardActivity(BaseModel):
    badges: int
    challenges: int
    followers: int
    saved_routes: int = Field(alias="savedRoutes")

    model_config = ConfigDict(populate_by_name=True)


class DashboardStat(BaseModel):
    """StatCard.jsx 의 props({icon, label, value, unit, trend, valueClassName})와 1:1 대응"""
    icon: str
    label: str
    value: Any
    unit: Optional[str] = None
    trend: Optional[str] = None
    value_class_name: Optional[str] = Field(default=None, alias="valueClassName")

    model_config = ConfigDict(populate_by_name=True)


class DashboardRoute(BaseModel):
    id: Any
    name: str
    image: str
    distance: str
    duration: str


class DashboardQuickMenu(BaseModel):
    """menu.icon 은 lucide-react의 아이콘 export 이름과 정확히 일치해야 함 (Icons[menu.icon])"""
    label: str
    path: str
    icon: str


class DashboardCommunityFeed(BaseModel):
    initial: str
    name: str
    text: str
    time: str
    likes: int


class DashboardResponse(BaseModel):
    user: DashboardUser
    totals: List[DashboardStat]
    recommended_route: DashboardRoute = Field(alias="recommendedRoute")
    activity: DashboardActivity
    quick_menu: List[DashboardQuickMenu] = Field(alias="quickMenu")
    community_feed: List[DashboardCommunityFeed] = Field(alias="communityFeed")

    model_config = ConfigDict(populate_by_name=True)