"""Run once after server starts: python seed.py"""
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.database import SessionLocal, create_tables
from app.models.user import User
from app.models.course import Course
from app.models.lesson import Lesson
import app.models

def seed():
    create_tables()
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.role == "admin").first()
        if not admin:
            print("❌ No admin found. Create admin via /docs first.")
            return
        if db.query(Course).first():
            print("⚠️  Already seeded. Delete learning_platform.db to reseed.")
            return
        print(f"✅ Using admin: {admin.name}")

        c1 = Course(title="Python for Beginners", description="Learn Python from absolute zero. Variables, loops, functions, and more. Perfect for complete beginners.", price=0.0, is_published=True, instructor_id=str(admin.id))
        db.add(c1); db.flush()
        for l in [
            (1,True,"Introduction to Python",10,"Welcome to Python!\n\nPython is one of the most popular programming languages. Used in web dev, data science, AI, and automation.\n\nInstalling Python:\n1. Go to python.org/downloads\n2. Download Python 3.x\n3. Tick 'Add Python to PATH'\n\nYour first program:\n    print('Hello, World!')\n\nRun it:\n    python hello.py\n\nCongratulations — you just wrote your first Python program!"),
            (2,True,"Variables and Data Types",15,"Variables are containers for storing data.\n\n    name = 'Abhijay'\n    age  = 20\n    gpa  = 9.2\n    is_student = True\n\nCore types:\n- str  → text: 'hello'\n- int  → whole number: 42\n- float → decimal: 9.99\n- bool  → True or False\n- None  → absence of value\n\nf-strings:\n    print(f'Hello {name}, you are {age} years old.')"),
            (3,False,"Control Flow — if, elif, else",20,"Make decisions in your code:\n\n    score = 85\n    if score >= 90:\n        print('A')\n    elif score >= 80:\n        print('B')\n    else:\n        print('C')\n\nComparison operators:\n    ==  !=  >  <  >=  <=\n\nLogical:\n    and  or  not\n\nExample:\n    if is_logged_in and is_verified:\n        print('Access granted')"),
            (4,False,"Loops — for and while",20,"Repeat code without writing it multiple times.\n\nfor loop:\n    for i in range(5):\n        print(i)  # 0 1 2 3 4\n\n    fruits = ['apple','banana','mango']\n    for fruit in fruits:\n        print(fruit)\n\nwhile loop:\n    count = 0\n    while count < 5:\n        print(count)\n        count += 1\n\nbreak → exit loop\ncontinue → skip to next"),
            (5,False,"Functions",25,"Reusable blocks of code:\n\n    def greet(name):\n        return f'Hello, {name}!'\n\n    print(greet('Abhijay'))\n\nDefault parameters:\n    def greet(name, greeting='Hello'):\n        return f'{greeting}, {name}!'\n\nMultiple returns:\n    def min_max(nums):\n        return min(nums), max(nums)\n\n    lo, hi = min_max([3,1,9,4])"),
        ]:
            db.add(Lesson(course_id=c1.id,order=l[0],is_free=l[1],title=l[2],duration_min=l[3],content=l[4]))

        c2 = Course(title="Web Development with FastAPI", description="Build production-ready REST APIs with FastAPI. Routing, Pydantic validation, SQLAlchemy ORM, JWT auth, and deployment.", price=999.0, is_published=True, instructor_id=str(admin.id))
        db.add(c2); db.flush()
        for l in [
            (1,True,"What is FastAPI?",12,"FastAPI is a modern Python web framework for building APIs.\n\n    pip install fastapi uvicorn\n\nYour first API:\n    from fastapi import FastAPI\n    app = FastAPI()\n\n    @app.get('/')\n    def hello():\n        return {'message': 'Hello World!'}\n\nRun:\n    uvicorn main:app --reload\n\nOpen http://localhost:8000/docs for interactive docs!"),
            (2,False,"Path params, query params, request body",20,"Path parameters:\n    @app.get('/users/{user_id}')\n    def get_user(user_id: int):\n        return {'id': user_id}\n\nQuery parameters:\n    @app.get('/courses')\n    def list_courses(skip: int=0, limit: int=10):\n        return {'skip': skip, 'limit': limit}\n\nRequest body:\n    from pydantic import BaseModel\n    class Course(BaseModel):\n        title: str\n        price: float = 0.0\n\n    @app.post('/courses')\n    def create(payload: Course):\n        return payload"),
            (3,False,"Pydantic v2 — Data validation",18,"Pydantic validates data automatically.\n\n    from pydantic import BaseModel, EmailStr, field_validator\n\n    class UserRegister(BaseModel):\n        name: str\n        email: EmailStr\n        password: str\n\n        @field_validator('password')\n        @classmethod\n        def check_strength(cls, v):\n            if len(v) < 8:\n                raise ValueError('Too short')\n            return v\n\nIf invalid → FastAPI returns 422 with field errors automatically."),
            (4,False,"SQLAlchemy ORM",25,"Work with databases using Python classes.\n\n    from sqlalchemy import create_engine, Column, String\n    from sqlalchemy.orm import declarative_base, sessionmaker\n\n    engine = create_engine('sqlite:///app.db')\n    Base   = declarative_base()\n\n    class User(Base):\n        __tablename__ = 'users'\n        id    = Column(String, primary_key=True)\n        name  = Column(String)\n        email = Column(String, unique=True)\n\n    # CRUD\n    db.add(user)\n    db.commit()\n    db.refresh(user)\n    user = db.query(User).filter(User.id==1).first()"),
            (5,False,"JWT Authentication",30,"JWT = JSON Web Token. Standard way to authenticate.\n\n    pip install python-jose passlib[bcrypt]\n\nHash passwords:\n    from passlib.context import CryptContext\n    pwd = CryptContext(schemes=['bcrypt'])\n    hashed = pwd.hash('mypassword')\n\nCreate token:\n    from jose import jwt\n    payload = {'sub': user_id, 'exp': expiry}\n    token = jwt.encode(payload, SECRET_KEY)\n\nProtect routes:\n    from fastapi.security import OAuth2PasswordBearer\n    oauth2 = OAuth2PasswordBearer(tokenUrl='/login')\n\n    @app.get('/me')\n    def me(token: str = Depends(oauth2)):\n        payload = jwt.decode(token, SECRET_KEY)\n        return payload"),
            (6,False,"Deploying FastAPI with Docker",22,"Dockerfile:\n    FROM python:3.11-slim\n    WORKDIR /app\n    COPY requirements.txt .\n    RUN pip install -r requirements.txt\n    COPY . .\n    EXPOSE 8000\n    CMD ['uvicorn', 'main:app', '--host', '0.0.0.0']\n\ndocker-compose.yml:\n    services:\n      api:\n        build: .\n        ports:\n          - '8000:8000'\n      db:\n        image: postgres:15\n        environment:\n          POSTGRES_PASSWORD: secret\n\nRun:\n    docker-compose up --build"),
        ]:
            db.add(Lesson(course_id=c2.id,order=l[0],is_free=l[1],title=l[2],duration_min=l[3],content=l[4]))

        c3 = Course(title="Introduction to AI & Machine Learning", description="Demystify AI and ML. Neural networks, your first ML model, LLMs, and prompt engineering.", price=1499.0, is_published=True, instructor_id=str(admin.id))
        db.add(c3); db.flush()
        for l in [
            (1,True,"What is Artificial Intelligence?",15,"AI is the simulation of human intelligence by machines.\n\nTypes:\n- Narrow AI  → one specific task (chess, image recognition)\n- General AI → human-level reasoning (not yet achieved)\n- Super AI   → surpasses humans (theoretical)\n\nAI vs ML vs Deep Learning:\n- AI            → broad field\n- Machine Learning → learns from data\n- Deep Learning    → uses neural networks\n\nReal AI you use daily:\n- Google Search ranking\n- Netflix recommendations\n- Spam filters\n- Face unlock\n- ChatGPT, Claude\n\nHow AI learns:\n1. Give thousands of examples\n2. Find patterns\n3. Predict on new data"),
            (2,False,"Supervised vs Unsupervised Learning",20,"Supervised Learning:\nLabelled training data → model learns mappings.\nExamples: spam detection, house prices, image classification.\nAlgorithms: Linear Regression, Decision Trees, SVM, Random Forest.\n\nUnsupervised Learning:\nNo labels — finds hidden patterns.\nExamples: customer segmentation, anomaly detection.\nAlgorithms: K-Means, DBSCAN, PCA.\n\nReinforcement Learning:\nAgent learns by trial and error with rewards.\nExamples: AlphaGo, trading algorithms, robot navigation.\n\nHow to choose:\n- Labels available? → Supervised\n- Finding groups?   → Unsupervised\n- Agent + reward?   → Reinforcement"),
            (3,False,"Neural Networks Explained",25,"Inspired by the human brain — layers of connected nodes.\n\nStructure:\n    Input layer → Hidden layers → Output layer\n\nHow a neuron works:\n    output = activation(x1*w1 + x2*w2 + bias)\n\nActivation functions:\n- ReLU    → max(0,x) — most common\n- Sigmoid → 0 to 1 — binary classification\n- Softmax → probabilities — multi-class\n\nTraining:\n1. Forward pass — data flows through, gets prediction\n2. Calculate loss — how wrong was it?\n3. Backprop — which weights caused the error?\n4. Gradient descent — nudge weights in right direction\n5. Repeat thousands of times\n\nDeep Learning = many hidden layers."),
            (4,False,"Large Language Models and Prompt Engineering",20,"LLMs are neural networks trained on massive text data.\nExamples: GPT-4, Claude, Gemini, LLaMA.\n\nTraining phases:\n1. Pre-training  → learn from trillions of words\n2. Fine-tuning   → curated high-quality data\n3. RLHF          → humans rate responses\n\nTokens:\nLLMs process text as tokens (~4 chars each).\nContext window = max tokens at once.\n\nPrompt Engineering:\nBad:  'Tell me about Python'\nGood: 'Explain Python decorators to a beginner with a simple example'\n\nTechniques:\n- Be specific about format\n- Give context\n- Few-shot prompting\n- Chain of thought: 'think step by step'"),
            (5,False,"Build your first ML model",30,"Using scikit-learn — most popular Python ML library.\n\n    pip install scikit-learn numpy\n\nThe ML workflow:\n1. Load data\n2. Split train/test\n3. Choose model\n4. Train\n5. Evaluate\n6. Predict\n\nExample:\n    from sklearn.linear_model import LinearRegression\n    from sklearn.model_selection import train_test_split\n\n    X = [[500],[750],[1000],[1500]]\n    y = [25, 35, 50, 75]\n\n    X_train, X_test, y_train, y_test = train_test_split(X, y)\n    model = LinearRegression()\n    model.fit(X_train, y_train)\n\n    price = model.predict([[1100]])\n    print(f'Predicted: {price[0]:.1f} lakhs')"),
        ]:
            db.add(Lesson(course_id=c3.id,order=l[0],is_free=l[1],title=l[2],duration_min=l[3],content=l[4]))

        db.commit()
        print("\n✅ Seeded successfully!")
        print(f"   📘 Python for Beginners       — Free  — 5 lessons")
        print(f"   📗 Web Dev with FastAPI        — ₹999  — 6 lessons")
        print(f"   📙 Intro to AI & ML            — ₹1499 — 5 lessons")
        print("\nOpen http://localhost:8000/courses to see them!")
    except Exception as e:
        db.rollback(); print(f"❌ Error: {e}"); raise
    finally:
        db.close()

if __name__ == "__main__":
    seed()
