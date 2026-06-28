import asyncpg
from config.settings import HOST, PORT, DBNAME, USER, PASSWORD

pool: asyncpg.Pool | None = None


async def init_db():
    global pool
    pool = await asyncpg.create_pool(
        host=HOST,
        port=int(PORT),
        database=DBNAME,
        user=USER,
        password=PASSWORD,
        min_size=1,
        max_size=10,
    )


async def close_db():
    if pool:
        await pool.close()


# ---------- members ----------

async def get_member(telegram_id: int):
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM members WHERE telegram_id = $1", telegram_id
        )


async def get_member_by_id(member_id: int):
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM members WHERE id = $1", member_id
        )


async def create_member(telegram_id: int, tg_nick: str | None,
                        full_name: str = "", role: str = "student"):
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            """
            INSERT INTO members (telegram_id, tg_nick, full_name, role)
            VALUES ($1, $2, $3, $4)
            RETURNING *
            """,
            telegram_id, tg_nick, full_name, role
        )


# ---------- invites ----------

async def create_invite(code: str, inviter_id: int):
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            """
            INSERT INTO invites (code, inviter_id)
            VALUES ($1, $2)
            RETURNING *
            """,
            code, inviter_id
        )


async def get_invite(code: str):
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM invites WHERE code = $1", code
        )


async def use_invite(code: str, invited_member_id: int):
    """Атомарно помечает инвайт использованным (защита от гонок)."""
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            """
            UPDATE invites
            SET is_used = TRUE,
                invited_member_id = $2,
                used_at = NOW()
            WHERE code = $1 AND is_used = FALSE
            RETURNING *
            """,
            code, invited_member_id
        )