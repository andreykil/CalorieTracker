from sqlalchemy import MetaData
from database import engine
from models import Base, GlobalProduct

from database import get_db

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

    db = next(get_db())
    apple = GlobalProduct(name="apple", calories=228, proteins=1, fats=2, carbs=3)
    pear = GlobalProduct(name="pear", calories=322, proteins=1, fats=2, carbs=3)
    tomato = GlobalProduct(name="Помидор", calories=1488, proteins=1, fats=2, carbs=3)
    db.add(apple)
    db.add(pear)
    db.add(tomato)
    db.commit()
    print("Добавлено: яблоко, груша и помидор")