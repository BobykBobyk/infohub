import aiomysql


async def get_db_pool():
    return await aiomysql.create_pool(
        host='localhost',
        port=3306,
        user='root',
        password='password',
        db='db',
        minsize=5,
        maxsize=10
    )


async def execute_query(query: str, params=None):
    pool = await get_db_pool()
    try:
        async with pool.acquire() as connection:
            async with connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, params)
                if query.strip().lower().startswith('select'):
                    return await cursor.fetchall()
                elif query.strip().lower().startswith(('insert', 'update', 'delete')):
                    await connection.commit()
                    return {'message': 'Query executed succesfully'}
    finally:
        pool.close()
        await pool.wait_closed()


async def create_database():
    await execute_query("""
    CREATE DATABASE IF NOT EXISTS db;
    """)


async def create_table():
    await execute_query("""
    CREATE TABLE IF NOT EXISTS table(
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) NOT NULL PRIMARY KEY,
    order_list VARCHAR(255) NOT NULL,
    name_product VARCHAR(255),
    numeric_product INT,
    price_product FLOAT,
    datetime VARCHAR(255)
    );
    """)


async def startup_event():
    await create_database()
    await create_table()
