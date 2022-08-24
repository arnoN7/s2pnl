CREATE TABLE "project" (
  "id" SERIAL PRIMARY KEY,
  "name" varchar(64),
  "created_at" timestamp DEFAULT 'now()',
  "details" text
);

CREATE TABLE "filtered_address" (
  "id" SERIAL PRIMARY KEY,
  "address" varchar(64),
  "created_at" timestamp DEFAULT 'now()',
  "details" text
);

CREATE TABLE "supplier" (
  "id" SERIAL PRIMARY KEY,
  "name" varchar(64),
  "address" varchar(128),
  "postcode" int,
  "city" varchar(64),
  "email" varchar(64),
  "siret" varchar(32),
  "phone" varchar(256),
  "created_at" timestamp DEFAULT 'now()',
  "details" text
);

CREATE TABLE "bill" (
  "id" SERIAL PRIMARY KEY,
  "amount" float,
  "date" timestamp DEFAULT 'now()',
  "dtn_end_amort" timestamp DEFAULT 'now()',
  "file" varchar(256),
  "details" text,
  "supplier_id" int,
  "project_id" int,
  "cat_id" int
);

CREATE TABLE "categorie" (
  "id" SERIAL PRIMARY KEY,
  "name" varchar(64),
  "created_at" timestamp DEFAULT 'now()',
  "details" text
);

CREATE TABLE "revenue" (
  "id" SERIAL PRIMARY KEY,
  "amount" float,
  "client_id" int,
  "project_id" int,
  "created_at" timestamp DEFAULT 'now()',
  "details" text
);

CREATE TABLE "client" (
  "id" SERIAL PRIMARY KEY,
  "name" varchar(128),
  "address" varchar(128),
  "postcode" int,
  "city" varchar(64),
  "phone" varchar(32),
  "created_at" timestamp DEFAULT 'now()',
  "details" text
);

CREATE UNIQUE INDEX ON "bill" ("file");

CREATE UNIQUE INDEX ON "client" ("name");

ALTER TABLE "bill" ADD FOREIGN KEY ("supplier_id") REFERENCES "supplier" ("id");

ALTER TABLE "bill" ADD FOREIGN KEY ("project_id") REFERENCES "project" ("id");

ALTER TABLE "bill" ADD FOREIGN KEY ("cat_id") REFERENCES "categorie" ("id");

ALTER TABLE "revenue" ADD FOREIGN KEY ("client_id") REFERENCES "client" ("id");

ALTER TABLE "revenue" ADD FOREIGN KEY ("project_id") REFERENCES "project" ("id");
