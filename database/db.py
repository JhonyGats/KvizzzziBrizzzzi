import aiosqlite
import json
from config import DB_NAME

async def create_tables():
    async with aiosqlite.connect(DB_NAME) as db:
        # для хранения состояния текущей игры пользователя:
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (
            user_id INTEGER PRIMARY KEY,
            question_index INTEGER,
            question_order TEXT,
            options_order TEXT,
            score INTEGER
        )''')
        # для хранения последнего результата (статистика)
        await db.execute('''CREATE TABLE IF NOT EXISTS results (
            user_id INTEGER PRIMARY KEY,
            last_score INTEGER
        )''')
        await db.commit()

async def get_state(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT question_index, question_order, options_order, score FROM quiz_state WHERE user_id = ?', (user_id,)) as cur:
            row = await cur.fetchone()
            if row:
                qi, qord, oord, score = row
                return {
                    "question_index": qi,
                    "question_order": json.loads(qord) if qord else None,
                    "options_order": json.loads(oord) if oord else None,
                    "score": score
                }
            return None

async def save_state(user_id, question_index, question_order, options_order, score):
    qord_json = json.dumps(question_order) if question_order is not None else None
    oord_json = json.dumps(options_order) if options_order is not None else None
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index, question_order, options_order, score) VALUES (?, ?, ?, ?, ?)',
                         (user_id, question_index, qord_json, oord_json, score))
        await db.commit()

async def delete_state(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('DELETE FROM quiz_state WHERE user_id = ?', (user_id,))
        await db.commit()

async def save_result(user_id, score):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR REPLACE INTO results (user_id, last_score) VALUES (?, ?)', (user_id, score))
        await db.commit()

async def get_result(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT last_score FROM results WHERE user_id = ?', (user_id,)) as cur:
            row = await cur.fetchone()
            return row[0] if row else None
