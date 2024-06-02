from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# доступ к
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Создание движка базы данных
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Создание фабрики сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создание базового класса для моделей
Base = declarative_base()


def get_db():
    """
    Создаёт сессию базы данных и возвращает её.
    Сессия автоматически закрывается после использования.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
