# messaging.py
from datetime import datetime
from bson.binary import Binary
from typing import List, Tuple

from db_manager import DatabaseManager
from security import criptografar_mensagem, descriptografar_mensagem

# Obter instância do DB e coleções
db_manager = DatabaseManager()
users_collection = db_manager.get_users_collection()
messages_collection = db_manager.get_messages_collection()


def iniciar_envio_mensagem(remetente: str) -> None:
    """Fluxo para enviar uma mensagem criptografada de 'remetente' para outro usuário."""
    print("\n--- Enviar Nova Mensagem ---")
    to_user = input("Digite o @ do destinatário: ").strip()

    # Valida destinatário
    if not to_user:
        print("Erro: usuário destinatário inválido.")
        return

    usuario_dest = users_collection.find_one({"username": to_user})
    if not usuario_dest:
        print(f"Erro: usuário '{to_user}' não encontrado.")
        return

    # Ler mensagem (mínimo 50 caracteres)
    while True:
        mensagem = input("Digite a mensagem (mínimo 50 caracteres): ").strip()
        if len(mensagem) < 50:
            print(f"Mensagem muito curta ({len(mensagem)} caracteres). Digite ao menos 50 caracteres.")
        else:
            break

    # Ler chave
    chave = input("Informe a chave criptográfica para cifrar a mensagem: ").strip()
    if not chave:
        print("Erro: chave inválida.")
        return

    # Criptografar
    try:
        token = criptografar_mensagem(mensagem, chave)  # bytes
    except Exception as e:
        print(f"Erro ao criptografar a mensagem: {e}")
        return

    # Armazenar no MongoDB (usando Binary para bytes)
    documento = {
        "from": remetente,
        "to": to_user,
        "mensagem": Binary(token),     # token é bytes; Binary armazena corretamente
        "status": "não lido",
        "timestamp": datetime.now()
    }

    result = messages_collection.insert_one(documento)
    if result.inserted_id:
        print("Mensagem enviada e armazenada com sucesso.")
    else:
        print("Erro: não foi possível salvar a mensagem.")


def _listar_mensagens_limpa(cursor) -> List[Tuple]:
    """
    Recebe um cursor e retorna lista de tuplas (index, _id, remetente, timestamp)
    para exibição limpa.
    """
    lista = []
    for i, doc in enumerate(cursor, start=1):
        remetente = doc.get("from", "Desconhecido")
        ts = doc.get("timestamp")
        if isinstance(ts, datetime):
            ts_str = ts.strftime("%d/%m/%Y %H:%M")
        else:
            ts_str = str(ts)
        lista.append((i, doc["_id"], remetente, ts_str))
    return lista


def iniciar_leitura_mensagens(usuario: str) -> None:
    """Fluxo para listar e ler mensagens do usuário (novas ou antigas)."""
    print("\n--- Ler Minhas Mensagens ---")
    print("1. Ler novas mensagens (não lidas)")
    print("2. Ler mensagens antigas (lidas)")
    escolha = input("Escolha uma opção (1 ou 2): ").strip()

    if escolha == "1":
        status_busca = "não lido"
    elif escolha == "2":
        status_busca = "lido"
    else:
        print("Opção inválida.")
        return

    # Buscar mensagens do usuário e ordenar por timestamp descendente
    cursor = messages_collection.find({"to": usuario, "status": status_busca}).sort("timestamp", -1)
    docs = list(cursor)

    if not docs:
        print(f"Nenhuma mensagem com status '{status_busca}' encontrada.")
        return

    # Mostrar lista limpa
    lista_limpa = _listar_mensagens_limpa(docs)
    print("\nMensagens encontradas:")
    for idx, _id, remetente, ts_str in lista_limpa:
        print(f"{idx}. De: @{remetente} - {ts_str}")

    # Map index -> document _id
    index_to_id = {str(idx): _id for idx, _id, _, _ in lista_limpa}

    escolha_idx = input("Digite o número da mensagem que deseja abrir (ou ENTER para cancelar): ").strip()
    if not escolha_idx:
        print("Operação cancelada.")
        return

    if escolha_idx not in index_to_id:
        print("Índice inválido.")
        return

    doc_id = index_to_id[escolha_idx]
    documento = messages_collection.find_one({"_id": doc_id})
    if not documento:
        print("Erro: mensagem não encontrada no banco.")
        return

    # Solicitar chave e tentar descriptografar (permitir re-tentativas)
    tentativas = 0
    while True:
        chave = input("Informe a chave criptográfica para decifrar a mensagem: ").strip()
        if not chave:
            print("Chave inválida.")
            resposta = input("Deseja tentar novamente? (s/n): ").strip().lower()
            if resposta != 's':
                return
            continue

        conteudo_cifrado = documento.get("mensagem")
        # conteudo_cifrado vem como bson.binary.Binary (subclasse de bytes)
        try:
            mensagem_decifrada = descriptografar_mensagem(conteudo_cifrado, chave)
        except Exception as e:
            mensagem_decifrada = None
            print(f"Erro durante a decifragem: {e}")

        if mensagem_decifrada is None:
            print("Chave incorreta ou mensagem corrompida.")
            tentativas += 1
            resposta = input("A chave está correta? Deseja tentar novamente? (s/n): ").strip().lower()
            if resposta != 's':
                print("Operação cancelada.")
                return
            # else: loop para tentar novamente
        else:
            # Exibir mensagem e atualizar status se necessário
            ts = documento.get("timestamp")
            ts_str = ts.strftime("%d/%m/%Y %H:%M") if isinstance(ts, datetime) else str(ts)
            print("\n--- Mensagem ---")
            print(f"De: @{documento.get('from')} - {ts_str}")
            print("Conteúdo:")
            print(mensagem_decifrada)
            print("-----------------")

            # Atualizar status para 'lido' se estava 'não lido'
            if documento.get("status") == "não lido":
                messages_collection.update_one({"_id": doc_id}, {"$set": {"status": "lido"}})
            return
