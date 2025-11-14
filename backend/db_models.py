from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Table, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

# Association table for article tags
article_tags = Table('article_tags', Base.metadata,
    Column('article_id', Integer, ForeignKey('articles.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

# Association table for article categories
article_categories = Table('article_categories', Base.metadata,
    Column('article_id', Integer, ForeignKey('articles.id')),
    Column('category_id', Integer, ForeignKey('categories.id'))
)

# Association table for condition related conditions
condition_related = Table('condition_related', Base.metadata,
    Column('condition_id', Integer, ForeignKey('conditions.id')),
    Column('related_condition_id', Integer, ForeignKey('conditions.id'))
)

class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    credentials = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    image = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    articles = relationship("Article", back_populates="author")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    articles = relationship("Article", secondary=article_categories, back_populates="categories")

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    articles = relationship("Article", secondary=article_tags, back_populates="tags")

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    subtitle = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    image = Column(String, nullable=True)
    featured = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=True)
    author = relationship("Author", back_populates="articles")
    
    tags = relationship("Tag", secondary=article_tags, back_populates="articles")
    categories = relationship("Category", secondary=article_categories, back_populates="articles")
    
    published_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_date = Column(DateTime(timezone=True), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Condition(Base):
    __tablename__ = "conditions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    subtitle = Column(String, nullable=True)
    overview = Column(Text, nullable=False)
    symptoms = Column(Text, nullable=False)
    causes = Column(Text, nullable=False)
    diagnosis = Column(Text, nullable=False)
    treatments = Column(Text, nullable=False)
    prevention = Column(Text, nullable=False)
    complications = Column(Text, nullable=True)
    also_known_as = Column(String, nullable=True)
    specialties = Column(String, nullable=True)
    prevalence = Column(String, nullable=True)
    risk_factors = Column(Text, nullable=True)
    image = Column(String, nullable=True)
    
    related_conditions = relationship(
        "Condition",
        secondary=condition_related,
        primaryjoin=(condition_related.c.condition_id == id),
        secondaryjoin=(condition_related.c.related_condition_id == id),
        backref="related_to"
    )
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Drug(Base):
    __tablename__ = "drugs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    type = Column(String, nullable=True)
    generic_name = Column(String, nullable=True)
    brand_names = Column(String, nullable=True)  # Comma-separated list
    drug_class = Column(String, nullable=True)
    description = Column(Text, nullable=False)
    uses = Column(Text, nullable=False)
    side_effects = Column(Text, nullable=False)
    precautions = Column(Text, nullable=False)
    interactions = Column(Text, nullable=False)
    dosage = Column(Text, nullable=False)
    image = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class VideoConsultation(Base):
    __tablename__ = "video_consultations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    time = Column(String, nullable=False)
    reason = Column(Text, nullable=False)
    payment_status = Column(String, default="pending")
    consultation_link = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
