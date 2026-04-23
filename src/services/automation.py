import paramiko
import sqlite3
import csv
import os
from datetime import datetime

class RelatorioAutomation:
    def __init__(self):
        # Parâmetros da Missão
        self.host = "seu.servidor.sftp.com"
        self.user = "admin_medcontrol"
        self.password = "senha_segura_bootcamp"
        self.db_path = "medcontrol.db"
        self.temp_file = "relatorio_diario.csv"

    def gerar_payload(self):
        """Extrai dados do histórico do MedControl para CSV"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # Seleciona o histórico de administração do idoso
            cursor.execute("SELECT * FROM historico_remedios") 
            dados = cursor.fetchall()
            
            with open(self.temp_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Medicamento", "Hora", "Status", "Justificativa"])
                writer.writerows(dados)
            conn.close()
            return True
        except Exception:
            return False

    def executar_missao_sftp(self):
        """Pipeline Programático: Conectar -> Listar -> Enviar"""
        if not self.gerar_payload():
            return "ERRO: Falha ao gerar relatório local (Payload)."

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            # 1. CONECTAR (Criptografia SSH-2 / RFC 4253)
            print(f"Iniciando túnel seguro com {self.host}...")
            client.connect(self.host, username=self.user, password=self.password, timeout=10)
            sftp = client.open_sftp()

            # 2. LISTAR (Mapear diretório disponível)
            print("Mapeando diretório remoto...")
            sftp.listdir('.') 

            # 3. ENVIAR (Push do relatório)
            remoto_path = f"/uploads/saude/{datetime.now().strftime('%Y%m%d')}_meds.csv"
            print(f"Enviando payload para: {remoto_path}")
            sftp.put(self.temp_file, remoto_path)
            
            sftp.close()
            return "SUCESSO: Relatório enviado via SFTP!"

        # --- Matriz de Diagnóstico (Resiliência) ---
        except paramiko.AuthenticationException:
            return "SINTOMA: Bad Auth (Credenciais Inválidas)."
        except Exception:
            return "SINTOMA: Servidor Indisponível ou falha de rede."
        finally:
            client.close()
            if os.path.exists(self.temp_file):
                os.remove(self.temp_file) # Limpeza de arquivos temporários
