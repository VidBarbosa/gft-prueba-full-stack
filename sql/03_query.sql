SET search_path TO btg, public;

SELECT DISTINCT c.nombre
FROM cliente c
JOIN inscripcion i ON i.idCliente = c.id
WHERE NOT EXISTS (
  SELECT 1
  FROM visitan v
  WHERE v.idCliente = c.id
    AND NOT EXISTS (
      SELECT 1
      FROM disponibilidad d
      WHERE d.idSucursal = v.idSucursal
        AND d.idProducto  = i.idProducto
    )
)
ORDER BY c.nombre;
