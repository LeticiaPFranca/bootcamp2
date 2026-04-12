import sqlite3

class MedDatabase:
    def __init__(self, db_name="medcontrol.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS medicamentos (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nome TEXT NOT NULL,
                            dose TEXT NOT NULL,
                            via TEXT NOT NULL,
                            frequencia TEXT NOT NULL
                          )''')
        self.conn.commit()

    def adicionar_medicamento(self, nome, dose, via, frequencia):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO medicamentos (nome, dose, via, frequencia) VALUES (?,?,?,?)", 
                       (nome, dose, via, frequencia))
        self.conn.commit()
        return True