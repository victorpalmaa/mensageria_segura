# Mensageria Segura

Um chat de terminal seguro com criptografia (simulada) ponta-a-ponta.

Serviço de mensageria em modo texto (terminal) escrito em Python para comunicação segura e cifrada entre usuários, utilizando MongoDB Atlas como banco de dados.

## 🚀 Guia Rápido

### Requisitos

- Python 3.9+
- Pip (gerenciador de pacotes do Python)
- Uma conta gratuita no MongoDB Atlas

### Configuração e Execução

**⚠️ O projeto NÃO funcionará sem o arquivo de configuração `.env`. Siga estes passos.**

#### 1. Clone o Repositório

```bash
git clone https://github.com/victorpalmaa/mensageria_segura.git
cd mensageria_segura
```

#### 2. Instale as Dependências

Um arquivo `requirements.txt` é fornecido com todas as bibliotecas necessárias.

```bash
# Instala todas as bibliotecas do projeto
pip3 install -r requirements.txt
```

#### 3. Crie o Arquivo de Configuração `.env`

**Este é o passo mais importante.**

1. Crie um arquivo chamado `.env` na raiz do projeto.
2. Obtenha sua String de Conexão (URI) do MongoDB Atlas. (Veja a seção Configuração abaixo).
3. Cole a URI dentro do arquivo `.env`, como no exemplo:

```
MONGO_URI="mongodb+srv://<username>:<password>@<cluster-url>/?retryWrites=true&w=majority"
```

#### 4. Execute o Programa

Com o `.env` criado e as dependências instaladas, execute o arquivo `main.py`:

```bash
python3 main.py
```

O programa irá se conectar ao banco e mostrar o menu principal:

```
Conexão com o MongoDB estabelecida com sucesso!
--- Sistema de Mensageria Segura ---
1. Registrar-se
2. Fazer Login
3. Sair
```

## 🔧 Configuração (MongoDB Atlas)

Para que o programa se conecte, você precisa de uma `MONGO_URI`.

1. **Crie um Cluster**: Crie um cluster gratuito (M0) no MongoDB Atlas.

2. **Crie um Usuário de Banco de Dados**:
   - Vá em Security → Database Access.
   - Crie um usuário (ex: `usuarioprojeto`).
   - **IMPORTANTE**: Use uma senha sem caracteres especiais (ex: `trabalho123`) para evitar erros de URL.

3. **Libere o Acesso de IP**:
   - Vá em Security → Network Access.
   - Adicione a regra `0.0.0.0/0` (Allow Access From Anywhere).

4. **Obtenha a URI**:
   - Vá em Database → Connect → Drivers.
   - Copie a string de conexão (URI) e cole-a no seu arquivo `.env`, substituindo `<username>` e `<password>` pelo usuário que você criou.

## 📂 Estrutura do Projeto

```
mensageria_segura/
├── .gitignore         # Ignora o .env e arquivos de cache
├── auth.py            # Funções de Registrar e Login
├── db_manager.py      # Classe Singleton para gerenciar a conexão com o Mongo
├── main.py            # Ponto de entrada, menu principal
├── security.py        # Funções de Criptografar e Descriptografar
└── requirements.txt   # Lista de dependências (pymongo, cryptography, etc)
```

### Componentes Principais

- **db_manager.py**: Gerencia a conexão com o MongoDB, incluindo a correção de SSL/TLS (`tlsCAFile=ca`) para macOS.
- **auth.py**: Lida com o registro de usuários (usando werkzeug para hash de senhas) e autenticação.
- **security.py**: Usa `cryptography.fernet` (AES) para cifrar e decifrar as mensagens. A chave é derivada da senha fornecida pelo usuário usando SHA-256.

## 💬 Formato dos Dados (MongoDB)

O projeto utiliza duas coleções principais no banco `projeto_chat_seguro`.

### Coleção Users

Armazena as credenciais de login.

```json
{
  "_id": "ObjectId(...)",
  "username": "@alice",
  "password_hash": "pbkdf2:sha256:..."
}
```

### Coleção Messages

Armazena as mensagens criptografadas.

```json
{
  "_id": "ObjectId(...)",
  "from_user": "@alice",
  "to_user": "@bob",
  "message_content": "gAAAAABl... (dado binário cifrado)",
  "status": "não lido" | "lido",
  "timestamp": "ISODate(...)"
}
```

## 🔄 Fluxo de Comunicação (Lógica)

1. Usuário A se registra/loga.
2. Usuário B se registra/loga.
3. Usuário A escolhe "Escrever Mensagem":
   - Informa destinatário: "@bob"
   - Escreve a mensagem (min 50 chars)
   - Informa uma chave secreta (ex: "segredo123")
4. O app usa a chave "segredo123" para CIFRAR a mensagem.
5. A mensagem é salva no MongoDB com o status "não lido".

---

6. Usuário B loga e escolhe "Ler Novas Mensagens".
7. O app lista as mensagens "não lidas" (De: @alice - [data/hora]).
8. Usuário B escolhe a mensagem de @alice.
9. O app solicita a CHAVE SECRETA.
10. Se a chave estiver errada ("segredo_errado"): O app avisa.
11. Se a chave estiver correta ("segredo123"): O app DECIFRA a mensagem, exibe o conteúdo e atualiza o status para "lido" no banco.

## 🐛 Solução de Problemas (Troubleshooting)

### Erro: `--- ERRO DE CONEXÃO ---`

Este é o erro mais comum. Se você o vir, verifique **Nesta Ordem**:

1. **Senha Incorreta / Caracteres Especiais**: A `MONGO_URI` no seu `.env` está 100% correta? A senha que você criou no Atlas é a mesma? Tente usar uma senha só com letras e números (ex: `trabalho123`).

2. **Acesso de IP**: Você liberou o `0.0.0.0/0` no "Network Access" do Atlas?

3. **Problema de SSL (macOS)**: O código em `db_manager.py` já inclui a correção `tlsCAFile=certifi.where()`. Verifique se a biblioteca `certifi` está instalada (`pip3 install certifi`).