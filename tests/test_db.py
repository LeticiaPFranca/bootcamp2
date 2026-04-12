from src.database import MedDatabase

def test_adicionar_medicamento():
    db = MedDatabase(":memory:") 
    sucesso = db.adicionar_medicamento("Dipirona", "500mg", "Oral", "8h")
    assert sucesso is True