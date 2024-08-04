CREATE TABLE users (
  user_id BIGINT PRIMARY KEY,
  user_name VARCHAR NOT NULL
);

CREATE TABLE professions (
    user_id BIGINT,
    profession_name VARCHAR NOT NULL,

    PRIMARY KEY (user_id, profession_name)
);