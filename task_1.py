import sqlite3

conn = sqlite3.connect("students.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT,
    last_name TEXT,
    middle_name TEXT,
    group_name TEXT,
    grade1 INTEGER,
    grade2 INTEGER,
    grade3 INTEGER,
    grade4 INTEGER
)
''')
conn.commit()


class Student:
    def __init__(self, first_name, last_name, middle_name, group_name, grades):
        self.first_name = first_name
        self.last_name = last_name
        self.middle_name = middle_name
        self.group_name = group_name
        self.grades = grades


def add_student():
    print("\n--- Добавление нового студента ---")
    first_name = input("Введите имя: ")
    last_name = input("Введите фамилию: ")
    middle_name = input("Введите отчество: ")
    group_name = input("Введите группу: ")

    print("Введите 4 оценки (через Enter):")
    grades = []
    for i in range(4):
        while True:
            try:
                grade = int(input(f"Оценка {i + 1}: "))
                if 1 <= grade <= 5:
                    grades.append(grade)
                    break
                else:
                    print("Оценка должна быть от 1 до 5!")
            except ValueError:
                print("Введите число!")

    try:
        cursor.execute('''
        INSERT INTO students (first_name, last_name, middle_name, group_name, grade1, grade2, grade3, grade4)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (first_name, last_name, middle_name, group_name, grades[0], grades[1], grades[2], grades[3]))
        conn.commit()
        print("Студент успешно добавлен!")
    except Exception as e:
        print(f"Ошибка при добавлении: {e}")


def show_all_students():
    print("\n--- Список всех студентов ---")
    try:
        cursor.execute("SELECT * FROM students")
        rows = cursor.fetchall()
        if not rows:
            print("Студентов нет.")
            return

        if len(rows[0]) != 9:  # id + 8 полей
            print("Ошибка структуры базы данных!")
            return

        for row in rows:
            print(
                f"ID: {row[0]} | {row[1]} {row[2]} {row[3]} | Группа: {row[4]} | Оценки: {row[5]}, {row[6]}, {row[7]}, {row[8]}")
    except Exception as e:
        print(f"Ошибка при чтении данных: {e}")


def show_student():
    print("\n--- Просмотр студента ---")
    try:
        student_id = int(input("Введите ID студента: "))
    except ValueError:
        print("ID должен быть числом!")
        return

    try:
        cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
        row = cursor.fetchone()
        if not row:
            print("Студент не найден!")
            return

        if len(row) < 9:
            print("Ошибка данных студента!")
            return

        grades = [row[5], row[6], row[7], row[8]]
        avg = sum(grades) / len(grades)
        print(f"\nИнформация о студенте:")
        print(f"ID: {row[0]}")
        print(f"ФИО: {row[1]} {row[2]} {row[3]}")
        print(f"Группа: {row[4]}")
        print(f"Оценки: {grades}")
        print(f"Средний балл: {avg:.2f}")
    except Exception as e:
        print(f"Ошибка: {e}")


def edit_student():
    print("\n--- Редактирование студента ---")
    try:
        student_id = int(input("Введите ID студента для редактирования: "))
    except ValueError:
        print("ID должен быть числом!")
        return

    try:
        cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
        current = cursor.fetchone()
        if not current:
            print("Студент не найден!")
            return

        print("Введите новые данные (оставьте пустым, чтобы не менять):")
        first_name = input(f"Имя ({current[1]}): ")
        last_name = input(f"Фамилия ({current[2]}): ")
        middle_name = input(f"Отчество ({current[3]}): ")
        group_name = input(f"Группа ({current[4]}): ")

        first_name = first_name if first_name else current[1]
        last_name = last_name if last_name else current[2]
        middle_name = middle_name if middle_name else current[3]
        group_name = group_name if group_name else current[4]

        print("Введите новые оценки через пробел или Enter, чтобы оставить прежние:")
        print(f"Текущие оценки: {current[5]}, {current[6]}, {current[7]}, {current[8]}")
        grades_input = input("Оценки (4 числа через пробел): ")

        if grades_input:
            try:
                grades = list(map(int, grades_input.split()))
                if len(grades) == 4 and all(1 <= g <= 5 for g in grades):
                    grade1, grade2, grade3, grade4 = grades
                else:
                    print("Должны быть 4 оценки от 1 до 5! Оставляем старые.")
                    grade1, grade2, grade3, grade4 = current[5], current[6], current[7], current[8]
            except:
                print("Ошибка! Оставляем старые оценки.")
                grade1, grade2, grade3, grade4 = current[5], current[6], current[7], current[8]
        else:
            grade1, grade2, grade3, grade4 = current[5], current[6], current[7], current[8]

        cursor.execute('''
        UPDATE students
        SET first_name=?, last_name=?, middle_name=?, group_name=?, grade1=?, grade2=?, grade3=?, grade4=?
        WHERE id=?
        ''', (first_name, last_name, middle_name, group_name, grade1, grade2, grade3, grade4, student_id))
        conn.commit()
        print("Данные обновлены!")
    except Exception as e:
        print(f"Ошибка при редактировании: {e}")


