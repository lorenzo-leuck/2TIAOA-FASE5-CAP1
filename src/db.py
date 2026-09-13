import sqlite3

class Database:
    def __init__(self, db_path='cardioia.db'):
        self.db_path = db_path

    def connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_table(self, table_name, columns):
        """
        Create table if it doesn't exist.

        columns: dict of {column_name: sql_type}
        Example: {'temperatura': 'REAL', 'umidade': 'REAL', 'ativo': 'BOOLEAN'}

        'id' INTEGER PRIMARY KEY and 'timestamp' DATETIME are added automatically.
        """
        col_defs = ['id INTEGER PRIMARY KEY AUTOINCREMENT']
        for name, dtype in columns.items():
            col_defs.append(f'{name} {dtype}')
        col_defs.append('timestamp DATETIME DEFAULT CURRENT_TIMESTAMP')

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                {', '.join(col_defs)}
            )
        ''')
        conn.commit()
        conn.close()

    def insert(self, table_name, data):
        """Insert a row. data: dict of {column_name: value}"""
        cols = ', '.join(data.keys())
        placeholders = ', '.join('?' for _ in data)
        values = list(data.values())

        conn = self.connection()
        cursor = conn.cursor()
        cursor.execute(
            f'INSERT INTO {table_name} ({cols}) VALUES ({placeholders})', values
        )
        conn.commit()
        row_id = cursor.lastrowid
        conn.close()
        return row_id

    def fetch_all(self, table_name, order_by='timestamp ASC'):
        conn = self.connection()
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM {table_name} ORDER BY {order_by}')
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def fetch_where(self, table_name, where, values):
        conn = self.connection()
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM {table_name} WHERE {where} ORDER BY timestamp DESC', values)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def fetch_latest(self, table_name):
        conn = self.connection()
        cursor = conn.cursor()
        cursor.execute(
            f'SELECT * FROM {table_name} ORDER BY timestamp DESC LIMIT 1'
        )
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
