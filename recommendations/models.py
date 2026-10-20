"""Data models for Scheme Recommendation and User Profile."""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class MatchStatus(str, Enum):
    LIKELY_MATCH = "LIKELY_MATCH"
    NEEDS_VERIFICATION = "NEEDS_VERIFICATION"
    DOES_NOT_MATCH = "DOES_NOT_MATCH"


class UserProfile(BaseModel):
    age: Optional[int] = Field(None, description="Age in years (0-120)")
    gender: Optional[str] = Field(None, description="Gender: female, male, transgender, or other")
    category: Optional[str] = Field(None, description="Social category: SC, ST, BC, MBC, DNC, General, etc.")
    annual_income: Optional[float] = Field(None, description="Annual family income in INR")
    occupation: Optional[str] = Field(None, description="Occupation: student, farmer, unemployed, etc.")
    education_level: Optional[str] = Field(None, description="Highest educational qualification")
    government_school: Optional[str] = Field("unknown", description="Studied in a government school: yes, no, or unknown")
    current_student_status: Optional[str] = Field("unknown", description="Currently enrolled as student: yes, no, or unknown")
    district: Optional[str] = Field(None, description="District or residence within Tamil Nadu")
    marital_status: Optional[str] = Field(None, description="Marital status: unmarried, married, widow, divorced, destitute")
    disability_status: Optional[str] = Field("unknown", description="Differently abled / disability status: yes, no, or unknown")
    farmer_status: Optional[str] = Field("unknown", description="Farmer or agricultural land-holding status: yes, no, or unknown")

    @field_validator("age")
    @classmethod
    def validate_age(cls, v: Optional[int]) -> Optional[int]:
        if v is not None:
            if v < 0 or v > 120:
                raise ValueError("Age must be between 0 and 120 years.")
        return v

    @field_validator("annual_income")
    @classmethod
    def validate_income(cls, v: Optional[float]) -> Optional[float]:
        if v is not None:
            if v < 0:
                raise ValueError("Annual family income cannot be negative.")
        return v

    @field_validator(
        "government_school",
        "current_student_status",
        "disability_status",
        "farmer_status",
        mode="before",
    )
    @classmethod
    def normalize_tri_state(cls, v: Optional[str]) -> str:
        if not v:
            return "unknown"
        norm = str(v).strip().lower()
        if norm in ("yes", "true", "y"):
            return "yes"
        if norm in ("no", "false", "n"):
            return "no"
        return "unknown"


class SchemeRecommendation(BaseModel):
    scheme_id: str
    scheme_name: str
    department: Optional[str] = None
    category: Optional[str] = None
    status: MatchStatus
    matched_conditions: List[str] = Field(default_factory=list)
    failed_conditions: List[str] = Field(default_factory=list)
    unknown_conditions: List[str] = Field(default_factory=list)
    eligibility: Optional[str] = None
    verification_level: Optional[str] = None
    official_source_url: Optional[str] = None
    score: int = 0


class RecommendationResponse(BaseModel):
    total_schemes_evaluated: int
    likely_matches_count: int
    needs_verification_count: int
    does_not_match_count: int
    recommendations: List[SchemeRecommendation]
