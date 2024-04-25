from dataclasses import dataclass
import aiosqlite
import config
from users import insert_user
import logging
from typing import Iterable
from books import Book

logger = logging.getLogger(__name__)


@dataclass
class BookVoteResult:
    book_name: str
    score: int


@dataclass
class VoteResults:
    vote_start: str
    vote_finish: str
    leaders: list[BookVoteResult]


@dataclass
class Voting:
    id: int
    vote_start: str
    vote_finish: str


async def get_actual_voting() -> Voting | None:
    sql = '''SELECT id, voting_start, voting_finish 
    FROM voting WHERE voting_start <= current_date AND voting_finish >= current_date 
        ORDER BY voting_start LIMIT 1'''

    async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(sql) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return None
            return Voting(
                id=row['id'],
                vote_start=row['voting_start'],
                vote_finish=row['voting_finish']
            )


async def save_vote(telegram_user_id: int, books: Iterable[Book]) -> None:
    await insert_user(telegram_user_id)
    actual_voting = await get_actual_voting()
    if actual_voting is None:
        logger.warning('No actual voting in save_vote()')
        return
    sql = ("""INSERT OR REPLACE INTO vote (vote_id, user_id, first_book, second_book, third_book)
           VALUES(:vote_id, :user_id, :first_book, :second_book, :third_book)""")
    books = tuple(books)
    async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
        await db.execute(sql, {'vote_id': actual_voting.id, 'user_id': telegram_user_id, 'first_book': books[0].id, 'second_book': books[1].id, 'third_book': books[2].id})
        await db.commit()


async def get_leaders() -> VoteResults:
    actual_voting = await get_actual_voting()
    vote_result = VoteResults(vote_start=actual_voting.vote_start,
                              vote_finish=actual_voting.vote_finish,
                              leaders=[])
    sql = '''
    SELECT t2.*, b.name as book_name 
    FROM (SELECT t.book_id, sum(t.score) from(
        SELECT first_book as book_id, 3*COUNT(*) as score
        FROM vote v
        WHERE vote_id = (:voting_id)
        group by first_book
        
        UNION
        
        SELECT second_book as book_id, 2*COUNT(*) as score
        FROM vote v
        WHERE vote_id = (:voting_id)
        group by second_book
        
        UNION
        
        SELECT third_book as book_id, 1*COUNT(*) as score
        FROM vote v
        WHERE vote_id = (:voting_id)
        group by third_book
    )t 
    group by book_id order by sum(t.score) desc
    limit 10) t2
    LEFT JOIN book b on b.id=t2.book_id
    '''
    async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(sql, {"voting_id": actual_voting.id}) as cursor:
            rows = await cursor.fetchall()
            for row in rows:
                vote_result.leaders.append(BookVoteResult(
                    book_name=row['book_name'],
                    score=row['sum(t.score)']
                ))
    return vote_result
