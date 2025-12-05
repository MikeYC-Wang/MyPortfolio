from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func

# ==========================================
# 1. 資料庫連線設定
# ==========================================
# ⚠️ 請再次確認密碼是否正確
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Day25143@localhost:5432/portfolio_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==========================================
# 2. 資料庫模型 (DB Models)
# ==========================================

# A. 專案 (首頁作品集用)
class ProjectModel(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    tech_stack = Column(String)

# B. 特效程式碼 (特效實驗室用)
class CodeSnippetModel(Base):
    __tablename__ = "code_snippets"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    html_code = Column(Text)
    css_code = Column(Text)
    js_code = Column(Text)
    is_published = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

# C. 部落格文章 (未來擴充用)
class PostModel(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(Text)
    cover_image = Column(String, nullable=True)
    is_published = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

# D. 技能 (雷達圖用 ✨)
class SkillModel(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, unique=True, index=True)
    score = Column(Integer)
    skill_order = Column(Integer, default=0)

# ==========================================
# 3. 傳輸模型 (Pydantic Schemas)
# ==========================================

# 專案 Schema
class ProjectSchema(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    tech_stack: Optional[str] = None
    class Config:
        from_attributes = True

# 特效新增用的 Schema
class CodeSnippetCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    html_code: Optional[str] = ""
    css_code: Optional[str] = ""
    js_code: Optional[str] = ""
    is_published: bool = True

# 特效讀取用的 Schema
class CodeSnippetSchema(CodeSnippetCreate):
    id: int
    created_at: Optional[object] = None
    class Config:
        from_attributes = True

# 文章 Schema
class PostSchema(BaseModel):
    id: int
    title: str
    content: Optional[str] = None
    cover_image: Optional[str] = None
    class Config:
        from_attributes = True

# 技能 Schema (雷達圖用 ✨)
class SkillSchema(BaseModel):
    category: str
    score: int
    class Config:
        from_attributes = True

# ==========================================
# 4. FastAPI 主程式與路由
# ==========================================
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "全端核心 V2.3 (含技能) 啟動成功！"}

# --- 專案 API ---
@app.get("/api/projects", response_model=List[ProjectSchema])
def get_projects(db: Session = Depends(get_db)):
    return db.query(ProjectModel).all()

# --- 特效程式碼 API ---
@app.get("/api/snippets", response_model=List[CodeSnippetSchema])
def get_snippets(db: Session = Depends(get_db)):
    return db.query(CodeSnippetModel).filter(CodeSnippetModel.is_published == True).order_by(CodeSnippetModel.id.desc()).all()

@app.post("/api/snippets", response_model=CodeSnippetSchema)
def create_snippet(snippet: CodeSnippetCreate, db: Session = Depends(get_db)):
    db_snippet = CodeSnippetModel(**snippet.dict())
    db.add(db_snippet)
    db.commit()
    db.refresh(db_snippet)
    return db_snippet

# --- 技能 API (新增 ✨) ---
@app.get("/api/skills", response_model=List[SkillSchema])
def get_skills(db: Session = Depends(get_db)):
    # 按照 skill_order 排序
    return db.query(SkillModel).order_by(SkillModel.skill_order).all()

# --- 文章 API (預留) ---
@app.get("/api/posts", response_model=List[PostSchema])
def get_posts(db: Session = Depends(get_db)):
    return db.query(PostModel).filter(PostModel.is_published == True).all()