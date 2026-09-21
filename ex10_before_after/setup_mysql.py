"""
Exercise 10 setup — seeds `usuarios_ex10`, a dedicated table isolated
from ex04/ex06's own `usuarios`/`analistas` tables so app_vulneravel.py
and app_seguro.py can run side by side against the shared mysql-lab
container without clobbering other exercises' data.
"""
from diplomat.mysql import run_many, run_write

USUARIOS = [
    (1, "ana", "ana@x.com", "senha123", "key-ana-010", 5),
    (2, "bruno", "bruno@x.com", "senha456", "key-bruno-020", 2),
    (3, "caio", "caio@x.com", "senha789", "key-caio-030", 1),
]


def setup_mysql() -> None:
    """(Re)create and reseed `usuarios_ex10` so every run starts clean —
    important here because the DELETE exploit actually removes a row."""
    run_write("DROP TABLE IF EXISTS usuarios_ex10")
    run_write(
        """
        CREATE TABLE usuarios_ex10 (
            id INT PRIMARY KEY,
            nome VARCHAR(50) NOT NULL,
            email VARCHAR(100) NOT NULL,
            senha VARCHAR(100) NOT NULL,
            api_key VARCHAR(50) NOT NULL UNIQUE,
            nivel_acesso INT NOT NULL
        )
        """
    )
    run_many(
        "INSERT INTO usuarios_ex10 (id, nome, email, senha, api_key, nivel_acesso) VALUES (%s, %s, %s, %s, %s, %s)",
        USUARIOS,
    )


if __name__ == "__main__":
    setup_mysql()
    print(f"MySQL populated: {len(USUARIOS)} usuarios_ex10")
