import pandas as pd
from sqlalchemy import MetaData
from database import engine, get_db
from models import Base, GlobalProduct

metadata = MetaData()

def drop_all_tables():
    print("Сброс таблиц...")
    metadata.reflect(bind=engine)
    for table in reversed(metadata.sorted_tables):
        print(f"Удаляется таблица: {table.name}")
        table.drop(engine)

def create_all_tables():
    print("Создание таблиц...")
    Base.metadata.create_all(bind=engine)
    print("Таблицы успешно созданы!")

# добавление продуктов из Excel-таблицы
def insert_products_from_excel(products_file):
    print("Чтение данных из Excel...")
    df = pd.read_excel(products_file)

    required_columns = ['name', 'calories', 'proteins', 'fats', 'carbs']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Отсутствует обязательный столбец: {col}")

    db = next(get_db())

    print("Вставка продуктов в таблицу global_products...")
    for index, row in df.iterrows():

        existing_product = db.query(GlobalProduct).filter_by(name=row['name']).first()
        if existing_product:
            print(f"Продукт '{row['name']}' уже существует, пропуск.")
            continue

        product = GlobalProduct(
            name=row['name'],
            calories=row['calories'],
            proteins=row['proteins'],
            fats=row['fats'],
            carbs=row['carbs']
        )
        db.add(product)
        db.commit()

    try:
        db.commit()
        print("Продукты успешно добавлены!")
    except Exception as e:
        db.rollback()
        print(f"Ошибка при добавлении продуктов: {str(e)}")
    finally:
        db.close()

# Пересоздание таблиц БД и добавление продуктов из products.xlsx
if __name__ == "__main__":
    excel_file = "products.xlsx"

    drop_all_tables()
    create_all_tables()

    insert_products_from_excel(excel_file)
