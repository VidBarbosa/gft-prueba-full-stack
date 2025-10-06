SET search_path TO btg, public;

CREATE TABLE IF NOT EXISTS cliente (
  id          SERIAL PRIMARY KEY,
  nombre      VARCHAR(100) NOT NULL,
  apellidos   VARCHAR(120) NOT NULL,
  ciudad      VARCHAR(80)  NOT NULL
);

CREATE TABLE IF NOT EXISTS sucursal (
  id          SERIAL PRIMARY KEY,
  nombre      VARCHAR(120) NOT NULL UNIQUE,
  ciudad      VARCHAR(80)  NOT NULL
);

CREATE TABLE IF NOT EXISTS producto (
  id            SERIAL PRIMARY KEY,
  nombre        VARCHAR(120) NOT NULL UNIQUE,
  tipoProducto  btg.tipo_producto NOT NULL
);

CREATE TABLE IF NOT EXISTS disponibilidad (
  idSucursal  INT NOT NULL,
  idProducto  INT NOT NULL,
  PRIMARY KEY (idSucursal, idProducto),
  CONSTRAINT fk_disp_sucursal FOREIGN KEY (idSucursal) REFERENCES sucursal(id) ON DELETE CASCADE,
  CONSTRAINT fk_disp_producto FOREIGN KEY (idProducto) REFERENCES producto(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS inscripcion (
  idProducto  INT NOT NULL,
  idCliente   INT NOT NULL,
  PRIMARY KEY (idProducto, idCliente),
  CONSTRAINT fk_insc_producto FOREIGN KEY (idProducto) REFERENCES producto(id) ON DELETE CASCADE,
  CONSTRAINT fk_insc_cliente  FOREIGN KEY (idCliente)  REFERENCES cliente(id)  ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS visitan (
  idSucursal  INT NOT NULL,
  idCliente   INT NOT NULL,
  fechaVisita DATE NOT NULL DEFAULT CURRENT_DATE,
  PRIMARY KEY (idSucursal, idCliente, fechaVisita),
  CONSTRAINT fk_vis_sucursal FOREIGN KEY (idSucursal) REFERENCES sucursal(id) ON DELETE CASCADE,
  CONSTRAINT fk_vis_cliente  FOREIGN KEY (idCliente)  REFERENCES cliente(id)  ON DELETE CASCADE
);
