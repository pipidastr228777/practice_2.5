import tkinter as tk
import requests
import sqlite3

conn = sqlite3.connect("currency.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS group_currency (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER,
    currency_code TEXT,
    UNIQUE(group_id, currency_code),
    FOREIGN KEY(group_id) REFERENCES groups(id)
)
""")
conn.commit()

def get_data():
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    try:
        response = requests.get(url)
        return response.json()
    except:
        print("Ошибка при получении данных")
        return {"Valute": {}}

data = get_data()


root = tk.Tk()
root.title("Курсы валют")
root.geometry("700x500")
text_output = tk.Text(root, width=50, height=20)
text_output.pack(pady=10)

entry = tk.Entry(root)
entry.pack(pady=5)


def show_all(data):
    text_output.delete(1.0, tk.END)
    for code, val in data["Valute"].items():
        text_output.insert(tk.END, f"{code} - {val['Value']}\n")


def show_one(data):
    code = entry.get().upper()
    text_output.delete(1.0, tk.END)
    if code in data["Valute"]:
        text_output.insert(tk.END, f"{code} - {data['Valute'][code]['Value']}\n")
    else:
        text_output.insert(tk.END, "Валюта не найдена\n")


def create_group():
    name = entry.get().strip()
    if name == "":
        text_output.insert(tk.END, "Название группы пустое\n")
        return
    try:
        cur.execute("INSERT INTO groups (name) VALUES (?)", (name,))
        conn.commit()
        text_output.insert(tk.END, f"Группа '{name}' создана\n")
    except:
        text_output.insert(tk.END, "Такая группа уже существует\n")

def show_group():
    text_output.delete(1.0, tk.END)
    cur.execute("SELECT id, name FROM groups")
    groups = cur.fetchall()
    if not groups:
        text_output.insert(tk.END, "Групп нет\n")
        return
    for gid, name in groups:
        cur.execute("SELECT currency_code FROM group_currency WHERE group_id=?", (gid,))
        codes = [r[0] for r in cur.fetchall()]
        if codes:
            text_output.insert(tk.END, f"{name}: {', '.join(codes)}\n")
        else:
            text_output.insert(tk.END, f"{name}: пусто\n")

def add_group():
    text_output.delete(1.0, tk.END)
    parts = entry.get().split()
    if len(parts) != 2:
        text_output.insert(tk.END, "Формат: <название_группы> <код_валюты>\n")
        return
    name, cur_code = parts
    cur_code = cur_code.upper()
    cur.execute("SELECT id FROM groups WHERE name=?", (name,))
    res = cur.fetchone()
    if not res:
        text_output.insert(tk.END, "Группа не найдена\n")
        return
    gid = res[0]
    if cur_code not in data["Valute"]:
        text_output.insert(tk.END, "Валюта не найдена\n")
        return
    try:
        cur.execute("INSERT INTO group_currency (group_id, currency_code) VALUES (?, ?)", (gid, cur_code))
        conn.commit()
        text_output.insert(tk.END, f"Валюта {cur_code} добавлена в группу {name}\n")
    except:
        text_output.insert(tk.END, "Валюта уже в группе\n")

btn_all = tk.Button(root, text="Все валюты", command=lambda: show_all(data))
btn_all.pack()
btn_one = tk.Button(root, text="Найти валюту", command=lambda: show_one(data))
btn_one.pack()
btn_create = tk.Button(root, text="Создать группу", command=create_group)
btn_create.pack()
btn_show = tk.Button(root, text="Показать группы", command=show_group)
btn_show.pack()
btn_add = tk.Button(root, text="Добавить в группу", command=add_group)
btn_add.pack()

root.mainloop()
conn.close()