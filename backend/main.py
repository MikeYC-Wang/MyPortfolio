import os
import shutil
import uuid
import datetime
import secrets
import psutil
import GPUtil
import requests
import random
from bs4 import BeautifulSoup
from dotenv import load_dotenv
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
from passlib.context import CryptContext
from jose import JWTError, jwt
from collections import Counter

# ==========================================
# 0. 環境變數與安全設定
# ==========================================
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key_change_me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

# ==========================================
# 1. 資料庫連線設定
# ==========================================
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
    content = Column(Text, nullable=True)

class CodeSnippetModel(Base):
    __tablename__ = "code_snippets"
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True, nullable=False) # 隨機別名
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

class AdminModel(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class LoginLogModel(Base):
    __tablename__ = "login_logs"
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String)
    username_attempt = Column(String)
    is_success = Column(Boolean)
    attempt_time = Column(TIMESTAMP, server_default=func.now())

class ApiLogModel(Base):
    __tablename__ = "api_logs"
    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, index=True)      # 請求的路徑 (例如 /api/projects)
    method = Column(String)                # 請求的方法 (GET, POST 等)
    client_ip = Column(String)             # 客戶端 IP
    timestamp = Column(TIMESTAMP, server_default=func.now()) # 發生時間

# ==========================================
# 3. 傳輸模型 (Pydantic Schemas)
# ==========================================

