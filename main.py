# main.py
import auth

def menu_principal():
    usuario_logado = None

    while True:
        if not usuario_logado:
            print("\n--- Sistema de Mensageria Segura ---")
            print("1. Registrar-se")
            print("2. Fazer Login")
            print("3. Sair")
            escolha = input("Escolha uma opção: ")

            if escolha == '1':
                auth.registrar_usuario()
            elif escolha == '2':
                usuario_logado = auth.login_usuario()
            elif escolha == '3':
                print("Até logo!")
                break
            else:
                print("Opção inválida.")
        else:
            # PARABÉNS! Você completou a Task 1.
            # O código da Task 2 (Enviar Mensagem) e Task 3 (Ler Mensagem)
            # começará aqui, dentro deste 'else'.
            print(f"\n--- Menu Principal (Logado como: {usuario_logado}) ---")
            print("1. Escrever nova mensagem (Task 2)")
            print("2. Ler minhas mensagens (Task 3)")
            print("3. Deslogar (Logout)")
            
            escolha_logado = input("Escolha uma opção: ")

            if escolha_logado == '1':
                print("... (Aqui chamará a função de ENVIAR da Task 2) ...")
                pass
            elif escolha_logado == '2':
                print("... (Aqui chamará a função de LER da Task 3) ...")
                pass
            elif escolha_logado == '3':
                print(f"Deslogando usuário {usuario_logado}...")
                usuario_logado = None
            else:
                print("Opção inválida.")

if __name__ == "__main__":
    menu_principal()