alter table "lasso_customer_originalseller" add column "origin_id" integer REFERENCES "lasso_global_origin" ("id");
alter table "lasso_warehandling_unitwork" add column "entry_id" integer REFERENCES "lasso_warehandling_entry" ("id");
alter table "lasso_warehandling_unitwork" add column "withdrawal_id" integer REFERENCES "lasso_warehandling_withdrawal" ("id");

alter table "lasso_warehandling_entryrow" add column "origin_id" integer REFERENCES "lasso_global_origin" ("id");
update "lasso_warehandling_entryrow" set origin_id = (select origin_id from "lasso_warehandling_entry" where "lasso_warehandling_entry".id = "lasso_warehandling_entryrow"."entry_id");
alter table "lasso_warehandling_entry" drop column "origin_id";
