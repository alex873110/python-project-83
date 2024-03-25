CREATE TABLE urls (
    id SERIAL PRIMARY KEY,
    name varchar(255),
    created_at date
);

CREATE TABLE url_checks (
    id SERIAL PRIMARY KEY,
    url_id bigint REFERENCES urls(id),
    status_code int,
    h1 varchar(255),
    title varchar(255),
    description varchar(1000),
    created_at TIMESTAMP NOT NULL
);
