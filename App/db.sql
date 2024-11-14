--BASE DE DATOS DESCRITA EN TEXTO PARA CONOCER LOS ATRIBUTOS DE CADA TABLA/ENTIDAD



-- Definición de los ENUMs
CREATE TYPE Category_Plant AS ENUM ('planta_interior', 'arbol_fruta');
CREATE TYPE Role AS ENUM ('usuario', 'gestor_vivero', 'administrador');
CREATE TYPE Type_Plant AS ENUM ('arbusto', 'flor', 'arbol');
CREATE TYPE Type_reaction AS ENUM ('like', 'love', 'funny', 'sad', 'angry');
CREATE TYPE Category_Product AS ENUM ('decoracion', 'utiles', 'promocionales');

CREATE TYPE Info AS (
  name VARCHAR,
  description TEXT
);--

-- Tablas
--IMPORTANCIA 100%
CREATE TABLE Users (
  id_user SERIAL PRIMARY KEY,
  name VARCHAR,
  email VARCHAR UNIQUE,
  password VARCHAR,
  ubication JSONB,
  img BYTEA,
  role Role,
);--

CREATE TABLE Plants (
  id_plant SERIAL PRIMARY KEY,
  info Info,
  hora_de_riego VARCHAR,
  category CategoryPlant,
  tipo Type_Plant,
  img VARCHAR
);--

CREATE TABLE User_Plant (
  id_user INTEGER REFERENCES Users(id_user),
  id_plant INTEGER REFERENCES Plants(id_plant),
  PRIMARY KEY (id_user, id_plant)
);--

--IMPORTANCIA 80%
CREATE TABLE Nursery (
  id SERIAL PRIMARY KEY,
  info Info,  -- Campo de tipo composite 'info'
  ubication VARCHAR,
  img VARCHAR,
  id_manager INTEGER REFERENCES Users(id_user)
);--

CREATE TABLE Nursery_Plant (
  id_plants INTEGER REFERENCES Plants(id),
  id_nursery INTEGER REFERENCES Nursery(id),
  PRIMARY KEY (id_plants, id_nursery)
);--


--IMPORTANCIA 50%
CREATE TABLE Publications (
  id_publication SERIAL PRIMARY KEY,
  id_author INTEGER REFERENCES usuarios(id_user),
  title VARCHAR,
  description TEXT,
  media BYTEA
);

CREATE TABLE Reactions (
  id_reaction SERIAL PRIMARY KEY,
  id_publication INTEGER REFERENCES Publications(id_publication),
  reaction Type_reaction
);--

--IMPORTANCIA 20%
CREATE TABLE Products (
  id_product SERIAL PRIMARY KEY,
  name VARCHAR,
  quantity INTEGER,
  price INTEGER,
  description TEXT,
  img BYTEA,
  categoria Category_Product
);--

CREATE TABLE Carts (
  id_cart SERIAL PRIMARY KEY,
  id_user INTEGER REFERENCES Users(id_user),
  total FLOAT
);--

CREATE TABLE Cart_Product (
  id_cart INTEGER REFERENCES Carts(id_cart),
  id_product INTEGER REFERENCES Products(id_product),
  PRIMARY KEY (id_cart, id_product)
);--

CREATE TABLE Sales (
  id_sale SERIAL PRIMARY KEY,
  total INTEGER
);--

CREATE TABLE Sale_Product (
  id_sale INTEGER REFERENCES Sales(id_sale),
  id_product INTEGER REFERENCES Products(id_product),
  PRIMARY KEY (id_sale, id_product)
);--

--FUNCTIONS
CREATE OR REPLACE FUNCTION add_user(
    user_name VARCHAR,
    user_email VARCHAR,
    user_password VARCHAR,
    user_ubication JSONB,
    user_img BYTEA,
    user_role Role
) RETURNS INTEGER AS $$
DECLARE
    new_user_id INTEGER;
BEGIN
    INSERT INTO Users (name, email, password, ubication, img, role)
    VALUES (user_name, user_email, user_password, user_ubication, user_img, user_role)
    RETURNING id_user INTO new_user_id;
    
    RETURN new_user_id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION add_plant_to_user(
    user_id INTEGER,
    plant_name VARCHAR,
    plant_description TEXT,
    plant_hora_de_riego VARCHAR,
    plant_category CategoryPlant,
    plant_tipo Type_Plant,
    plant_img VARCHAR
) RETURNS INTEGER AS $$
DECLARE
    new_plant_id INTEGER;
BEGIN
    INSERT INTO Plants (info, hora_de_riego, category, tipo, img)
    VALUES (ROW(plant_name, plant_description), plant_hora_de_riego, plant_category, plant_tipo, plant_img)
    RETURNING id_plant INTO new_plant_id;
    
    INSERT INTO User_Plant (id_user, id_plant)
    VALUES (user_id, new_plant_id);
    
    RETURN new_plant_id;
END;
$$ LANGUAGE plpgsql;

-- Function to get all plants for a specific user
CREATE OR REPLACE FUNCTION get_user_plants(user_id INTEGER) 
RETURNS TABLE(id_plant INTEGER, info JSONB, hora_de_riego VARCHAR, category CategoryPlant, tipo Type_Plant, img VARCHAR) 
AS $$
BEGIN
    RETURN QUERY
    SELECT p.id_plant, p.info, p.hora_de_riego, p.category, p.tipo, p.img
    FROM Plants p
    JOIN User_Plant up ON p.id_plant = up.id_plant
    WHERE up.id_user = user_id;
END;
$$ LANGUAGE plpgsql;

-- Function to get a specific plant for a specific user
CREATE OR REPLACE FUNCTION get_user_plant(user_id INTEGER, plant_id INTEGER)
RETURNS TABLE(id_plant INTEGER, info JSONB, hora_de_riego VARCHAR, category CategoryPlant, tipo Type_Plant, img VARCHAR) 
AS $$
BEGIN
    RETURN QUERY
    SELECT p.id_plant, p.info, p.hora_de_riego, p.category, p.tipo, p.img
    FROM Plants p
    JOIN User_Plant up ON p.id_plant = up.id_plant
    WHERE up.id_user = user_id AND p.id_plant = plant_id;
END;
$$ LANGUAGE plpgsql;
