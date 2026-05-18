# 💊 MedControl

> Aplicativo desktop para controle de medicamentos de idosos — com alertas automáticos, histórico de doses e integração com ViaCEP + Google Maps.

🔗 **[Acesse a página do projeto aqui](https://SEU_USUARIO.github.io/medcontrol)**  
_(substitua `SEU_USUARIO` pelo seu usuário do GitHub)_

---

## ✨ Funcionalidades

- ⏰ **Alertas automáticos** de dose no horário exato
- 📋 **Histórico completo** de administrações (com justificativas)
- 👤 **Perfil do idoso** com nome, idade e cuidadores
- 📍 **Busca de CEP** via API pública do ViaCEP (preenchimento automático)
- 🗺️ **Integração Google Maps** — botão "Traçar Rota" com um clique
- 🗄️ **Banco de dados local** em SQLite (sem nuvem, sem assinatura)

---

## 🖥️ Requisitos

- Python **3.10** ou superior
- Windows 10/11, macOS 12+ ou Linux

---

## 🚀 Como instalar e executar

### 1. Clone o repositório

```bash
git clone https://github.com/SEU_USUARIO/medcontrol.git
cd medcontrol
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Execute a migração do banco de dados

_(só precisa fazer isso uma vez)_

```bash
python migrate.py
```

### 4. Inicie o aplicativo

```bash
python main.py
```

---

## 🧪 Executar os testes

```bash
pytest test_medcontrol.py -v
```

---

## 📁 Estrutura do projeto

```
medcontrol/
├── main.py                    # Ponto de entrada do aplicativo
├── migrate.py                 # Script de migração do banco
├── requirements.txt           # Dependências Python
├── medcontrol.db              # Banco SQLite (gerado após migrate.py)
├── index.html                 # Página web do projeto (GitHub Pages)
├── src/
│   ├── database/
│   │   ├── __init__.py
│   │   └── db.py              # Acesso ao banco de dados
│   ├── services/
│   │   ├── __init__.py
│   │   ├── viacep.py          # Integração com API ViaCEP
│   │   └── maps.py            # Integração com Google Maps
│   └── ui/
│       ├── __init__.py
│       └── perfil.py          # Tela de perfil (customtkinter)
└── test_medcontrol.py         # Testes automatizados (pytest)
```

---

## 🌐 Deploy (GitHub Pages)

A página do projeto (`index.html`) é publicada automaticamente via **GitHub Pages**.

Para ativar:
1. Vá em **Settings → Pages** no seu repositório
2. Em **Source**, selecione `Deploy from a branch`
3. Escolha a branch `main` e a pasta `/root`
4. Clique em **Save**

Seu link ficará disponível em:  
`https://github.com/LeticiaPFranca/bootcamp2/tree/entrega-intermediaria`

---

## 📦 Gerar release para download

1. Compacte a pasta do projeto em `.zip` (excluindo `medcontrol.db` e `__pycache__`)
2. No GitHub, vá em **Releases → Create a new release**
3. Adicione a tag `v1.0.0`, título e descrição
4. Anexe o `.zip` como asset
5. Publique — o botão "Baixar" no site apontará para este release

---

## 🔗 Integração com API

Este projeto consome a **API pública do ViaCEP** (`https://viacep.com.br`):

- Endpoint: `GET https://viacep.com.br/ws/{CEP}/json/`
- Sem autenticação necessária
- Retorna: logradouro, bairro, cidade, estado

---

## 📄 Licença

MIT © MedControl — desenvolvido com ❤️ para cuidadores
