from sqlalchemy import MetaData
from database import engine
from models import Base

metadata = MetaData()

def drop_all_tables():
    metadata.reflect(bind=engine)
    for table in reversed(metadata.sorted_tables):
        print(f"Удаляется таблица: {table.name}")
        table.drop(engine)


def create_all_tables():
    print("Создание таблиц...")
    Base.metadata.create_all(bind=engine)
    print("Таблицы успешно созданы!")


if __name__ == "__main__":
    drop_all_tables()
    create_all_tables()