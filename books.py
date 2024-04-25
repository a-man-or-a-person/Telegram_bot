from dataclasses import dataclass
from datetime import datetime
import aiosqlite
import config


@dataclass
class Book:
    id: int
    name: str
    category_id: int
    category_name: str
    read_start: datetime
    read_finish: datetime


@dataclass
class Category:
    id: int
    name: str
    books: list[Book]


def _group_books_by_category(books: list[Book]) -> list[Category]:
    categories = []
    category_id = None
    for book in books:
        if category_id != book.category_id:
            category_id = book.category_id
            categories.append(Category(
                id=book.category_id,
                name=book.category_name,
                books=[book]))
            continue
        categories[-1].books.append(book)
    return categories


async def get_all_books() -> list[Category]:
    sql = '''select 
        b.id as book_id,
        b.name as book_name,
        c.id as category_id,
        c.name as category_name,
        b.read_start,
        b.read_finish
        from book as b left join book_category as c on c.id=b.category_id order by c."ordering", b."ordering"
        '''
    books = []
    async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(sql) as cursor:
            async for row in cursor:
                books.append(Book(id=row["book_id"],
                                  name=row["book_name"],
                                  category_id=row['category_id'],
                                  category_name=row['category_name'],
                                  read_start=row["read_start"],
                                  read_finish=row["read_finish"]))
    return _group_books_by_category(books)


async def get_not_started_books() -> list[Category]:
    sql = '''select 
        b.id as book_id,
        b.name as book_name,
        c.id as category_id,
        c.name as category_name,
        b.read_start,
        b.read_finish
        from book as b left join book_category as c on c.id=b.category_id
         WHERE b.read_start is NULL
         ORDER BY c."ordering", b."ordering"
        '''
    books = []
    async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(sql) as cursor:
            async for row in cursor:
                books.append(Book(id=row["book_id"],
                                  name=row["book_name"],
                                  category_id=row['category_id'],
                                  category_name=row['category_name'],
                                  read_start=row["read_start"],
                                  read_finish=row["read_finish"]))
    return _group_books_by_category(books)


async def get_already_read_books() -> list[Book]:
    sql = '''SELECT 
        b.id as book_id,
        b.name as book_name,
        c.id as category_id,
        c.name as category_name,
        b.read_start,
        b.read_finish
        FROM book b
        LEFT JOIN book_category c ON c.id = b.category_id
        WHERE read_start < current_date AND read_finish <= current_date
        ORDER BY b.read_start
        '''
    books = []
    async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(sql) as cursor:
            async for row in cursor:
                read_start, read_finish = map(lambda date: datetime.strptime(date, '%Y-%m-%d'),
                                              (row['read_start'], row['read_finish']))

                read_start, read_finish = map(lambda date: date.strftime(config.DATE_FORMAT), (read_start, read_finish))
                books.append(Book(id=row["book_id"],
                                  name=row["book_name"],
                                  category_id=row['category_id'],
                                  category_name=row['category_name'],
                                  read_start=read_start,
                                  read_finish=read_finish))
    return books


async def get_books_by_numbers(numbers: list[int]) -> list[Book]:
    numbers_joined = ','.join(map(str, map(int, numbers)))

    hardcoded_sql_values = []
    for index, number in enumerate(numbers, 1):
        hardcoded_sql_values.append(f'({number}, {index})')
    hardcoded_sql_values = ', '.join(hardcoded_sql_values)

    sql = f'''SELECT t2.* FROM (
        VALUES {hardcoded_sql_values}
        ) t0
        INNER JOIN (
        SELECT t.* FROM (
            SELECT  ROW_NUMBER() OVER( ORDER BY c."ordering", b."ordering") as idx,
            b.id as book_id,
            b.name as book_name,
            c.id as category_id,
            c.name as category_name,
            b.read_start,
            b.read_finish
            FROM book b
            LEFT JOIN book_category c ON c.id = b.category_id
            WHERE read_start is NULL 
        ) t
        WHERE t.idx IN ({numbers_joined}) 
        )t2
        ON t0.column1 = t2.idx
        ORDER BY t0.column2
    '''
    books = []
    async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(sql) as cursor:
            async for row in cursor:
                books.append(Book(id=row["book_id"],
                                  name=row["book_name"],
                                  category_id=row['category_id'],
                                  category_name=row['category_name'],
                                  read_start=None,
                                  read_finish=None))
    return books


async def get_now_reading_books() -> list[Book] | None:
    sql = '''SELECT 
        b.id as book_id,
        b.name as book_name,
        c.id as category_id,
        c.name as category_name,
        b.read_start,
        b.read_finish
        FROM book b
        LEFT JOIN book_category c ON c.id = b.category_id
        WHERE read_start <= current_date AND read_finish >= current_date
        ORDER BY b.read_start
        '''
    books = []
    async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(sql) as cursor:
            async for row in cursor:
                read_start, read_finish = map(lambda date: datetime.strptime(date, '%Y-%m-%d'),
                                              (row['read_start'], row['read_finish']))

                read_start, read_finish = map(lambda date: date.strftime(config.DATE_FORMAT), (read_start, read_finish))
                books.append(Book(id=row["book_id"],
                                  name=row["book_name"],
                                  category_id=row['category_id'],
                                  category_name=row['category_name'],
                                  read_start=read_start,
                                  read_finish=read_finish))
    return books






