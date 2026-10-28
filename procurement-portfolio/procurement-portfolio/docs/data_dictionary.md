# Словарь данных

Все строки синтетические. Кодировка CSV: UTF-8 с BOM, разделитель — запятая. Даты: YYYY-MM-DD. Денежные значения: рубли, без отдельного расчёта налогов.

| Таблица | Ключ | Поля |
|---|---|---|
| products | sku | product_name — название; category — категория; supplier — поставщик; brand — бренд; sale_price — учебная розничная цена; unit_cost — себестоимость; lead_days — срок пополнения; moq — минимальный заказ; batch_size — кратность |
| sales | sale_date, sku | quantity — проданные единицы за календарный день |
| stocks | snapshot_date, sku, location | quantity — физический доступный остаток; in_transit — входящие поставки, не включённые в остаток |
| settings | одна строка | snapshot_date — дата среза; period_start — начало продаж; period_days — длина периода; safety_days — страховой запас; excess_days — добавка к порогу избытка |

В `replenishment.csv`: sold_units — продажи периода; daily_sales — средние продажи в день; available_units — доступный запас; incoming_units — товар в пути; coverage_days — дни запаса (пусто при отсутствии продаж); net_need — чистая потребность; order_units — заказ после округления; order_budget — бюджет; status — статус запаса.

Для восстановления SQL-базы используется SQLite. Типы и ограничения: `sql/01_schema.sql`. Это не выгрузка с реальной учётной системы и не точная копия MP FULL.
