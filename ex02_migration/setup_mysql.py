"""
Exercise 2 setup — creates and populates the MySQL `ativos`/`alertas`
tables used as the migration source (Aulas 1, 2 e 3).

`ativos` 1 --N `alertas`: each asset can have many alerts.
"""
from diplomat.mysql import run_many, run_write

ATIVOS = [
    (1, "SRV-WEB01", "192.168.1.10", "alta"),
    (2, "PC-RH03", "192.168.1.45", "baixa"),
]

ALERTAS = [
    (1, 1, "BRUTE_FORCE", "critica"),
    (2, 1, "PORT_SCAN", "alta"),
    (3, 2, "XSS", "media"),
]


def setup_mysql() -> None:
    """(Re)create and populate `ativos`/`alertas`, so this is re-runnable."""
    run_write("DROP TABLE IF EXISTS alertas")
    run_write("DROP TABLE IF EXISTS ativos")
    run_write(
        """
        CREATE TABLE ativos (
            id INT PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            ip VARCHAR(45) NOT NULL UNIQUE,
            criticidade ENUM('baixa', 'media', 'alta') NOT NULL
        )
        """
    )
    run_write(
        """
        CREATE TABLE alertas (
            id INT PRIMARY KEY,
            ativo_id INT NOT NULL,
            tipo VARCHAR(50) NOT NULL,
            severidade VARCHAR(20) NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ativo_id) REFERENCES ativos(id)
        )
        """
    )
    run_many(
        "INSERT INTO ativos (id, nome, ip, criticidade) VALUES (%s, %s, %s, %s)",
        ATIVOS,
    )
    run_many(
        "INSERT INTO alertas (id, ativo_id, tipo, severidade) VALUES (%s, %s, %s, %s)",
        ALERTAS,
    )


if __name__ == "__main__":
    setup_mysql()
    print(f"MySQL populated: {len(ATIVOS)} ativos, {len(ALERTAS)} alertas")
