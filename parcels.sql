-- Create a owner and parcels table in geospatial database
CREATE SCHEMA IF NOT EXISTS geospatial;
DROP TABLE IF EXISTS geospatial.parcel;
DROP TABLE IF EXISTS geospatial.owner;
CREATE TABLE IF NOT EXISTS geospatial.owner
(
    owner_id INT PRIMARY KEY,
    phone VARCHAR(256) NOT NULL,
    f_name VARCHAR(256) NOT NULL,
    l_name VARCHAR(256) NOT NULL,
    email VARCHAR(256)
);

CREATE TABLE IF NOT EXISTS geospatial.parcel
(
    gid SERIAL PRIMARY KEY,
    owner_id INT NOT NULL,
    area DOUBLE PRECISION,
    county VARCHAR(256) NOT NULL,
    district VARCHAR(256) NOT NULL,
    sold BOOLEAN DEFAULT FALSE,
    price VARCHAR(256),
    CONSTRAINT fk_owner FOREIGN KEY(owner_id) REFERENCES geospatial.owner(owner_id),
    geom GEOMETRY(Polygon, 21037)
);

CREATE INDEX parcel_geom_idx ON geospatial.parcel USING GIST(geom);
GRANT INSERT, UPDATE, DELETE, REFERENCES ON geospatial.parcel to nygma;