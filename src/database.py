import sqlite3

class MedDatabase:
    def __init__(self, db_name="medcontrol.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        # Tabela de Perfil
        cursor.execute('''CREATE TABLE IF NOT EXISTS perfil (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            nome TEXT, 
                            idade INTEGER, 
                            cuidadores TEXT)''')
        # Tabela de Medicamentos
        cursor.execute('''CREATE TABLE IF NOT EXISTS medicamentos (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            nome TEXT, 
                            dose TEXT, 
                            tipo TEXT, 
                            quantidade REAL, 
                            via TEXT, 
                            intervalo_horas INTEGER, 
                            horario_inicio TEXT)''')
        # Tabela de Histórico (Nova!)
        cursor.execute('''CREATE TABLE IF NOT EXISTS historico (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            id_medicamento INTEGER, 
                            data_hora TEXT, 
                            status TEXT, 
                            justificativa TEXT)''')
        self.conn.commit()

    def salvar_perfil(self, nome, idade, cuidadores):
        self.conn.execute("INSERT INTO perfil (nome, idade, cuidadores) VALUES (?, ?, ?)", (nome, idade, cuidadores))
        self.conn.commit()

    def salvar_medicamento(self, nome, dose, tipo, qtd, via, intervalo, inicio):
        self.conn.execute("INSERT INTO medicamentos (nome, dose, tipo, quantidade, via, intervalo_horas, horario_inicio) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                          (nome, dose, tipo, qtd, via, intervalo, inicio))
        self.conn.commit()

    def buscar_medicamentos(self):
        return self.conn.execute("SELECT * FROM medicamentos").fetchall()

    def registrar_administracao(self, id_med, data, status, motivo=None):
        self.conn.execute("INSERT INTO historico (id_medicamento, data_hora, status, justificativa) VALUES (?, ?, ?, ?)", 
                          (id_med, data, status, motivo))
        self.conn.commit()