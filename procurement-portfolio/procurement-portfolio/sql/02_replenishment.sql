-- SQLite 3. Расчёт на уровне SKU, не складываем снимки остатков разных дат.
-- Сначала агрегируем продажи и остатки отдельно, затем соединяем: это исключает
-- размножение строк при соединении ежедневных продаж с несколькими складами.
CREATE VIEW replenishment AS
WITH demand AS (
 SELECT s.sku, SUM(s.quantity) AS sold_units
 FROM sales s CROSS JOIN settings c
 WHERE s.sale_date BETWEEN c.period_start AND c.snapshot_date GROUP BY s.sku
), inventory AS (
 SELECT s.sku, SUM(s.quantity) AS available_units, SUM(s.in_transit) AS incoming_units
 FROM stocks s CROSS JOIN settings c
 WHERE s.snapshot_date=c.snapshot_date GROUP BY s.sku
), base AS (
 SELECT p.*, COALESCE(d.sold_units,0) AS sold_units,
 COALESCE(d.sold_units,0)*1.0/c.period_days AS daily_sales,
 COALESCE(i.available_units,0) AS available_units,
 COALESCE(i.incoming_units,0) AS incoming_units,c.safety_days,c.excess_days
 FROM products p CROSS JOIN settings c
 LEFT JOIN demand d ON d.sku=p.sku LEFT JOIN inventory i ON i.sku=p.sku
), need AS (
 SELECT *, MAX(0,daily_sales*(lead_days+safety_days)-available_units-incoming_units) AS raw_need
 FROM base
), rounded AS (
 SELECT *, CAST(raw_need AS INTEGER) + (raw_need>CAST(raw_need AS INTEGER)) AS net_need
 FROM need
), orders AS (
 SELECT *, CASE WHEN net_need=0 THEN 0
 ELSE MAX(moq,CAST((net_need+batch_size-1)/batch_size AS INTEGER)*batch_size) END AS order_units
 FROM rounded
)
SELECT sku,product_name,category,supplier,sold_units,daily_sales,available_units,incoming_units,
 lead_days,CASE WHEN daily_sales=0 THEN NULL ELSE available_units/daily_sales END AS coverage_days,
 net_need,order_units,unit_cost,order_units*unit_cost AS order_budget,
 CASE WHEN daily_sales=0 THEN 'Нет продаж'
 WHEN available_units/daily_sales<lead_days THEN 'Риск дефицита'
 WHEN available_units/daily_sales>lead_days+safety_days+excess_days THEN 'Избыток'
 ELSE 'Норма' END AS status
FROM orders;
