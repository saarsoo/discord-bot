CREATE TABLE IF NOT EXISTS users (
  user_id BIGINT PRIMARY KEY,
  user_name VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS professions (
  user_id BIGINT,
  profession_name VARCHAR NOT NULL,

  PRIMARY KEY (user_id, profession_name)
);

CREATE TABLE IF NOT EXISTS recipes (
  user_id BIGINT,
  recipe_name VARCHAR NOT NULL,

  PRIMARY KEY (user_id, recipe_name)
);