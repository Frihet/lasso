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



alter table "lasso_customer_customer" alter column "price_per_kilo_per_day" type numeric(12, 6);
alter table "lasso_customer_customer" alter column "price_per_kilo_per_entry" type numeric(12, 6);
alter table "lasso_customer_customer" alter column "price_per_kilo_per_withdrawal" type numeric(12, 6);
alter table "lasso_customer_customer" alter column "price_per_unit_per_day" type numeric(12, 6);
alter table "lasso_customer_customer" alter column "price_per_unit_per_entry" type numeric(12, 6);
alter table "lasso_customer_customer" alter column "price_per_unit_per_withdrawal" type numeric(12, 6);
alter table "lasso_customer_customer" alter column "price_min_per_day" type numeric(12, 6);
alter table "lasso_customer_customer" alter column "price_min_per_entry" type numeric(12, 6);
alter table "lasso_customer_customer" alter column "price_min_per_withdrawal" type numeric(12, 6);
alter table "lasso_customer_unitworkprices" alter column "price_per_unit" type numeric(12, 6);
alter table "lasso_warehouse_palletspace" alter column "size_w" type numeric(12, 6);
alter table "lasso_warehouse_palletspace" alter column "size_h" type numeric(12, 6);
alter table "lasso_warehouse_palletspace" alter column "size_d" type numeric(12, 6);
alter table "lasso_warehandling_entry" alter column "insurance_percentage" type numeric(12, 6);
alter table "lasso_warehandling_entry" alter column "price_per_kilo_per_entry" type numeric(12, 6);
alter table "lasso_warehandling_entry" alter column "price_per_unit_per_entry" type numeric(12, 6);
alter table "lasso_warehandling_entry" alter column "price_min_per_entry" type numeric(12, 6);
alter table "lasso_warehandling_entryrow" alter column "nett_weight" type numeric(12, 6);
alter table "lasso_warehandling_entryrow" alter column "_nett_weight_left" type numeric(12, 6);
alter table "lasso_warehandling_entryrow" alter column "gross_weight" type numeric(12, 6);
alter table "lasso_warehandling_entryrow" alter column "_gross_weight_left" type numeric(12, 6);
alter table "lasso_warehandling_entryrow" alter column "product_value" type numeric(12, 6);
alter table "lasso_warehandling_withdrawal" alter column "price_per_kilo_per_withdrawal" type numeric(12, 6);
alter table "lasso_warehandling_withdrawal" alter column "price_per_unit_per_withdrawal" type numeric(12, 6);
alter table "lasso_warehandling_withdrawal" alter column "price_min_per_withdrawal" type numeric(12, 6);
alter table "lasso_warehandling_withdrawalrow" alter column "old_nett_weight" type numeric(12, 6);
alter table "lasso_warehandling_withdrawalrow" alter column "_nett_weight" type numeric(12, 6);
alter table "lasso_warehandling_withdrawalrow" alter column "old_gross_weight" type numeric(12, 6);
alter table "lasso_warehandling_withdrawalrow" alter column "_gross_weight" type numeric(12, 6);
alter table "lasso_warehandling_unitwork" alter column "price_per_unit" type numeric(12, 6);
alter table "lasso_warehandling_storagelog" alter column "price_per_kilo_per_day" type numeric(12, 6);
alter table "lasso_warehandling_storagelog" alter column "price_per_unit_per_day" type numeric(12, 6);
alter table "lasso_warehandling_storagelog" alter column "price_min_per_day" type numeric(12, 6);
alter table "lasso_warehandling_storagelog" alter column "_nett_weight_left" type numeric(12, 6);
alter table "lasso_warehandling_storagelog" alter column "_gross_weight_left" type numeric(12, 6);

alter table "lasso_global_transportcondition" add column "is_default" boolean NOT NULL default false;
alter table "lasso_global_vehicletype" add column "is_default" boolean NOT NULL default false;



