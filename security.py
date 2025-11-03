# security.py
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken

def _derivar_chave(chave_texto: str) -> bytes:
    """Deriva uma chave de criptografia válida a partir de uma senha de texto."""
    # Usamos SHA-256 para criar um hash da senha
    hash_obj = hashlib.sha256(chave_texto.encode('utf-8'))
    # O Fernet espera uma chave de 32 bytes codificada em base64
    return base64.urlsafe_b64encode(hash_obj.digest())

def criptografar_mensagem(mensagem: str, chave_texto: str) -> bytes:
    """Criptografa uma mensagem usando a chave fornecida."""
    chave_derivada = _derivar_chave(chave_texto)
    f = Fernet(chave_derivada)
    return f.encrypt(mensagem.encode('utf-8'))

def descriptografar_mensagem(token_cifrado: bytes, chave_texto: str) -> str | None:
    """Descriptografa um token usando a chave fornecida."""
    try:
        chave_derivada = _derivar_chave(chave_texto)
        f = Fernet(chave_derivada)
        mensagem_decifrada = f.decrypt(token_cifrado)
        return mensagem_decifrada.decode('utf-8')
    except InvalidToken:
        # Isso acontece se a chave estiver errada!
        return None