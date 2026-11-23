import os
import asyncpg


class Database:
    """Класс для взаимодействия с PostgreSQL."""

    def init(self):
        self.pool = None

    async def connect(self):
        """Создание пула подключений."""

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
        """Закрытие подключений."""

        if self.pool is not None:
            await self.pool.close()
            self.pool = None

    async def register_user(self, telegram_id, username):
        """Регистрация или обновление пользователя."""

        async with self.pool.acquire() as connection:
            return await connection.fetchrow(
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

    async def get_user(self, telegram_id):
        """Получение пользователя."""

        async with self.pool.acquire() as connection:
            return await connection.fetchrow(
                """
                SELECT id, telegram_id, username, created_at
                FROM users
                WHERE telegram_id = $1
                """,
                telegram_id
            )

    async def get_categories(self):
        """Получение всех категорий."""

        async with self.pool.acquire() as connection:
            return await connection.fetch(
                """
                SELECT id, name
                FROM categories
                ORDER BY id
                """
            )

    async def create_report(
        self,
        telegram_id,
        category_id,
        report_type,
        title,
        description,
        event_date,
        latitude,
        longitude,
        address=None
    ):
        """Создание объявления."""

        if report_type not in ("lost", "found"):
            raise ValueError("Недопустимый тип объявления.")

        async with self.pool.acquire() as connection:
            async with connection.transaction():

                user = await connection.fetchrow(
                    """
                    SELECT id
                    FROM users
                    WHERE telegram_id = $1
                    """,
                    telegram_id
                )

                if user is None:
                    raise ValueError("Пользователь не зарегистрирован.")

                category = await connection.fetchrow(
                    """
                    SELECT id
                    FROM categories
                    WHERE id = $1
                    """,
                    category_id
                )

                if category is None:
                    raise ValueError("Категория не найдена.")

                report = await connection.fetchrow(
                    """
                    INSERT INTO reports (
                        user_id,
                        category_id,
                        report_type,
                        title,
                        description,
                        event_date,
                        location,
                        address
                    )
                    VALUES (
                        $1, $2, $3, $4, $5, $6,
                        ST_SetSRID(
                            ST_MakePoint($7, $8), 4326
                        )::geography,
                        $9
                    )
                    RETURNING id, title, report_type, created_at
                    """,
                    user["id"], category_id,
                    report_type,
                    title,
                    description,
                    event_date,
                    longitude,
                    latitude,
                    address
                )

                return report