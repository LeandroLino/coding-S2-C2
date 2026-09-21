"""
Exercise 6 setup — creates and populates the MySQL `analistas`/
`incidentes` tables used by the broken-access-control API (Aulas 3, 6
e 8/A01).
"""
from diplomat.mysql import run_many, run_write

ANALISTAS = [
    (1, "ana", "key-ana-001", 5),
    (2, "bruno", "key-bruno-002", 2),
]

INCIDENTES = [
    (1, 1, "Brute force SSH", "critica", "aberto"),
    (2, 2, "Phishing no RH", "media", "aberto"),
]


def setup_mysql() -> None:
    """(Re)create and populate `analistas`/`incidentes`, so this is re-runnable."""
    run_write("DROP TABLE IF EXISTS incidentes")
    run_write("DROP TABLE IF EXISTS analistas")
    run_write(
        """
        CREATE TABLE analistas (
            id INT PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            api_key VARCHAR(100) NOT NULL UNIQUE,
            nivel INT NOT NULL
        )
        """
    )
    run_write(
        """
        CREATE TABLE incidentes (
            id INT PRIMARY KEY,
            dono_id INT NOT NULL,
            titulo VARCHAR(200) NOT NULL,
            severidade VARCHAR(20) NOT NULL,
            status VARCHAR(20) NOT NULL,
            FOREIGN KEY (dono_id) REFERENCES analistas(id)
        )
        """
    )
    run_many(
        "INSERT INTO analistas (id, nome, api_key, nivel) VALUES (%s, %s, %s, %s)",
        ANALISTAS,
    )
    run_many(
        "INSERT INTO incidentes (id, dono_id, titulo, severidade, status) VALUES (%s, %s, %s, %s, %s)",
        INCIDENTES,
    )


if __name__ == "__main__":
    setup_mysql()
    print(f"MySQL populated: {len(ANALISTAS)} analistas, {len(INCIDENTES)} incidentes")
