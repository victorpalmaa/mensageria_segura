# db_manager.py
import os
import pymongo
import sys
import certifi  # <<< NOVO: Importa a biblioteca de certificados

from dotenv import load_dotenv

class DatabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            
            load_dotenv()
            mongo_uri = os.getenv("MONGO_URI")

            if not mongo_uri:
                print("Erro fatal: Variável de ambiente MONGO_URI não encontrada.")
                print("Verifique se seu arquivo .env está correto.")
                sys.exit(1)

            # <<< NOVO: Pega o caminho para o pacote de certificados
            ca = certifi.where() 
            
            try:
                # <<< NOVO: Adiciona 'tlsCAFile=ca' para forçar o uso dos certificados
                cls._instance.client = pymongo.MongoClient(
                    mongo_uri, 
                    serverSelectionTimeoutMS=5000,
                    tlsCAFile=ca  # <-- Esta é a correção
                )
                
                cls._instance.client.server_info() 
                print("Conexão com o MongoDB estabelecida com sucesso!")
                
            except pymongo.errors.ServerSelectionTimeoutError:
                print("\n--- ERRO DE CONEXÃO (PYMONGO) ---")
                print("O Python não conseguiu se conectar ao MongoDB.")
                print("Verifique se a SENHA no arquivo .env está 100% correta (sem caracteres especiais).")
                print("O firewall ou a rede podem estar bloqueando o Python (mesmo que o 'nc' funcione).")
                sys.exit(1)
            except Exception as e:
                print(f"Um erro inesperado ocorreu: {e}")
                sys.exit(1)

            cls._instance.db = cls._instance.client["projeto_chat_seguro"]
            cls._instance.users_collection = cls._instance.db["Users"]
            cls._instance.messages_collection = cls._instance.db["Messages"]
            
        return cls._instance

    def get_db(self):
        return self.db
    
    def get_users_collection(self):
        return self.users_collection
    
    def get_messages_collection(self):
        return self.messages_collection