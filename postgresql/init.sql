-- Connect first, then:

CREATE TABLE IF NOT EXISTS news (
  date          TIMESTAMP,      -- or TEXT if you prefer
  title         TEXT,
  url           TEXT    PRIMARY KEY,
  summary       TEXT,
  source_feed   TEXT
);

CREATE TABLE IF NOT EXISTS x_posts (
  date          TIMESTAMP,
  title         TEXT,
  url           TEXT    PRIMARY KEY,
  summary       TEXT,
  source_feed   TEXT
);

CREATE TABLE IF NOT EXISTS truth (
  date          TIMESTAMP,
  title         TEXT,
  url           TEXT    PRIMARY KEY,
  summary       TEXT,
  source_feed   TEXT
);
