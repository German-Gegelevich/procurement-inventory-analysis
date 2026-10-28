-- 1. Общий объём потребности и бюджет. Бюджет — модель, не утверждённый заказ.
SELECT COUNT(*) AS sku_count,SUM(sold_units) AS sold_units,
 SUM(available_units) AS available_units,SUM(incoming_units) AS incoming_units,
 SUM(order_units>0) AS sku_to_order,SUM(order_units) AS order_units,
 SUM(order_budget) AS order_budget FROM replenishment;

-- 2. Статусы: риск оценивается по текущему запасу БЕЗ поставок в пути.
SELECT status,COUNT(*) AS sku_count,SUM(order_units) AS order_units,
 SUM(order_budget) AS order_budget FROM replenishment GROUP BY status;

-- 3. Категории. Бюджет агрегируем по суммам, не усредняем построчные доли.
SELECT category,COUNT(*) AS sku_count,SUM(sold_units) AS sold_units,
 SUM(order_units) AS order_units,SUM(order_budget) AS order_budget
FROM replenishment GROUP BY category ORDER BY order_budget DESC;

-- 4. Очередь для проверки: сначала риск дефицита, затем запас в днях.
SELECT sku,product_name,status,ROUND(coverage_days,1) AS coverage_days,
 lead_days,net_need,order_units,order_budget FROM replenishment
WHERE order_units>0
ORDER BY CASE WHEN status='Риск дефицита' THEN 0 ELSE 1 END,
 coverage_days,sku;

-- 5. Нет продаж: нельзя считать дни обеспеченности равными нулю.
SELECT sku,product_name,available_units,unit_cost,
 available_units*unit_cost AS inventory_cost
FROM replenishment WHERE status='Нет продаж' ORDER BY inventory_cost DESC;