def delete_student():
    print("\n--- Удаление студента ---")
    try:
        student_id = int(input("Введите ID студента для удаления: "))
    except ValueError:
        print("ID должен быть числом!")
        return

    try:
        cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
        if not cursor.fetchone():
            print("Студент не найден!")
            return

        confirm = input(f"Вы уверены, что хотите удалить студента с ID {student_id}? (да/нет): ")
        if confirm.lower() == "да":
            cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
            conn.commit()
            print("Студент удалён!")
        else:
            print("Удаление отменено.")
    except Exception as e:
        print(f"Ошибка при удалении: {e}")


def group_avg():
    print("\n--- Средний балл группы ---")
    group_name = input("Введите название группы: ")

    try:
        cursor.execute(
            "SELECT first_name, last_name, grade1, grade2, grade3, grade4 FROM students WHERE group_name = ?",
            (group_name,))
        rows = cursor.fetchall()
        if not rows:
            print("Группа не найдена или нет студентов.")
            return

        all_grades = []
        print(f"\nСтуденты группы {group_name}:")
        for row in rows:
            grades = [row[2], row[3], row[4], row[5]]
            all_grades.extend(grades)
            avg_student = sum(grades) / len(grades)
            print(f"  - {row[0]} {row[1]}: {grades} (ср. {avg_student:.2f})")

        group_avg_value = sum(all_grades) / len(all_grades)
        print(f"\nСредний балл группы {group_name}: {group_avg_value:.2f}")
    except Exception as e:
        print(f"Ошибка: {e}")


def main_menu():
    while True:
        print("\n" + "=" * 50)
        print("СИСТЕМА УПРАВЛЕНИЯ СТУДЕНТАМИ")
        print("=" * 50)
        print("1. Добавить студента")
        print("2. Показать всех студентов")
        print("3. Показать одного студента (со средним баллом)")
        print("4. Редактировать студента")
        print("5. Удалить студента")
        print("6. Средний балл группы")
        print("0. Выход")
        print("=" * 50)

        choice = input("Выберите действие (0-6): ")

        if choice == "1":
            add_student()
        elif choice == "2":
            show_all_students()
        elif choice == "3":
            show_student()
        elif choice == "4":
            edit_student()
        elif choice == "5":
            delete_student()
        elif choice == "6":
            group_avg()
        elif choice == "0":
            print("До свидания!")
            conn.close()
            break
        else:
            print("Неверный выбор! Попробуйте снова.")


def repair_database():
    try:
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS students_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            middle_name TEXT,
            group_name TEXT,
            grade1 INTEGER,
            grade2 INTEGER,
            grade3 INTEGER,
            grade4 INTEGER
        )
        ''')

        try:
            cursor.execute("SELECT * FROM students")
            rows = cursor.fetchall()
            for row in rows:
                if len(row) >= 9:
                    cursor.execute('''
                    INSERT INTO students_new (id, first_name, last_name, middle_name, group_name, grade1, grade2, grade3, grade4)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', row[:9])
        except:
            pass

        cursor.execute("DROP TABLE IF EXISTS students_old")
        cursor.execute("ALTER TABLE students RENAME TO students_old")
        cursor.execute("ALTER TABLE students_new RENAME TO students")

        conn.commit()
        print("База данных восстановлена!")
    except Exception as e:
        print(f"Ошибка восстановления: {e}")


if __name__ == "__main__":
    try:
        cursor.execute("SELECT * FROM students LIMIT 1")
        test_row = cursor.fetchone()
        if test_row and len(test_row) != 9:
            print("Обнаружена проблема со структурой БД. Восстанавливаем...")
            repair_database()
    except:
        print("Создаем новую базу данных...")

    main_menu()