CREATE TABLE "lasso_customer_warehandlingprice" (
    "id" serial NOT NULL PRIMARY KEY,
    "customer_id" integer NOT NULL REFERENCES "lasso_customer_customer" ("organization_ptr_id") DEFERRABLE INITIALLY DEFERRED,
    "name" varchar(200) NOT NULL,
    "is_default" boolean NOT NULL,
    "price_per_kilo_per_day" numeric(12, 6) NOT NULL,
    "price_per_kilo_per_entry" numeric(12, 6) NOT NULL,
    "price_per_kilo_per_withdrawal" numeric(12, 6) NOT NULL,
    "price_per_unit_per_day" numeric(12, 6) NOT NULL,
    "price_per_unit_per_entry" numeric(12, 6) NOT NULL,
    "price_per_unit_per_withdrawal" numeric(12, 6) NOT NULL,
    "price_min_per_day" numeric(12, 6) NOT NULL,
    "price_min_per_entry" numeric(12, 6) NOT NULL,
    "price_min_per_withdrawal" numeric(12, 6) NOT NULL
);

insert into "lasso_customer_warehandlingprice" (
  "name",
  "is_default",
  "customer_id",
  "price_per_kilo_per_day",
  "price_per_kilo_per_entry",
  "price_per_kilo_per_withdrawal",
  "price_per_unit_per_day",
  "price_per_unit_per_entry",
  "price_per_unit_per_withdrawal",
  "price_min_per_day",
  "price_min_per_entry",
  "price_min_per_withdrawal")
  (select
    'default',
    true,
    "organization_ptr_id",
    "price_per_kilo_per_day",
    "price_per_kilo_per_entry",
    "price_per_kilo_per_withdrawal",
    "price_per_unit_per_day",
    "price_per_unit_per_entry",
    "price_per_unit_per_withdrawal",
    "price_min_per_day",
    "price_min_per_entry",
    "price_min_per_withdrawal"
   from "lasso_customer_customer");

alter table "lasso_customer_customer" drop column "price_per_kilo_per_day";
alter table "lasso_customer_customer" drop column"price_per_kilo_per_entry";
alter table "lasso_customer_customer" drop column"price_per_kilo_per_withdrawal";
alter table "lasso_customer_customer" drop column"price_per_unit_per_day";
alter table "lasso_customer_customer" drop column"price_per_unit_per_entry";
alter table "lasso_customer_customer" drop column"price_per_unit_per_withdrawal";
alter table "lasso_customer_customer" drop column"price_min_per_day";
alter table "lasso_customer_customer" drop column"price_min_per_entry";
alter table "lasso_customer_customer" drop column"price_min_per_withdrawal";


alter table "lasso_warehandling_entry" add column "price_id" integer REFERENCES "lasso_customer_warehandlingprice";
update "lasso_warehandling_entry" set "price_id" = (select "id" from "lasso_customer_warehandlingprice" where "lasso_customer_warehandlingprice"."customer_id" = "lasso_warehandling_entry"."customer_id");

alter table lasso_global_insurance alter column percent type numeric(12,6);


alter table "lasso_warehandling_withdrawalrow" add column "price_per_kilo_per_withdrawal" numeric(12, 6) NOT NULL default 0.0;
alter table "lasso_warehandling_withdrawalrow" add column "price_per_unit_per_withdrawal" numeric(12, 6) NOT NULL default 0.0;
alter table "lasso_warehandling_withdrawalrow" add column "price_min_per_withdrawal" numeric(12, 6) NOT NULL default 0.0;

update "lasso_warehandling_withdrawalrow" set "price_per_kilo_per_withdrawal" = (select "price_per_kilo_per_withdrawal" from "lasso_warehandling_withdrawal" where "lasso_warehandling_withdrawal".id = "lasso_warehandling_withdrawalrow"."withdrawal_id"), "price_per_unit_per_withdrawal" = (select "price_per_unit_per_withdrawal" from "lasso_warehandling_withdrawal" where "lasso_warehandling_withdrawal".id = "lasso_warehandling_withdrawalrow"."withdrawal_id"), "price_min_per_withdrawal" = (select "price_min_per_withdrawal" from "lasso_warehandling_withdrawal" where "lasso_warehandling_withdrawal".id = "lasso_warehandling_withdrawalrow"."withdrawal_id");

alter table "lasso_warehandling_withdrawal" drop column "price_per_kilo_per_withdrawal";
alter table "lasso_warehandling_withdrawal" drop column "price_per_unit_per_withdrawal";
alter table "lasso_warehandling_withdrawal" drop column "price_min_per_withdrawal";
