import keyring

def set_key(service, username, password):
    keyring.set_password(service, username, password)

if __name__ == '__main__':
    # Example usage
    service = input("Service: ")
    username = input("Username: ")
    password = input("Password: ")
    set_key(service, username, password)
    print("Key set in Keychain.")