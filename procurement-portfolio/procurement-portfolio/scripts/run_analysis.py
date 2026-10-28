"""CSV -> SQLite -> отчёты. Только стандартная библиотека Python 3.10+."""
import csv
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'results'
RESULTS.mkdir(exist_ok=True)
db_path = RESULTS / 'portfolio.sqlite'
if db_path.exists():
    db_path.unlink()
db = sqlite3.connect(db_path)
db.row_factory = sqlite3.Row
db.executescript((ROOT / 'sql/01_schema.sql').read_text(encoding='utf-8'))
for name in ['products', 'sales', 'stocks', 'settings']:
    with (ROOT / 'data' / f'{name}.csv').open(encoding='utf-8-sig', newline='') as f:
        reader = csv.reader(f)
        headers = next(reader)
        db.executemany(f"INSERT INTO {name} VALUES ({','.join('?' for _ in headers)})", reader)
db.executescript((ROOT / 'sql/02_replenishment.sql').read_text(encoding='utf-8'))
assert not db.execute('PRAGMA foreign_key_check').fetchall()
assert db.execute('SELECT COUNT(*) FROM settings').fetchone()[0] == 1
assert db.execute('SELECT COUNT(*) FROM products').fetchone()[0] == 240
assert db.execute('SELECT COUNT(*) FROM sales').fetchone()[0] == 7200
assert db.execute('SELECT COUNT(*) FROM stocks').fetchone()[0] == 480
assert db.execute('SELECT COUNT(*) FROM replenishment WHERE order_units>0 AND order_units<net_need').fetchone()[0] == 0
assert db.execute('SELECT COUNT(*) FROM replenishment r JOIN products p USING(sku) WHERE order_units>0 AND (order_units % batch_size<>0 OR order_units<moq)').fetchone()[0] == 0
queries = {
 'replenishment': 'SELECT * FROM replenishment ORDER BY sku',
 'priority_orders': "SELECT * FROM replenishment WHERE order_units>0 ORDER BY CASE WHEN status='Риск дефицита' THEN 0 ELSE 1 END,coverage_days,sku",
 'by_category': 'SELECT category,COUNT(*) AS sku_count,SUM(sold_units) AS sold_units,SUM(order_units) AS order_units,SUM(order_budget) AS order_budget FROM replenishment GROUP BY category ORDER BY order_budget DESC',
 'by_status': 'SELECT status,COUNT(*) AS sku_count,SUM(order_units) AS order_units,SUM(order_budget) AS order_budget FROM replenishment GROUP BY status',
}
for name, query in queries.items():
    cursor = db.execute(query)
    with (RESULTS / f'{name}.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([c[0] for c in cursor.description])
        writer.writerows(cursor)
summary = dict(db.execute('SELECT COUNT(*) AS sku_count,SUM(sold_units) AS sold_units,SUM(available_units) AS available_units,SUM(incoming_units) AS incoming_units,SUM(order_units>0) AS sku_to_order,SUM(order_units) AS order_units,SUM(order_budget) AS order_budget FROM replenishment').fetchone())
summary['status_counts'] = {r['status']: r['sku_count'] for r in db.execute(queries['by_status'])}
summary['validation'] = 'passed'
(RESULTS / 'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
db.commit()
db.close()
print(json.dumps(summary,ensure_ascii=False,indent=2))
