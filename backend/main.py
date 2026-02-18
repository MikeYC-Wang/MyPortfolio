import os
import shutil
import uuid
import datetime
from dotenv import load_dotenv # 載入環境變數
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from passlib.context import CryptContext # 密碼加密
from jose import JWTError, jwt # JWT Token

# ==========================================
# 0. 環境變數與安全設定
# ==========================================
# 載入 .env 檔案
load_dotenv()

# 從環境變數讀取設定，若讀取不到則使用預設值 (建議正式環境務必設定 .env)
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key_change_me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 密碼加密設定
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

# ==========================================
# 1. 資料庫連線設定
# ==========================================
# 從環境變數讀取資料庫連線字串
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Day25143@localhost:5432/portfolio_db")

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

# 管理員帳號表
class AdminModel(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

# 登入嘗試紀錄表 (Log)
class LoginLogModel(Base):
    __tablename__ = "login_logs"
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String)
    username_attempt = Column(String)
    is_success = Column(Boolean)
    attempt_time = Column(TIMESTAMP, server_default=func.now())

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

# Token 回傳模型
class Token(BaseModel):
    access_token: str
    token_type: str

# ==========================================
# 4. FastAPI 主程式與工具函式
# ==========================================
app = FastAPI()

# 自動建表
Base.metadata.create_all(bind=engine)

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

# --- 密碼與 Token 工具 ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- 啟動事件：從 .env 建立管理員 ---
@app.on_event("startup")
def create_admin_from_env():
    db = SessionLocal()
    
    # 從環境變數讀取帳號密碼
    env_user = os.getenv("ADMIN_USER")
    env_pass = os.getenv("ADMIN_PASSWORD")

    # 如果 .env 沒設定，則不執行建立動作
    if not env_user or not env_pass:
        print("Warning: ADMIN_USER or ADMIN_PASSWORD not set in .env file. Skipping admin creation.")
        db.close()
        return

    # 檢查該帳號是否已存在
    admin = db.query(AdminModel).filter(AdminModel.username == env_user).first()
    
    if not admin:
        print(f"Creating admin account from .env: {env_user}")
        hashed_pwd = get_password_hash(env_pass)
        new_admin = AdminModel(username=env_user, hashed_password=hashed_pwd)
        db.add(new_admin)
        db.commit()
    
    db.close()

# ==========================================
# 5. API 路由
# ==========================================

@app.get("/")
def read_root():
    return {"message": "Portfolio API V3.0 Running"}

# --- 登入 API ---
@app.post("/api/login", response_model=Token)
def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 1. 取得 Client IP
    client_ip = request.client.host
    
    # 2. 檢查過去 10 分鐘內的失敗次數
    ten_mins_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=10)
    failed_attempts = db.query(LoginLogModel).filter(
        LoginLogModel.ip_address == client_ip,
        LoginLogModel.is_success == False,
        LoginLogModel.attempt_time >= ten_mins_ago
    ).count()

    if failed_attempts >= 3:
        # 紀錄這次被阻擋的嘗試
        log = LoginLogModel(ip_address=client_ip, username_attempt=form_data.username, is_success=False)
        db.add(log)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many failed attempts ({failed_attempts + 1}). Please try again later.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. 驗證帳號密碼
    admin = db.query(AdminModel).filter(AdminModel.username == form_data.username).first()
    
    if not admin or not verify_password(form_data.password, admin.hashed_password):
        # 登入失敗 -> 寫入 Log
        log = LoginLogModel(ip_address=client_ip, username_attempt=form_data.username, is_success=False)
        db.add(log)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 4. 登入成功 -> 寫入 Log
    log = LoginLogModel(ip_address=client_ip, username_attempt=form_data.username, is_success=True)
    db.add(log)
    db.commit()

    # 5. 發放 Token
    access_token = create_access_token(data={"sub": admin.username})
    return {"access_token": access_token, "token_type": "bearer"}

# --- 圖片上傳 ---
@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    file_ext = file.filename.split(".")[-1]
    file_name = f"{uuid.uuid4()}.{file_ext}"
    file_path = f"{UPLOAD_DIR}/{file_name}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"url": f"/static/uploads/{file_name}"}

# --- 其他 CRUD API ---

@app.get("/api/projects", response_model=List[ProjectSchema])
def get_projects(db: Session = Depends(get_db)):
    return db.query(ProjectModel).all()

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

@app.get("/api/skills", response_model=List[SkillSchema])
def get_skills(db: Session = Depends(get_db)):
    return db.query(SkillModel).order_by(SkillModel.skill_order).all()

@app.get("/api/posts", response_model=List[PostSchema])
def get_posts(db: Session = Depends(get_db)):
    return db.query(PostModel).order_by(PostModel.id.desc()).all()

@app.get("/api/posts/{post_id}", response_model=PostSchema)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(PostModel).filter(PostModel.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.post("/api/posts", response_model=PostSchema)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    db_post = PostModel(**post.dict())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@app.put("/api/posts/{post_id}", response_model=PostSchema)
def update_post(post_id: int, post: PostUpdate, db: Session = Depends(get_db)):
    db_post = db.query(PostModel).filter(PostModel.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    db_post.title = post.title
    db_post.content = post.content
    db_post.cover_image = post.cover_image
    db_post.is_published = post.is_published
    db.commit()
    db.refresh(db_post)
    return db_post

@app.delete("/api/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    db_post = db.query(PostModel).filter(PostModel.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(db_post)
    db.commit()
    return {"message": "Deleted successfully"}