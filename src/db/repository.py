import os
import asyncpg


class Database:
    """Класс для взаимодействия с PostgreSQL."""

    def __init__(self):
        self.pool = None

    async def connect(self):
        """Создание пула подключений к базе данных."""

        self.pool = await asyncpg.create_pool(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "lost_found"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD"),
            min_size=1,
            max_size=10
        )

        print("Подключение к PostgreSQL установлено.")

    async def close(self):
        """Закрытие пула подключений."""

        if self.pool is not None:
            await self.pool.close()
            self.pool = None

    async def register_user(self, telegram_id, username):
        """Регистрация пользователя или обновление его username."""

        async with self.pool.acquire() as connection:
            user = await connection.fetchrow(
                """
                INSERT INTO users (telegram_id, username)
                VALUES ($1, $2)
                ON CONFLICT (telegram_id)
                DO UPDATE SET username = EXCLUDED.username
                RETURNING id, telegram_id, username
                """,
                telegram_id,
                username
            )

            return user

    async def get_categories(self):
        """Получение списка всех категорий."""

        async with self.pool.acquire() as connection:
            categories = await connection.fetch(
                """
                SELECT id, name
                FROM categories
                ORDER BY id
                """
            )

            return categories

    async def get_user(self, telegram_id):
        """Получение пользователя по Telegram ID."""

        async with self.pool.acquire() as connection:
            user = await connection.fetchrow(
                """
                SELECT id, telegram_id, username, created_at
                FROM users
                WHERE telegram_id = $1
                """,
                telegram_id
            )

            return user
