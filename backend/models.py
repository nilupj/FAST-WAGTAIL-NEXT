from enum import Enum
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from datetime import datetime

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class ErrorResponse(BaseModel):
    message: str
    details: Optional[str] = None

# Article models
class ArticleAuthor(BaseModel):
    name: str
    credentials: Optional[str] = None
    bio: Optional[str] = None
    image: Optional[HttpUrl] = None

class ArticleCategory(BaseModel):
    name: str
    slug: str

class ArticleBase(BaseModel):
    title: str
    slug: str
    summary: Optional[str] = None
    subtitle: Optional[str] = None
    image: Optional[HttpUrl] = None

class ArticlePreview(ArticleBase):
    id: int
    category: Optional[str] = None
    created_at: datetime

class Article(ArticleBase):
    id: int
    content: str
    author: Optional[ArticleAuthor] = None
    published_date: datetime
    updated_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    category: Optional[ArticleCategory] = None

# Condition models
class RelatedCondition(BaseModel):
    name: str
    slug: str

class ConditionBase(BaseModel):
    name: str
    slug: str
    subtitle: Optional[str] = None

class ConditionPreview(ConditionBase):
    id: int

class Condition(ConditionBase):
    id: int
    overview: str
    symptoms: str
    causes: str
    diagnosis: str
    treatments: str
    prevention: str
    complications: Optional[str] = None
    related_conditions: Optional[List[RelatedCondition]] = None
    image: Optional[HttpUrl] = None
    also_known_as: Optional[str] = None
    specialties: Optional[str] = None
    prevalence: Optional[str] = None
    risk_factors: Optional[str] = None

# Drug models
class DrugPath(BaseModel):
    name: str
    slug: str
    type: Optional[str] = None  # e.g., "Medication", "Supplement", "Vitamin"

class DrugPreview(BaseModel):
    id: int
    description: Optional[str] = None
    image: Optional[HttpUrl] = None

class Drug(BaseModel):
    id: int
    description: str
    uses: str
    side_effects: str
    precautions: str
    interactions: str
    dosage: str
    image: Optional[HttpUrl] = None
    generic_name: Optional[str] = None
    brand_names: Optional[List[str]] = None
    drug_class: Optional[str] = None

# Symptom checker models
class SymptomRequest(BaseModel):
    age: int = Field(..., ge=1, le=120)
    gender: Gender
    symptoms: List[str] = Field(..., min_items=1)

class PossibleCondition(BaseModel):
    name: str
    description: str
    probability: float  # 0-100
    urgency: int  # 1-5, with 5 being most urgent

class SymptomResponse(BaseModel):
    conditions: List[PossibleCondition]
    disclaimer: str = "This assessment is for informational purposes only and does not constitute medical advice. Please consult with a healthcare professional for proper diagnosis and treatment."

class WellBeingResponse(BaseModel):
    featured: List[ArticlePreview]
    articles: List[ArticlePreview]