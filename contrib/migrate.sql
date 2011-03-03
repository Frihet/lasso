alter table "lasso_customer_originalseller" add column "origin_id" integer REFERENCES "lasso_global_origin" ("id");
alter table "lasso_warehandling_unitwork" add column "entry_id" integer REFERENCES "lasso_warehandling_entry" ("id");
alter table "lasso_warehandling_unitwork" add column "withdrawal_id" integer REFERENCES "lasso_warehandling_withdrawal" ("id");

alter table "lasso_warehandling_entryrow" add column "origin_id" integer REFERENCES "lasso_global_origin" ("id");
update "lasso_warehandling_entryrow" set origin_id = (select origin_id from "lasso_warehandling_entry" where "lasso_warehandling_entry".id = "lasso_warehandling_entryrow"."entry_id");
alter table "lasso_warehandling_entry" drop column "origin_id";

alter table lasso_warehandling_transportcondition rename to lasso_global_transportcondition;

CREATE TABLE "lasso_global_vehicletype" (
    "id" serial NOT NULL PRIMARY KEY,
    "name" varchar(200) NOT NULL,
    "min_temp" double precision NOT NULL,
    "max_temp" double precision NOT NULL
);
insert into "lasso_global_vehicletype" (name, min_temp, max_temp) values('TK-LKW', -18.0, -18.0);
alter table "lasso_warehandling_withdrawal" add column "vehicle_type_id" integer REFERENCES "lasso_global_vehicletype" ("id");
alter table "lasso_warehandling_withdrawal" drop column "vehicle_type";
update "lasso_warehandling_withdrawal" set "vehicle_type_id" = (select id from "lasso_global_vehicletype");
insert into lasso_global_vehicletype (name, min_temp, max_temp) values('Kühl-LKW', -5.0, 2.0);

alter table "lasso_customer_customer" add column "price_min_per_day" double precision NOT NULL default 0.0;
alter table "lasso_customer_customer" add column "price_min_per_entry" double precision NOT NULL default 0.0;
alter table "lasso_customer_customer" add column "price_min_per_withdrawal" double precision NOT NULL default 0.0;
alter table "lasso_warehandling_entry" add column "price_min_per_entry" double precision NOT NULL default 0.0;
alter table "lasso_warehandling_withdrawal" add column "price_min_per_withdrawal" double precision NOT NULL default 0.0;
alter table "lasso_warehandling_storagelog" add column "price_min_per_day" double precision NOT NULL default 0.0;

alter table "lasso_customer_contact" add column "title" varchar(30) NOT NULL default '';

