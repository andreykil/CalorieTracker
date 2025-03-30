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
    print("Сброс таблиц...")
    drop_all_tables()
    create_all_tables()

    db = next(get_db())
    apple = GlobalProduct(name="Суп", calories=120, proteins=5, fats=5, carbs=20)
    pear = GlobalProduct(name="Каша", calories=322, proteins=10, fats=2, carbs=30)
    tomato = GlobalProduct(name="Помидор", calories=50, proteins=0, fats=1, carbs=10)
    db.add(apple)
    db.add(pear)
    db.add(tomato)
    db.commit()
    print("Добавлено: Суп, Каша, Помидор")