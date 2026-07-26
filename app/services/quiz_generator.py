"""
Rule-based quiz generator.
Generates multiple choice questions from lesson content.
Concept questions take priority — hand-crafted per topic for accuracy.
"""
import random
from typing import List
from dataclasses import dataclass


@dataclass
class QuizQuestion:
    question: str
    options: List[str]
    correct: int
    explanation: str


def generate_quiz(lesson_title: str, lesson_content: str, num_questions: int = 5) -> List[QuizQuestion]:
    title_lower = lesson_title.lower()
    content_lower = (lesson_content or "").lower()

    # concept questions are hand-crafted and always accurate
    questions = _concept_questions(title_lower, content_lower)

    # shuffle and pick
    random.shuffle(questions)
    result = questions[:num_questions]

    # pad with fallback if not enough
    while len(result) < num_questions:
        result += _fallback_questions(lesson_title)

    return result[:num_questions]


def _concept_questions(title: str, content: str) -> List[QuizQuestion]:
    questions = []

    # ── Python loops ──
    if "loop" in title or ("for" in title and "loop" in content) or "while" in title:
        questions += [
            QuizQuestion("Which keyword is used to start a for loop in Python?",
                ["for", "loop", "repeat", "each"], 0,
                "'for' is the keyword that begins a for loop in Python."),
            QuizQuestion("What does the 'break' statement do inside a loop?",
                ["Exits the loop immediately", "Skips to the next iteration", "Restarts the loop from the beginning", "Pauses the loop"],
                0, "'break' exits the loop immediately, stopping all further iterations."),
            QuizQuestion("What does 'continue' do inside a loop?",
                ["Skips the current iteration and moves to the next", "Exits the loop", "Ends the program", "Repeats the current iteration"],
                0, "'continue' skips the rest of the current iteration and moves to the next one."),
            QuizQuestion("Which loop is best when you know how many times to repeat?",
                ["for loop", "while loop", "do-while loop", "infinite loop"],
                0, "The 'for' loop is used when the number of iterations is known."),
            QuizQuestion("What does range(5) produce in Python?",
                ["Numbers 0, 1, 2, 3, 4", "Numbers 1, 2, 3, 4, 5", "Numbers 0 to 5 inclusive", "A list of 5 random numbers"],
                0, "range(5) produces integers from 0 up to (but not including) 5."),
            QuizQuestion("Which loop keeps running as long as a condition is True?",
                ["while loop", "for loop", "range loop", "repeat loop"],
                0, "The 'while' loop continues executing as long as its condition is True."),
        ]

    # ── Python variables & data types ──
    elif "variable" in title or "data type" in title or "type" in title:
        questions += [
            QuizQuestion("Which of these is a valid Python variable name?",
                ["my_var", "2var", "my-var", "class"],
                0, "Variable names must start with a letter or underscore, not a digit or special character."),
            QuizQuestion("What data type stores True or False values in Python?",
                ["bool", "str", "int", "float"],
                0, "bool (boolean) stores True or False values."),
            QuizQuestion("Which data type stores decimal numbers in Python?",
                ["float", "int", "str", "bool"],
                0, "float stores floating-point (decimal) numbers."),
            QuizQuestion("What is the output of type('hello') in Python?",
                ["<class 'str'>", "<class 'int'>", "<class 'bool'>", "<class 'list'>"],
                0, "String literals like 'hello' are of type str."),
            QuizQuestion("What does an f-string do in Python?",
                ["Embeds variables inside a string", "Creates a new file", "Formats numbers only", "Converts string to float"],
                0, "f-strings allow you to embed variable values directly inside a string using {}."),
            QuizQuestion("Which keyword represents the absence of a value in Python?",
                ["None", "Null", "Empty", "Void"],
                0, "None represents the absence of a value in Python."),
        ]

    # ── Python functions ──
    elif "function" in title or "def" in title:
        questions += [
            QuizQuestion("Which keyword defines a function in Python?",
                ["def", "function", "func", "define"],
                0, "Python uses 'def' followed by the function name to define a function."),
            QuizQuestion("What keyword sends a value back from a function?",
                ["return", "yield", "output", "give"],
                0, "'return' exits the function and sends a value back to the caller."),
            QuizQuestion("What are values passed into a function called?",
                ["Arguments", "Variables", "Returns", "Outputs"],
                0, "Values passed to a function are called arguments (or parameters in the definition)."),
            QuizQuestion("What happens if a function has no return statement?",
                ["It returns None", "It returns 0", "It crashes", "It returns False"],
                0, "A function without a return statement implicitly returns None."),
            QuizQuestion("What is a default parameter in Python?",
                ["A parameter with a pre-set value", "A required parameter", "A parameter that returns nothing", "A global variable"],
                0, "Default parameters have a pre-set value used when no argument is provided."),
            QuizQuestion("What symbol separates parameters in a function definition?",
                ["Comma ,", "Semicolon ;", "Colon :", "Pipe |"],
                0, "Parameters in a function definition are separated by commas."),
        ]

    # ── Introduction to Python / Beginner ──
    elif "introduction" in title or "beginner" in title or "python" in title:
        questions += [
            QuizQuestion("Which function displays output to the console in Python?",
                ["print()", "echo()", "output()", "display()"],
                0, "print() is the built-in function for displaying output in Python."),
            QuizQuestion("What file extension do Python files use?",
                [".py", ".python", ".pt", ".pyt"],
                0, "Python source files use the .py extension."),
            QuizQuestion("What symbol is used for single-line comments in Python?",
                ["#", "//", "/*", "--"],
                0, "The # symbol marks the start of a single-line comment in Python."),
            QuizQuestion("Which of these is NOT a Python data type?",
                ["varchar", "int", "float", "str"],
                0, "varchar is a SQL data type, not a Python data type."),
            QuizQuestion("How do you run a Python file called app.py from the terminal?",
                ["python app.py", "run app.py", "execute app.py", "start app.py"],
                0, "You run Python files with the 'python filename.py' command."),
            QuizQuestion("Python is primarily used in which fields?",
                ["Web dev, data science, AI, and automation", "Only game development", "Only mobile apps", "Only hardware programming"],
                0, "Python is widely used in web development, data science, AI, automation, and more."),
        ]

    # ── FastAPI / Web API ──
    elif "fastapi" in title or "api" in title or "route" in title or "endpoint" in title:
        questions += [
            QuizQuestion("Which HTTP method is used to retrieve data?",
                ["GET", "POST", "DELETE", "PATCH"],
                0, "GET requests fetch/read data without modifying it."),
            QuizQuestion("Which HTTP method creates a new resource?",
                ["POST", "GET", "PUT", "DELETE"],
                0, "POST sends data to the server to create a new resource."),
            QuizQuestion("What does a 404 HTTP status code mean?",
                ["Resource not found", "Server error", "Unauthorized", "Bad request"],
                0, "404 means the requested resource was not found on the server."),
            QuizQuestion("What does Pydantic do in FastAPI?",
                ["Validates request and response data", "Manages the database", "Handles authentication", "Serves HTML files"],
                0, "Pydantic validates incoming data against defined schemas automatically."),
            QuizQuestion("What decorator marks a function as a GET endpoint in FastAPI?",
                ["@router.get()", "@app.fetch()", "@get.route()", "@endpoint.get()"],
                0, "@router.get() or @app.get() decorates a function as a GET endpoint."),
            QuizQuestion("What does the Depends() function do in FastAPI?",
                ["Injects dependencies like DB sessions or current user", "Defines route parameters", "Sends HTTP responses", "Creates database tables"],
                0, "Depends() injects reusable dependencies (like database sessions) into route handlers."),
        ]

    # ── SQLAlchemy / Database ──
    elif "sqlalchemy" in title or "database" in title or "orm" in title or "model" in title:
        questions += [
            QuizQuestion("What does ORM stand for?",
                ["Object-Relational Mapping", "Object-Route Manager", "Organised Record Method", "Optional Return Mode"],
                0, "ORM stands for Object-Relational Mapping — it maps Python classes to database tables."),
            QuizQuestion("Which SQLAlchemy method saves a new object to the database?",
                ["db.add() then db.commit()", "db.save()", "db.insert()", "db.push()"],
                0, "You first add() the object to the session, then commit() to write it to the database."),
            QuizQuestion("What does db.query(User).filter(...).first() do?",
                ["Returns the first matching user or None", "Returns all users", "Deletes a user", "Updates a user"],
                0, ".first() returns the first result of the query, or None if no match is found."),
            QuizQuestion("Which column type is used for primary keys in SQLAlchemy?",
                ["Column(String, primary_key=True)", "Column(PK=True)", "PrimaryKey(String)", "Column.pk(String)"],
                0, "primary_key=True in a Column definition marks it as the primary key."),
            QuizQuestion("What does cascade='all, delete-orphan' do in SQLAlchemy?",
                ["Deletes related records when parent is deleted", "Creates copies of records", "Syncs data between tables", "Prevents deletion"],
                0, "cascade delete removes related child records when the parent record is deleted."),
        ]

    # ── JWT / Authentication ──
    elif "jwt" in title or "auth" in title or "token" in title or "password" in title:
        questions += [
            QuizQuestion("What does JWT stand for?",
                ["JSON Web Token", "Java Web Transfer", "JavaScript Web Type", "JSON Write Token"],
                0, "JWT stands for JSON Web Token — a compact way to transmit claims between parties."),
            QuizQuestion("Which hashing algorithm is commonly used for passwords?",
                ["bcrypt", "MD5", "SHA-1", "Base64"],
                0, "bcrypt is the recommended password hashing algorithm — it's slow by design to prevent brute force."),
            QuizQuestion("What HTTP header carries the JWT token?",
                ["Authorization: Bearer <token>", "Token: <token>", "Auth: JWT <token>", "X-Token: <token>"],
                0, "JWT tokens are sent in the Authorization header with the 'Bearer' prefix."),
            QuizQuestion("What does a 401 HTTP status code mean?",
                ["Unauthorized — authentication required", "Forbidden", "Not found", "Server error"],
                0, "401 Unauthorized means the request requires valid authentication credentials."),
            QuizQuestion("Why should passwords never be stored as plain text?",
                ["They can be stolen if the database is breached", "They take up too much space", "Python cannot store plain text", "Databases don't support text"],
                0, "Plain text passwords are immediately readable if the database is compromised. Always hash them."),
        ]

    # ── AI / Machine Learning ──
    elif "ai" in title or "machine learning" in title or "neural" in title or "llm" in title or "model" in title:
        questions += [
            QuizQuestion("What does AI stand for?",
                ["Artificial Intelligence", "Automated Integration", "Automated Intelligence", "Artificial Integration"],
                0, "AI stands for Artificial Intelligence — the simulation of human intelligence by machines."),
            QuizQuestion("Which type of machine learning uses labelled training data?",
                ["Supervised learning", "Unsupervised learning", "Reinforcement learning", "Transfer learning"],
                0, "Supervised learning trains on labelled examples where the correct output is known."),
            QuizQuestion("What is a neural network inspired by?",
                ["The human brain", "Electric circuits", "Spreadsheets", "Database tables"],
                0, "Neural networks are loosely inspired by the structure of neurons in the human brain."),
            QuizQuestion("What does LLM stand for?",
                ["Large Language Model", "Linear Learning Machine", "Local Logic Module", "Layered Language Matrix"],
                0, "LLM stands for Large Language Model — AI systems trained on massive amounts of text data."),
            QuizQuestion("What is the purpose of training an ML model?",
                ["To learn patterns from data so it can make predictions", "To write code automatically", "To store data in a database", "To create user interfaces"],
                0, "Training allows a model to learn patterns from examples so it can make predictions on new data."),
            QuizQuestion("Which Python library is most popular for machine learning?",
                ["scikit-learn", "pygame", "tkinter", "flask"],
                0, "scikit-learn is the most widely used Python library for classical machine learning algorithms."),
        ]

    # ── Docker / Deployment ──
    elif "docker" in title or "deploy" in title or "container" in title:
        questions += [
            QuizQuestion("What is a Docker container?",
                ["A lightweight isolated environment that runs an application", "A type of database", "A cloud storage service", "A web browser"],
                0, "A Docker container packages an app and all its dependencies into an isolated environment."),
            QuizQuestion("What file defines how to build a Docker image?",
                ["Dockerfile", "docker.json", "container.yml", "build.py"],
                0, "The Dockerfile contains instructions for building a Docker image."),
            QuizQuestion("What command builds a Docker image?",
                ["docker build", "docker run", "docker start", "docker create"],
                0, "'docker build' reads the Dockerfile and creates an image."),
            QuizQuestion("What does 'docker compose up' do?",
                ["Starts all services defined in docker-compose.yml", "Uploads files to the cloud", "Installs Docker", "Creates a Dockerfile"],
                0, "'docker compose up' starts all services defined in the docker-compose.yml file."),
            QuizQuestion("What port does a FastAPI app typically run on?",
                ["8000", "3000", "80", "5432"],
                0, "FastAPI with Uvicorn runs on port 8000 by default."),
        ]

    # ── Generic fallback for unrecognised topics ──
    else:
        questions += _fallback_questions("this lesson")

    return questions


def _fallback_questions(lesson_title: str) -> List[QuizQuestion]:
    return [
        QuizQuestion("Why is it important to understand core programming concepts?",
            ["They form the foundation for all advanced topics", "They are only used in one language", "They have no practical applications", "They are only for beginners"],
            0, "Core concepts like variables, loops, and functions are the building blocks of all programming."),
        QuizQuestion("What is the best approach when learning a new programming topic?",
            ["Practice with small examples first", "Memorise all the syntax immediately", "Skip to advanced topics", "Only read, never code"],
            0, "Building small working examples is the most effective way to solidify new programming knowledge."),
        QuizQuestion("What should you do when your code has a bug?",
            ["Read the error message carefully and debug step by step", "Delete all your code and start over", "Ignore it and move on", "Ask someone else to fix it"],
            0, "Error messages give you the exact location and type of error — always read them first."),
    ]