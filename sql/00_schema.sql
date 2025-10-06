CREATE SCHEMA IF NOT EXISTS btg AUTHORIZATION btg;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type t JOIN pg_namespace n ON n.oid=t.typnamespace
                 WHERE t.typname = 'tipo_producto' AND n.nspname='btg') THEN
    CREATE TYPE btg.tipo_producto AS ENUM ('FPV','FIC','CDT','CUENTA','TARJETA');
  END IF;
END$$;
