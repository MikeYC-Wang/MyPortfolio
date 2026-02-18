import os
import shutil
import uuid
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
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

# ✨ 新增：更新文章用的 Schema (跟 Create 一樣，但為了語意清楚分開定義)
class PostUpdate(BaseModel):
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

# 允許跨域 (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "static/uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

app.mount("/static", StaticFiles(directory="static"), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "全端核心 V2.4 (管理升級版) 啟動成功！"}

# --- 圖片上傳 API ---
@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    file_ext = file.filename.split(".")[-1]
    file_name = f"{uuid.uuid4()}.{file_ext}"
    file_path = f"{UPLOAD_DIR}/{file_name}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
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

# --- 部落格文章 API (完整 CRUD) ---

# 1. 取得所有文章
@app.get("/api/posts", response_model=List[PostSchema])
def get_posts(db: Session = Depends(get_db)):
    # 這裡改成回傳「所有」文章(包含隱藏的)，方便後台管理，或者你可以另外寫一個 api/admin/posts
    # 為了簡單，目前先回傳全部，並依 ID 倒序排列 (新文章在前)
    return db.query(PostModel).order_by(PostModel.id.desc()).all()

# 2. 取得單篇文章
@app.get("/api/posts/{post_id}", response_model=PostSchema)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(PostModel).filter(PostModel.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    return post

# 3. 新增文章
@app.post("/api/posts", response_model=PostSchema)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    db_post = PostModel(**post.dict())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

# 4. ✨ 更新文章 (PUT)
@app.put("/api/posts/{post_id}", response_model=PostSchema)
def update_post(post_id: int, post: PostUpdate, db: Session = Depends(get_db)):
    db_post = db.query(PostModel).filter(PostModel.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    # 更新欄位
    db_post.title = post.title
    db_post.content = post.content
    db_post.cover_image = post.cover_image
    db_post.is_published = post.is_published
    
    db.commit()
    db.refresh(db_post)
    return db_post

# 5. ✨ 刪除文章 (DELETE)
@app.delete("/api/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    db_post = db.query(PostModel).filter(PostModel.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    db.delete(db_post)
    db.commit()
    return {"message": "刪除成功"}