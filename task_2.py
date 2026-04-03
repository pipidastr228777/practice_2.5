import sqlite3

conn = sqlite3.connect("drink_store.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS alcoholic_drinks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    strength REAL,
    price REAL,
    quantity INTEGER
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    quantity INTEGER
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS cocktails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    composition TEXT,
    price REAL,
    strength REAL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS cocktail_ingredients (
    cocktail_id INTEGER,
    ingredient_name TEXT,
    amount INTEGER,
    FOREIGN KEY (cocktail_id) REFERENCES cocktails (id)
)
''')

conn.commit()


def add_alcoholic_drink():
    print("\n--- Добавление алкогольного напитка ---")
    name = input("Введите название: ")

    try:
        strength = float(input("Введите крепость (0-100): "))
        price = float(input("Введите цену: "))
        quantity = int(input("Введите количество на складе (в мл): "))

        cursor.execute('''
        INSERT INTO alcoholic_drinks (name, strength, price, quantity)
        VALUES (?, ?, ?, ?)
        ''', (name, strength, price, quantity))
        conn.commit()
        print("Напиток успешно добавлен!")
    except Exception as e:
        print(f"Ошибка при добавлении: {e}")


def show_alcoholic_drinks():
    print("\n--- Список алкогольных напитков ---")
    try:
        cursor.execute("SELECT * FROM alcoholic_drinks")
        rows = cursor.fetchall()
        if not rows:
            print("Напитков нет.")
            return

        for row in rows:
            print(f"ID: {row[0]} | {row[1]} | Крепость: {row[2]}% | Цена: {row[3]} руб. | Остаток: {row[4]} мл")
    except Exception as e:
        print(f"Ошибка при чтении данных: {e}")


def add_ingredient():
    print("\n--- Добавление ингредиента ---")
    name = input("Введите название ингредиента: ")

    try:
        quantity = int(input("Введите количество (в мл или граммах): "))

        cursor.execute('''
        INSERT INTO ingredients (name, quantity)
        VALUES (?, ?)
        ''', (name, quantity))
        conn.commit()
        print("Ингредиент успешно добавлен!")
    except Exception as e:
        print(f"Ошибка при добавлении: {e}")


def show_ingredients():
    print("\n--- Список ингредиентов ---")
    try:
        cursor.execute("SELECT * FROM ingredients")
        rows = cursor.fetchall()
        if not rows:
            print("Ингредиентов нет.")
            return

        for row in rows:
            print(f"ID: {row[0]} | {row[1]} | Остаток: {row[2]}")
    except Exception as e:
        print(f"Ошибка при чтении данных: {e}")


def add_cocktail():
    print("\n--- Добавление коктейля ---")
    name = input("Введите название коктейля: ")

    print("Введите состав (алкогольные напитки и ингредиенты):")
    composition = input("Описание состава: ")

    try:
        price = float(input("Введите цену коктейля: "))

        total_strength = 0
        total_volume = 0

        print("\nДобавьте алкогольные напитки в составе:")
        while True:
            drink_name = input("Введите название напитка (или 'стоп' для завершения): ")
            if drink_name.lower() == 'стоп':
                break

            cursor.execute("SELECT strength, quantity FROM alcoholic_drinks WHERE name = ?", (drink_name,))
            drink = cursor.fetchone()
            if drink:
                try:
                    volume = int(input(f"Введите объем {drink_name} в мл: "))
                    total_strength += drink[0] * volume
                    total_volume += volume
                    print(f"Добавлено {volume} мл {drink_name}")
                except:
                    print("Ошибка ввода объема!")
            else:
                print("Напиток не найден в базе!")

        if total_volume > 0:
            cocktail_strength = total_strength / total_volume
        else:
            cocktail_strength = 0

        cursor.execute('''
        INSERT INTO cocktails (name, composition, price, strength)
        VALUES (?, ?, ?, ?)
        ''', (name, composition, price, cocktail_strength))
        conn.commit()
        print(f"Коктейль успешно добавлен! Крепость: {cocktail_strength:.1f}%")
    except Exception as e:
        print(f"Ошибка при добавлении: {e}")


def show_cocktails():
    print("\n--- Список коктейлей ---")
    try:
        cursor.execute("SELECT * FROM cocktails")
        rows = cursor.fetchall()
        if not rows:
            print("Коктейлей нет.")
            return

        for row in rows:
            print(f"ID: {row[0]} | {row[1]} | Крепость: {row[4]:.1f}% | Цена: {row[3]} руб.")
            print(f"  Состав: {row[2]}")
    except Exception as e:
        print(f"Ошибка при чтении данных: {e}")


def sell_cocktail():
    print("\n--- Продажа коктейля ---")
    try:
        cocktail_id = int(input("Введите ID коктейля: "))
        cursor.execute("SELECT * FROM cocktails WHERE id = ?", (cocktail_id,))
        cocktail = cursor.fetchone()

        if not cocktail:
            print("Коктейль не найден!")
            return

        print(f"Коктейль: {cocktail[1]}")
        print(f"Цена: {cocktail[3]} руб.")

        confirm = input("Подтвердите продажу (да/нет): ")
        if confirm.lower() == "да":
            print(f"Коктейль продан! Сумма: {cocktail[3]} руб.")
        else:
            print("Продажа отменена.")
    except Exception as e:
        print(f"Ошибка при продаже: {e}")


def sell_alcoholic_drink():
    print("\n--- Продажа алкогольного напитка ---")
    try:
        drink_id = int(input("Введите ID напитка: "))
        cursor.execute("SELECT * FROM alcoholic_drinks WHERE id = ?", (drink_id,))
        drink = cursor.fetchone()

        if not drink:
            print("Напиток не найден!")
            return

        print(f"Напиток: {drink[1]}")
        print(f"Цена за 100 мл: {drink[3]} руб.")
        print(f"Доступно: {drink[4]} мл")

        amount = int(input("Введите количество в мл: "))

        if amount > drink[4]:
            print("Недостаточно на складе!")
            return

        price = (drink[3] / 100) * amount
        print(f"Сумма к оплате: {price:.2f} руб.")

        confirm = input("Подтвердите продажу (да/нет): ")
        if confirm.lower() == "да":
            new_quantity = drink[4] - amount
            cursor.execute("UPDATE alcoholic_drinks SET quantity = ? WHERE id = ?", (new_quantity, drink_id))
            conn.commit()
            print(f"Продажа выполнена! Остаток: {new_quantity} мл")
        else:
            print("Продажа отменена.")
    except Exception as e:
        print(f"Ошибка при продаже: {e}")


def restock_drinks():
    print("\n--- Пополнение запасов напитков ---")
    try:
        drink_id = int(input("Введите ID напитка: "))
        cursor.execute("SELECT * FROM alcoholic_drinks WHERE id = ?", (drink_id,))
        drink = cursor.fetchone()

        if not drink:
            print("Напиток не найден!")
            return

        print(f"Напиток: {drink[1]}")
        print(f"Текущий остаток: {drink[4]} мл")

        amount = int(input("Введите количество для добавления (в мл): "))
        new_quantity = drink[4] + amount

        cursor.execute("UPDATE alcoholic_drinks SET quantity = ? WHERE id = ?", (new_quantity, drink_id))
        conn.commit()
        print(f"Запасы пополнены! Новый остаток: {new_quantity} мл")
    except Exception as e:
        print(f"Ошибка при пополнении: {e}")


def restock_ingredients():
    print("\n--- Пополнение запасов ингредиентов ---")
    try:
        ingredient_id = int(input("Введите ID ингредиента: "))
        cursor.execute("SELECT * FROM ingredients WHERE id = ?", (ingredient_id,))
        ingredient = cursor.fetchone()

        if not ingredient:
            print("Ингредиент не найден!")
            return

        print(f"Ингредиент: {ingredient[1]}")
        print(f"Текущий остаток: {ingredient[2]}")

        amount = int(input("Введите количество для добавления: "))
        new_quantity = ingredient[2] + amount

        cursor.execute("UPDATE ingredients SET quantity = ? WHERE id = ?", (new_quantity, ingredient_id))
        conn.commit()
        print(f"Запасы пополнены! Новый остаток: {new_quantity}")
    except Exception as e:
        print(f"Ошибка при пополнении: {e}")


def menu_drinks():
    while True:
        print("\n" + "-" * 40)
        print("УЧЕТ НАПИТКОВ")
        print("-" * 40)
        print("1. Добавить алкогольный напиток")
        print("2. Показать все напитки")
        print("3. Добавить ингредиент")
        print("4. Показать все ингредиенты")
        print("0. Назад в главное меню")
        print("-" * 40)

        choice = input("Выберите действие: ")

        if choice == "1":
            add_alcoholic_drink()
        elif choice == "2":
            show_alcoholic_drinks()
        elif choice == "3":
            add_ingredient()
        elif choice == "4":
            show_ingredients()
        elif choice == "0":
            break
        else:
            print("Неверный выбор! Попробуйте снова.")


def menu_cocktails():
    while True:
        print("\n" + "-" * 40)
        print("УПРАВЛЕНИЕ КОКТЕЙЛЯМИ")
        print("-" * 40)
        print("1. Добавить коктейль")
        print("2. Показать все коктейли")
        print("0. Назад в главное меню")
        print("-" * 40)

        choice = input("Выберите действие: ")

        if choice == "1":
            add_cocktail()
        elif choice == "2":
            show_cocktails()
        elif choice == "0":
            break
        else:
            print("Неверный выбор! Попробуйте снова.")


def menu_operations():
    while True:
        print("\n" + "-" * 40)
        print("ОПЕРАЦИИ")
        print("-" * 40)
        print("1. Продать коктейль")
        print("2. Продать алкогольный напиток")
        print("3. Пополнить запасы напитков")
        print("4. Пополнить запасы ингредиентов")
        print("0. Назад в главное меню")
        print("-" * 40)

        choice = input("Выберите действие: ")

        if choice == "1":
            sell_cocktail()
        elif choice == "2":
            sell_alcoholic_drink()
        elif choice == "3":
            restock_drinks()
        elif choice == "4":
            restock_ingredients()
        elif choice == "0":
            break
        else:
            print("Неверный выбор! Попробуйте снова.")


def main_menu():
    while True:
        print("\n" + "=" * 50)
        print("ПРИЛОЖЕНИЕ I LOVE DRINK")
        print("=" * 50)
        print("1. Учет напитков")
        print("2. Управление коктейлями")
        print("3. Операции")
        print("0. Выход")
        print("=" * 50)

        choice = input("Выберите категорию: ")

        if choice == "1":
            menu_drinks()
        elif choice == "2":
            menu_cocktails()
        elif choice == "3":
            menu_operations()
        elif choice == "0":
            print("До свидания!")
            conn.close()
            break
        else:
            print("Неверный выбор! Попробуйте снова.")


if __name__ == "__main__":
    main_menu()