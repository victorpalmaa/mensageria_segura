# auth.py

# 1. Importa a CLASSE, não a instância
from db_manager import DatabaseManager 
from werkzeug.security import generate_password_hash, check_password_hash

# 2. Pede ao Singleton pela instância (ele vai criar ou retornar a existente)
db_manager = DatabaseManager()

# 3. Agora sim, pega a coleção a partir da instância
users_collection = db_manager.get_users_collection()


def registrar_usuario() -> bool:
    """Solicita dados e registra um novo usuário no banco."""
    print("\n--- Registro de Novo Usuário ---")
    username = input("Digite seu @ (nome de usuário único): ").strip() # .strip() remove espaços
    password = input("Digite sua senha de login: ")

    # Validação simples
    if not username or not password:
        print("Erro: Usuário e senha não podem estar em branco.")
        return False

    # 1. Verifica se o usuário já existe
    if users_collection.find_one({"username": username}):
        print("Erro: Este nome de usuário já está em uso. Tente outro.")
        return False

    # 2. Cria o hash da senha
    hashed_password = generate_password_hash(password)

    # 3. Cria o "documento" (POJO/dicionário) do usuário
    novo_usuario = {
        "username": username,
        "password_hash": hashed_password
    }

    # 4. Insere no banco
    users_collection.insert_one(novo_usuario)
    print(f"Usuário {username} registrado com sucesso!")
    return True

def login_usuario() -> str | None:
    """Solicita dados, autentica e retorna o nome do usuário se o login for bem-sucedido."""
    print("\n--- Login ---")
    username = input("Digite seu @ (nome de usuário): ").strip()
    password = input("Digite sua senha de login: ")

    # 1. Busca o usuário no banco
    usuario_db = users_collection.find_one({"username": username})

    # 2. Verifica se o usuário existe e se a senha está correta
    if usuario_db and check_password_hash(usuario_db["password_hash"], password):
        print(f"Login bem-sucedido! Bem-vindo, {username}.")
        return username  # Retorna o nome do usuário logado
    
    print("Erro: Usuário ou senha inválidos.")
    return None