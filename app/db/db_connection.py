from psycopg2 import pool
from psycopg2.extras import RealDictCursor

from config import settings

connection_pool = None


def init_pool():
    global connection_pool

    if connection_pool is None:
        connection_pool = pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            host=settings.HOST,
            port=settings.PORT,
            dbname=settings.DBNAME,
            user=settings.DBNAME,
            password=settings.PASSWORD
        )


def get_db_connection():
    if connection_pool is None:
        init_pool()

    return connection_pool.getconn()


def release_db_connection(connection):
    connection_pool.putconn(connection)


def execute_query(query, params=None, fetchone=False, fetchall=False):
    connection = get_db_connection()

    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params or ())

            result = None

            if fetchone:
                result = cursor.fetchone()

            if fetchall:
                result = cursor.fetchall()

            connection.commit()
            return result

    except Exception:
        connection.rollback()
        raise

    finally:
        release_db_connection(connection)


def init_db():
    execute_query(
        """
        CREATE TABLE IF NOT EXISTS users (
            telegram_id BIGINT PRIMARY KEY,
            tg_nick VARCHAR(255),
            role VARCHAR(50) NOT NULL DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    execute_query(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS users_tg_nick_unique
        ON users (LOWER(tg_nick))
        WHERE tg_nick IS NOT NULL;
        """
    )

    execute_query(
        """
        CREATE TABLE IF NOT EXISTS materials (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author_id BIGINT REFERENCES users(telegram_id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )