BEGIN;

DELETE FROM btg.visitan;
DELETE FROM btg.inscripcion;
DELETE FROM btg.disponibilidad;

DELETE FROM btg.cliente;
DELETE FROM btg.producto;
DELETE FROM btg.sucursal;

COMMIT;
