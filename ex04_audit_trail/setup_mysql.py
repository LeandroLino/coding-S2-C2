"""
Exercise 4 setup — creates and populates the MySQL `usuarios` table
used by the privilege-change transaction (Aulas 2, 3 e 8/A09).
"""
from diplomat.mysql import run_many, run_write

USUARIOS = [
    (1, "ana", "ana@x.com", 5),
    (2, "bruno", "bruno@x.com", 2),
    (3, "caio", "caio@x.com", 1),
]


def setup_mysql() -> None:
    """(Re)create and populate `usuarios`, so this is re-runnable."""
    run_write("DROP TABLE IF EXISTS usuarios")
    run_write(
        """
        CREATE TABLE usuarios (
            id INT PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            email VARCHAR(150) NOT NULL UNIQUE,
            nivel_acesso INT NOT NULL
        )
        """
    )
    run_many(
        "INSERT INTO usuarios (id, nome, email, nivel_acesso) VALUES (%s, %s, %s, %s)",
        USUARIOS,
    )


if __name__ == "__main__":
    setup_mysql()
    print(f"MySQL populated: {len(USUARIOS)} usuarios")
