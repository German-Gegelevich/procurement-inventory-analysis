PRAGMA foreign_keys = ON;
CREATE TABLE products (
 sku TEXT PRIMARY KEY, product_name TEXT NOT NULL, category TEXT NOT NULL,
 supplier TEXT NOT NULL, brand TEXT NOT NULL,
 sale_price INTEGER NOT NULL CHECK(sale_price>0), unit_cost INTEGER NOT NULL CHECK(unit_cost>0),
 lead_days INTEGER NOT NULL CHECK(lead_days>0), moq INTEGER NOT NULL CHECK(moq>0),
 batch_size INTEGER NOT NULL CHECK(batch_size>0)
);
CREATE TABLE sales (
 sale_date TEXT NOT NULL, sku TEXT NOT NULL REFERENCES products(sku),
 quantity INTEGER NOT NULL CHECK(quantity>=0), PRIMARY KEY(sale_date,sku)
);
CREATE TABLE stocks (
 snapshot_date TEXT NOT NULL, sku TEXT NOT NULL REFERENCES products(sku),
 location TEXT NOT NULL, quantity INTEGER NOT NULL CHECK(quantity>=0),
 in_transit INTEGER NOT NULL CHECK(in_transit>=0), PRIMARY KEY(snapshot_date,sku,location)
);
CREATE TABLE settings (
 snapshot_date TEXT NOT NULL, period_start TEXT NOT NULL, period_days INTEGER NOT NULL,
 safety_days INTEGER NOT NULL, excess_days INTEGER NOT NULL
);
