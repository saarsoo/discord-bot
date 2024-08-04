import os
import asyncpg


DATABASE_CONNECTION_PARAMS = {
    "database": os.environ.get(
        "POSTGRES_DB"
    ),  # defaulted to POSTGRES_USER if not provided
    "user": os.environ.get("POSTGRES_USER"),
    "password": os.environ.get("POSTGRES_PASSWORD"),
    "host": os.environ.get("POSTGRES_HOST"),
    "port": os.environ.get("POSTGRES_PORT"),
    "ssl": os.environ.get("POSTGRES_SSL"),
}


async def validate_connection():
    try:
        params = {
            param: value
            for param, value in DATABASE_CONNECTION_PARAMS.items()
            if param != "password"
        }
        print(f"Connecting to the database using the following parameters: {params}")
        # Establish the connection
        conn = await asyncpg.connect(**DATABASE_CONNECTION_PARAMS)

        try:
            # Define the insert query and the data to be inserted
            query = """
                SELECT * FROM users
            """

            # Execute the insert query
            await conn.fetch(query)

            print("Connection to the database was successful.")
        finally:
            # Close the connection
            await conn.close()
    except asyncpg.PostgresError as e:
        print(f"An error occurred while trying to connect to the database.\n{e}")


async def add_user(user_id: int, user_name: str):
    print(f"Adding user {user_name} with ID {user_id} to the database...")

    try:
        # Establish the connection
        conn = await asyncpg.connect(**DATABASE_CONNECTION_PARAMS)

        try:
            # Define the insert query and the data to be inserted
            upsert_query = """
                INSERT INTO users (user_id, user_name) VALUES ($1, $2)
                ON CONFLICT (user_id) DO UPDATE
                SET user_name = EXCLUDED.user_name
            """
            upsert_data = (user_id, user_name)

            # Execute the insert query
            await conn.execute(upsert_query, *upsert_data)

            print(f"User {user_name} with ID {user_id} was added to the database.")
        finally:
            # Close the connection
            await conn.close()

    except asyncpg.PostgresError as e:
        print(f"An error occurred: {e}")


async def add_profession(user_id: int, profession: str):
    print(f"Adding profession {profession} for user {user_id} to the database...")

    try:
        # Establish the connection
        conn = await asyncpg.connect(**DATABASE_CONNECTION_PARAMS)

        try:
            # Define the insert query and the data to be inserted
            upsert_query = """
                INSERT INTO professions (user_id, profession_name)
                VALUES ($1, $2)
                ON CONFLICT (user_id, profession_name) DO NOTHING
            """
            upsert_data = (user_id, profession)

            # Execute the insert query
            await conn.execute(upsert_query, *upsert_data)

            print(
                f"Profession {profession} for user {user_id} was added to the database."
            )
        finally:
            # Close the connection
            await conn.close()

    except asyncpg.PostgresError as e:
        print(f"An error occurred: {e}")


async def remove_profession(user_id: int, profession: str):
    print(f"Removing profession {profession} for user {user_id} from the database...")

    try:
        # Establish the connection
        conn = await asyncpg.connect(**DATABASE_CONNECTION_PARAMS)

        try:
            # Define the insert query and the data to be inserted
            query = """
                DELETE FROM professions WHERE user_id = $1 AND profession_name = $2
            """
            data = (user_id, profession)

            # Execute the insert query
            await conn.execute(query, *data)

            print(
                f"Profession {profession} for user {user_id} was removed from the database."
            )
        finally:
            # Close the connection
            await conn.close()

    except asyncpg.PostgresError as e:
        print(f"An error occurred: {e}")


async def get_user_professions(user_id: int):
    print(f"Getting professions for user {user_id} from the database...")

    try:
        # Establish the connection
        conn = await asyncpg.connect(**DATABASE_CONNECTION_PARAMS)

        try:
            # Define the insert query and the data to be inserted
            query = """
                SELECT profession_name FROM professions WHERE user_id = $1
            """
            data = (user_id,)

            # Execute the insert query
            professions = await conn.fetch(query, *data)

            print(f"Professions for user {user_id} were retrieved from the database.")
            return professions
        finally:
            # Close the connection
            await conn.close()

    except asyncpg.PostgresError as e:
        print(f"An error occurred: {e}")


async def get_all_professions() -> list[dict]|None:
    print(f"Getting all professions from the database...")

    try:
        # Establish the connection
        conn = await asyncpg.connect(**DATABASE_CONNECTION_PARAMS)

        try:
            # Define the insert query and the data to be inserted
            query = """
                SELECT user_id, user_name, profession_name
                FROM professions
                JOIN users USING (user_id)
            """

            # Execute the insert query
            professions = await conn.fetch(query)

            print(f"All professions were retrieved from the database.")
            return professions
        finally:
            # Close the connection
            await conn.close()

    except asyncpg.PostgresError as e:
        print(f"An error occurred: {e}")
