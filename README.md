# MedControl - Gestão de Medicamentos

Este projeto é um sistema desenvolvido para auxiliar no controle de horários e administração de medicamentos, garantindo que o tratamento seja seguido corretamente.

## Informações do Projeto
- **Versão:** 0.1.0
- **Data:** 12/04/2026
- **Status:** Cadastro funcional, banco de dados SQLite configurado.

##  Funcionalidades Atuais
- [x] **Cadastro de Perfil:** Armazenamento de dados do paciente.
- [x] **Cadastro de Medicamentos:** Registro detalhado com:
    - Nome e Dose
    - Tipo (Comprimido, Gotas, etc.)
    - Via de administração
    - Intervalo de horas
    - Horário de início
- [x] **Persistência de Dados:** Uso de banco de dados SQL (SQLite).

##  Tecnologias Utilizadas
- **Linguagem:** Python 3.13
- **Interface:** CustomTkinter
- **Banco de Dados:** SQLite3

##  Próximos Passos (Roadmap)
-  Implementar sistema de alertas automáticos.
- Criar histórico de administração (checar doses tomadas/puladas).
- Adicionar campo de justificativa para doses não administradas.