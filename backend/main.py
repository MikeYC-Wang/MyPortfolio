import os
import shutil
import uuid
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func

# ==========================================
# 1. 資料庫連線設定
# ==========================================
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Day25143@localhost:5432/portfolio_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==========================================
# 2. 資料庫模型 (DB Models)
# ==========================================
class ProjectModel(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    tech_stack = Column(String)

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

class PostModel(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(Text)
    cover_image = Column(String, nullable=True)
    is_published = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

class SkillModel(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, unique=True, index=True)
    score = Column(Integer)
    skill_order = Column(Integer, default=0)

# ==========================================
# 3. 傳輸模型 (Pydantic Schemas)
# ==========================================
class ProjectSchema(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    tech_stack: Optional[str] = None
    class Config:
        from_attributes = True

class CodeSnippetCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    html_code: Optional[str] = ""
    css_code: Optional[str] = ""
    js_code: Optional[str] = ""
    is_published: bool = True

class CodeSnippetSchema(CodeSnippetCreate):
    id: int
    created_at: Optional[object] = None
    class Config:
        from_attributes = True

class PostSchema(BaseModel):
    id: int
    title: str
    content: Optional[str] = None
    cover_image: Optional[str] = None
    created_at: Optional[object] = None
    class Config:
        from_attributes = True

class PostCreate(BaseModel):
    title: str
    content: str
    cover_image: Optional[str] = None
    is_published: bool = True

class SkillSchema(BaseModel):
    category: str
    score: int
    class Config:
        from_attributes = True

# ==========================================
# 4. FastAPI 主程式與路由
# ==========================================
app = FastAPI()

# ✨ 設定圖片上傳資料夾
UPLOAD_DIR = "static/uploads"
# 如果資料夾不存在，就自動建立
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# ✨ 掛載靜態檔案路由 (這樣瀏覽器才能透過 /static/xxx 看到圖片)
app.mount("/static", StaticFiles(directory="static"), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "全端核心 V2.3 (含技能) 啟動成功！"}

# --- 圖片上傳 API (新增 ✨) ---
@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    # 1. 產生唯一的檔名 (避免檔名重複覆蓋)
    file_ext = file.filename.split(".")[-1]
    file_name = f"{uuid.uuid4()}.{file_ext}"
    file_path = f"{UPLOAD_DIR}/{file_name}"
    
    # 2. 將檔案存入硬碟
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 3. 回傳圖片的網址 (前端拿到這個網址後，存進 cover_image)
    return {"url": f"/static/uploads/{file_name}"}

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

# --- 技能 API ---
@app.get("/api/skills", response_model=List[SkillSchema])
def get_skills(db: Session = Depends(get_db)):
    return db.query(SkillModel).order_by(SkillModel.skill_order).all()

# --- 文章 API ---
@app.get("/api/posts", response_model=List[PostSchema])
def get_posts(db: Session = Depends(get_db)):
    return db.query(PostModel).filter(PostModel.is_published == True).all()

@app.get("/api/posts/{post_id}", response_model=PostSchema)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(PostModel).filter(PostModel.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    return post

@app.post("/api/posts", response_model=PostSchema)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    db_post = PostModel(**post.dict())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post