class ProjectSchema(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    tech_stack: Optional[str] = None
    content: Optional[str] = None
    class Config:
        from_attributes = True

class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None
    tech_stack: Optional[str] = None
    content: Optional[str] = None

class CodeSnippetCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    html_code: Optional[str] = ""
    css_code: Optional[str] = ""
    js_code: Optional[str] = ""
    is_published: bool = True

class CodeSnippetSchema(CodeSnippetCreate):
    id: int
    slug: str # 回傳時包含隨機別名
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

class Token(BaseModel):
    access_token: str
    token_type: str

# ==========================================
# 4. FastAPI 主程式與工具函式
# ==========================================
app = FastAPI()

Base.metadata.create_all(bind=engine)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://mikeyc-wang.github.io", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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

@app.on_event("startup")
def create_admin_from_env():
    db = SessionLocal()
    env_user = os.getenv("ADMIN_USER")
    env_pass = os.getenv("ADMIN_PASSWORD")

    if not env_user or not env_pass:
        print("Warning: ADMIN_USER or ADMIN_PASSWORD not set in .env file. Skipping admin creation.")
        db.close()
        return

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

@app.post("/api/login", response_model=Token)
def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    client_ip = request.client.host

    # 3 分鐘內失敗超過 3 次即鎖定 3 分鐘
    three_mins_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=3)
    failed_attempts = db.query(LoginLogModel).filter(
        LoginLogModel.ip_address == client_ip,
        LoginLogModel.is_success == False,
        LoginLogModel.attempt_time >= three_mins_ago
    ).count()

    if failed_attempts >= 3:
        # 紀錄這次被阻擋的嘗試
        log = LoginLogModel(ip_address=client_ip, username_attempt=form_data.username, is_success=False)
        db.add(log)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="密碼錯誤次數過多，請於 3 分鐘後再試。",
            headers={"WWW-Authenticate": "Bearer"},
        )

    admin = db.query(AdminModel).filter(AdminModel.username == form_data.username).first()
    if not admin or not verify_password(form_data.password, admin.hashed_password):
        log = LoginLogModel(ip_address=client_ip, username_attempt=form_data.username, is_success=False)
        db.add(log)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    log = LoginLogModel(ip_address=client_ip, username_attempt=form_data.username, is_success=True)
    db.add(log)
    db.commit()

    access_token = create_access_token(data={"sub": admin.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    file_ext = file.filename.split(".")[-1]
    file_name = f"{uuid.uuid4()}.{file_ext}"
    file_path = f"{UPLOAD_DIR}/{file_name}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"url": f"/static/uploads/{file_name}"}

# --- Projects ---
@app.get("/api/projects", response_model=List[ProjectSchema])
def get_projects(db: Session = Depends(get_db)):
    return db.query(ProjectModel).order_by(ProjectModel.id.asc()).all()

# --- Code Snippets (Playground) ---
@app.get("/api/snippets", response_model=List[CodeSnippetSchema])
def get_snippets(db: Session = Depends(get_db)):
    return db.query(CodeSnippetModel).filter(CodeSnippetModel.is_published == True).order_by(CodeSnippetModel.id.desc()).all()

@app.post("/api/snippets", response_model=CodeSnippetSchema)
def create_snippet(snippet: CodeSnippetCreate, db: Session = Depends(get_db)):
    # 產生 8 位元的隨機十六進位字串作為 slug
    random_slug = secrets.token_hex(4)
    db_snippet = CodeSnippetModel(**snippet.dict(), slug=random_slug)
    db.add(db_snippet)
    db.commit()
    db.refresh(db_snippet)
    return db_snippet

@app.get("/api/snippets/{slug}", response_model=CodeSnippetSchema)
def get_snippet(slug: str, db: Session = Depends(get_db)):
    snippet = db.query(CodeSnippetModel).filter(CodeSnippetModel.slug == slug).first()
    if not snippet:
        raise HTTPException(status_code=404, detail="作品不存在")
    return snippet

@app.put("/api/snippets/{slug}", response_model=CodeSnippetSchema)
def update_snippet(slug: str, snippet_data: CodeSnippetCreate, db: Session = Depends(get_db)):
    db_snippet = db.query(CodeSnippetModel).filter(CodeSnippetModel.slug == slug).first()
    if not db_snippet:
        raise HTTPException(status_code=404, detail="作品不存在")
    
    db_snippet.title = snippet_data.title
    db_snippet.description = snippet_data.description
    db_snippet.html_code = snippet_data.html_code
    db_snippet.css_code = snippet_data.css_code
    db_snippet.js_code = snippet_data.js_code
    db_snippet.is_published = snippet_data.is_published
    
    db.commit()
    db.refresh(db_snippet)
    return db_snippet

@app.delete("/api/snippets/{slug}")
def delete_snippet(slug: str, db: Session = Depends(get_db)):
    db_snippet = db.query(CodeSnippetModel).filter(CodeSnippetModel.slug == slug).first()
    if not db_snippet:
        raise HTTPException(status_code=404, detail="作品不存在")
    db.delete(db_snippet)
    db.commit()
    return {"message": "Snippet deleted successfully"}

# --- Skills (自動從專案的 tech_stack 統計) ---
@app.get("/api/skills", response_model=List[SkillSchema])
def get_skills(db: Session = Depends(get_db)):
    projects = db.query(ProjectModel.tech_stack).filter(ProjectModel.tech_stack.isnot(None)).all()
    
    tech_counter = Counter()
    
    for p in projects:
        if p.tech_stack:
            techs = [t.strip() for t in p.tech_stack.split(',') if t.strip()]
            tech_counter.update(techs)

    all_techs = tech_counter.most_common()
    
    result = [{"category": tech, "score": count} for tech, count in all_techs]
    
    return result

# --- Posts (Blog) ---
@app.get("/api/posts", response_model=List[PostSchema])
def get_posts(db: Session = Depends(get_db)):
    return db.query(PostModel).order_by(PostModel.id.asc()).all()

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

# --- 專案作品管理 API ---

# 1. 新增專案 (ORM 版)
@app.post("/api/projects")
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    db_project = ProjectModel(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return {"id": db_project.id, "message": "Project created"}

# 2. 更新專案 (ORM 版)
@app.put("/api/projects/{project_id}")
def update_project(project_id: int, project: ProjectCreate, db: Session = Depends(get_db)):
    db_project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db_project.title = project.title
    db_project.description = project.description
    db_project.tech_stack = project.tech_stack
    db_project.content = project.content
    
    db.commit()
    return {"message": "Project updated"}

# 3. 刪除專案 (ORM 版)
@app.delete("/api/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    db_project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(db_project)
    db.commit()
    
    return {"message": "Project deleted successfully"}

# 系統數據監控
@app.get("/api/system_status")
def get_system_status():
    gpu_usage = 0.0
    
    try:
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu_usage = round(gpus[0].load * 100, 1)
    except Exception as e:
        print(f"無法讀取 GPU 數據: {e}")

    return {
        "cpu": psutil.cpu_percent(interval=1),
        "ram": psutil.virtual_memory().percent,
        "gpu": gpu_usage
    }

# ==========================================
# GitHub 真實貢獻度抓取 API
# ==========================================
@app.get("/api/github_contributions")
def get_github_contributions():
    username = "MikeYC-Wang"
    url = f"https://github.com/users/{username}/contributions"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        data = []
        days = soup.find_all('td', class_='ContributionCalendar-day')
        
        for day in days:
            date = day.get('data-date')
            if not date:
                continue
            
            day_id = day.get('id')
            count = 0

            if day_id:
                tooltip = soup.find('tool-tip', {'for': day_id})
                if tooltip:
                    text = tooltip.text.strip()
                    if "No" in text or not text:
                        count = 0
                    else:
                        try:
                            count = int(text.split(' ')[0].replace(',', ''))
                        except ValueError:
                            count = 0
            
            data.append([date, count])
            
        return data
    except Exception as e:
        print(f"GitHub 抓取錯誤: {e}")
        return []

# ==========================================
# 系統圖表：API 每日呼叫次數統計
# ==========================================
@app.get("/api/stats/api-calls")
def get_api_calls_stats(db: Session = Depends(get_db)):
    today = datetime.datetime.now().date()
    seven_days_ago = today - datetime.timedelta(days=6)
    
    # 1. 預先建立過去 7 天的空字典
    stats = {}
    for i in range(6, -1, -1):
        target_date = (today - datetime.timedelta(days=i)).strftime("%m-%d")
        stats[target_date] = 0

    # 2. 從資料庫撈出過去 7 天的連線紀錄
    logs = db.query(ApiLogModel).filter(
        func.date(ApiLogModel.timestamp) >= seven_days_ago
    ).all()

    # 3. 將資料按日期分組累加
    for log in logs:
        if log.timestamp:
            log_date = log.timestamp.strftime("%m-%d")
            if log_date in stats:
                stats[log_date] += 1

    # 4. 轉換為前端 ECharts 需要的陣列格式
    data = [{"date": k, "count": v} for k, v in stats.items()]
    return data

# ==========================================
# 流量監控攔截器 (Middleware)
# ==========================================
@app.middleware("http")
async def log_api_requests(request: Request, call_next):
    # 先讓請求繼續往下走，拿到回應
    response = await call_next(request)
    
    # 我們只紀錄 /api/ 開頭的真實資料請求，排除靜態檔案或圖片下載，以免塞爆資料庫
    if request.url.path.startswith("/api/"):
        db = SessionLocal()
        try:
            log = ApiLogModel(
                path=request.url.path,
                method=request.method,
                client_ip=request.client.host
            )
            db.add(log)
            db.commit()
        except Exception as e:
            print(f"寫入 API 流量日誌失敗: {e}")
        finally:
            db.close()
            
    return response