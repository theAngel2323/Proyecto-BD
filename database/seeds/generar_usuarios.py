import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import bcrypt
from config.database import db_cursor


USUARIOS = [
    {"username": "usr_admin",   "password": "admin123"},
    {"username": "dr_mendoza",  "password": "medico123"},
    {"username": "dr_garcia",   "password": "medico123"},
    {"username": "enf_juarez",  "password": "enf123"},
    {"username": "enf_flores",  "password": "enf123"},
]


def hashear_password(password: str) -> str:
    """Genera un hash bcrypt seguro para la contraseña dada."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def main():
    print("=" * 50)
    print("  Generando contraseñas hasheadas...")
    print("=" * 50)

    with db_cursor() as cursor:
        for usuario in USUARIOS:
            hashed = hashear_password(usuario["password"])
            cursor.execute("""
                UPDATE usuario_sistema
                SET password_hash = %s
                WHERE username = %s
            """, (hashed, usuario["username"]))
            print(f"    {usuario['username']} → hash generado")

    print("\n Todos los usuarios actualizados con contraseña segura.")



if __name__ == "__main__":
    main()