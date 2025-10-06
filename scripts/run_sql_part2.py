import os
import psycopg2

DEFAULTS = {
    "host": os.getenv("PGHOST", "localhost"),
    "port": int(os.getenv("PGPORT", "5432")),
    "user": os.getenv("PGUSER", "btg"),
    "password": os.getenv("PGPASSWORD", "btg123"),
    "dbname": os.getenv("PGDATABASE", "BTG"),
}

SEED_SQL = r"""
SET search_path TO btg, public;

INSERT INTO sucursal (nombre, ciudad) VALUES
  ('Bogotá - Centro', 'Bogotá'),
  ('Bogotá - Norte',  'Bogotá'),
  ('Medellín - Poblado', 'Medellín'),
  ('Cali - Sur', 'Cali')
ON CONFLICT (nombre) DO NOTHING;

INSERT INTO producto (nombre, tipoProducto) VALUES
  ('FPV_BTG_PACTUAL_RECAUDADORA', 'FPV'),
  ('FPV_BTG_PACTUAL_ECOPETROL',   'FPV'),
  ('DEUDAPRIVADA',                'FIC'),
  ('FDO-ACCIONES',                'FIC'),
  ('CDT Tradicional',             'CDT'),
  ('Cuenta Ahorros',              'CUENTA'),
  ('Tarjeta Crédito',             'TARJETA')
ON CONFLICT (nombre) DO NOTHING;

INSERT INTO cliente (nombre, apellidos, ciudad) VALUES
  ('Ana',   'Pérez',  'Bogotá'),
  ('Bruno', 'Díaz',   'Medellín'),
  ('Carla', 'López',  'Bogotá'),
  ('Diego', 'Rivas',  'Cali'),
  ('Elena', 'Gómez',  'Bogotá')
ON CONFLICT DO NOTHING;

-- Bogotá - Norte ofrece TODO
INSERT INTO disponibilidad
SELECT s.id, p.id FROM sucursal s CROSS JOIN producto p WHERE s.nombre='Bogotá - Norte'
ON CONFLICT DO NOTHING;

-- Bogotá - Centro ofrece: Cuenta, Tarjeta, CDT
INSERT INTO disponibilidad
SELECT s.id, p.id FROM sucursal s
JOIN producto p ON p.nombre IN ('Cuenta Ahorros','Tarjeta Crédito','CDT Tradicional')
WHERE s.nombre='Bogotá - Centro'
ON CONFLICT DO NOTHING;

-- Medellín - Poblado ofrece: DeudaPrivada, FDO-ACCIONES, CDT
INSERT INTO disponibilidad
SELECT s.id, p.id FROM sucursal s
JOIN producto p ON p.nombre IN ('DEUDAPRIVADA','FDO-ACCIONES','CDT Tradicional')
WHERE s.nombre='Medellín - Poblado'
ON CONFLICT DO NOTHING;

-- Cali - Sur ofrece: Recaudadora
INSERT INTO disponibilidad
SELECT s.id, p.id FROM sucursal s
JOIN producto p ON p.nombre='FPV_BTG_PACTUAL_RECAUDADORA'
WHERE s.nombre='Cali - Sur'
ON CONFLICT DO NOTHING;

-- Visitas
INSERT INTO visitan (idSucursal, idCliente)
SELECT s.id, c.id
FROM sucursal s, cliente c
WHERE c.nombre='Ana' AND s.nombre IN ('Bogotá - Centro','Bogotá - Norte')
ON CONFLICT DO NOTHING;

INSERT INTO visitan (idSucursal, idCliente)
SELECT s.id, c.id
FROM sucursal s, cliente c
WHERE c.nombre='Bruno' AND s.nombre IN ('Medellín - Poblado')
ON CONFLICT DO NOTHING;

INSERT INTO visitan (idSucursal, idCliente)
SELECT s.id, c.id
FROM sucursal s, cliente c
WHERE c.nombre='Carla' AND s.nombre IN ('Bogotá - Norte')
ON CONFLICT DO NOTHING;

INSERT INTO visitan (idSucursal, idCliente)
SELECT s.id, c.id
FROM sucursal s, cliente c
WHERE c.nombre='Diego' AND s.nombre IN ('Cali - Sur')
ON CONFLICT DO NOTHING;

INSERT INTO visitan (idSucursal, idCliente)
SELECT s.id, c.id
FROM sucursal s, cliente c
WHERE c.nombre='Elena' AND s.nombre IN ('Bogotá - Centro','Medellín - Poblado')
ON CONFLICT DO NOTHING;

-- Inscripciones
INSERT INTO inscripcion (idProducto, idCliente)
SELECT p.id, c.id FROM producto p, cliente c
WHERE c.nombre='Ana' AND p.nombre IN ('CDT Tradicional','DEUDAPRIVADA')
ON CONFLICT DO NOTHING;

INSERT INTO inscripcion (idProducto, idCliente)
SELECT p.id, c.id FROM producto p, cliente c
WHERE c.nombre='Bruno' AND p.nombre IN ('FDO-ACCIONES')
ON CONFLICT DO NOTHING;

INSERT INTO inscripcion (idProducto, idCliente)
SELECT p.id, c.id FROM producto p, cliente c
WHERE c.nombre='Carla' AND p.nombre IN ('Tarjeta Crédito')
ON CONFLICT DO NOTHING;

INSERT INTO inscripcion (idProducto, idCliente)
SELECT p.id, c.id FROM producto p, cliente c
WHERE c.nombre='Diego' AND p.nombre IN ('FPV_BTG_PACTUAL_RECAUDADORA')
ON CONFLICT DO NOTHING;

INSERT INTO inscripcion (idProducto, idCliente)
SELECT p.id, c.id FROM producto p, cliente c
WHERE c.nombre='Elena' AND p.nombre IN ('Cuenta Ahorros','FDO-ACCIONES')
ON CONFLICT DO NOTHING;
"""

def run_seed():
    conn = psycopg2.connect(**DEFAULTS)
    try:
        with conn.cursor() as cur:
            print("==> Running SEED…")
            cur.execute(SEED_SQL)
        conn.commit()
        print("✅ Seed ejecutado correctamente")
    finally:
        conn.close()

if __name__ == "__main__":
    run_seed()
