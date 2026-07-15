import asyncpg
from config.settings import HOST, PORT, DBNAME, USER, PASSWORD

pool: asyncpg.Pool | None = None


async def create_pool():
    global pool
    pool = await asyncpg.create_pool(
        host=HOST,
        port=PORT,
        database=DBNAME,
        user=USER,
        password=PASSWORD,
        min_size=1,
        max_size=30,
    )
    return pool


async def close_pool():
    if pool:
        await pool.close()


async def get_or_create_member(telegram_id: int, tg_nick: str | None,
                               full_name: str = '') -> asyncpg.Record:
    """Возвращает пользователя, создаёт если его нет."""
    nick = tg_nick.lstrip('@').lower() if tg_nick else None
    async with pool.acquire() as conn:
        member = await conn.fetchrow(
            "SELECT * FROM members WHERE telegram_id = $1", telegram_id
        )
        if member is None:
            member = await conn.fetchrow(
                """
                INSERT INTO members (telegram_id, tg_nick, full_name)
                VALUES ($1, $2, $3)
                RETURNING *
                """,
                telegram_id, nick, full_name,
            )
        return member


async def update_subscription_status(telegram_id: int, is_subscribed: bool):
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE members
            SET is_subscribed = $2, last_subscription_check = NOW()
            WHERE telegram_id = $1
            """,
            telegram_id, is_subscribed,
        )

async def create_files(beatmaker_id: int, telegram_file_id: str, telegram_file_unique_id: str, file_name: str,
                       type_id: int):
    async with pool.acquire() as conn:
        await conn.execute(
            '''
            INSERT INTO files (beatmaker_id, telegram_file_id, telegram_file_unique_id, file_name, type_id)
            VALUES ($1, $2, $3, $4)
            ''',
            beatmaker_id, telegram_file_id, telegram_file_unique_id, file_name, type_id
        )

async def is_user_banned(telegram_id: int) -> bool:
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT is_banned FROM members WHERE telegram_id = $1", telegram_id
        )
        return bool(row and row["is_banned"])

async def is_admin_member(telegram_id: int) -> bool:
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            'SELECT role FROM members WHERE telegram_id = $1', telegram_id
        )
        return (row and row["role"]) == 'admin'

async def get_telegram_file_id_from_author(author_id: int) -> list[str]:
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            'SELECT telegram_file_id FROM files WHERE beatmaker_id = $1', author_id
        )
        return [row["telegram_file_id"] for row in rows]
