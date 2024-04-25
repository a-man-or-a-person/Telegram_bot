import sqlite3


def create_table():
    conn = sqlite3.connect('telegram_bot.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT exists bot_user(
        telegram_id bigint PRIMARY KEY,
        created_at timestamp default current_timestamp not NULL
        )''')

    cur.execute('''CREATE TABLE IF NOT exists book_category(
        id INTEGER PRIMARY KEY,
        created_at timestamp default current_timestamp not NULL,
        name varchar(200) not NULL unique,
        ordering integer not null unique
        )''')

    cur.execute('''CREATE TABLE IF NOT exists book(
        id INTEGER PRIMARY KEY,
        created_at timestamp default current_timestamp not NULL,
        name TEXT,
        category_id INTEGER NOT NULL,
        ordering integer not null,
        read_start date,
        read_finish date,
        FOREIGN KEY(category_id) REFERENCES book_category(id)
        
        )''')

    # Book status
    # 1. not read
    # 2. will be next
    # 3. reading now
    # 4. read

    # Voting
    cur.execute("""create table IF NOT exists voting (
    id integer primary key,
    voting_start timestamp not NULL,
    voting_finish timestamp not NULL
    )""")

    cur.execute("""create table IF NOT exists vote(
    vote_id integer,
    user_id integer not null,
    first_book integer,
    second_book integer,
    third_book integer,
    foreign key(user_id) references bot_user(telegram_id),
    foreign key (vote_id) references voting(id), 
    foreign key (first_book) references book(id),
    foreign key (second_book) references book(id),
    foreign key (third_book) references book(id),
    primary key(vote_id, user_id)
    )""")
    conn.commit()
    conn.close()


conn = sqlite3.connect('telegram_bot.db')
cur = conn.cursor()
# cur.execute('DROP TABLE IF EXISTS vote')
# create_table()
genres = [("Фэнтези", 10), ("Научная фантастика", 20), ("Детектив", 30), ("Роман", 40), ("Поэзия", 50)]
books = [("Гарри Поттер и философский камень", 1, 1), ("Гарри Поттер и Тайная комната", 1, 2),
         ("Гарри Поттер и узник Азкабана", 1, 3), ("Марсианин", 2, 1), ("Основание", 2, 2), ("Азимов. Я, робот", 2, 3),
         ("Убийство в Восточном экспрессе", 3, 1), ("Девушка с татуировкой дракона", 3, 2), ("Шерлок Холмс", 3, 3),
         ("Гордость и предубеждение", 4, 1), ("Анна Каренина", 4, 2), ("Три товарища", 4, 3),
         ("Стихотворения Пушкина", 5, 1), ("Стихи Есенина", 5, 2), ("Сонеты Шекспира", 5, 3)]
# cur.execute('PRAGMA table_info("book_category")')
# cur.execute('INSERT INTO voting("voting_start", "voting_finish") VALUES("2024-04-23", "2024-04-28")')
# cur.execute('DELETE FROM voting')
# cur.executemany('insert into book ("name", "category_id", "ordering") values(?, ?, ?)', books)
cur.execute('select * from vote')
for row in cur.fetchall():
    print(row)
# cur.execute('update book set read_start="2024-04-18", read_finish="2024-05-21" WHERE name="Марсианин"')
conn.commit()
conn.close()
