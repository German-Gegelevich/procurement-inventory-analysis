"""Обновить обзор: pip install matplotlib; python scripts/plot_results.py."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
def read(name):
    with (ROOT / name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))
status = read('results/by_status.csv')
categories = read('results/by_category.csv')
snapshot = read('data/settings.csv')[0]['snapshot_date']
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                     'axes.spines.top': False, 'axes.spines.right': False})
fig, axes = plt.subplots(1, 2, figsize=(14, 5.7), gridspec_kw={'width_ratios': [1, 1.4]})
colors = {'Избыток': '#dc9858', 'Нет продаж': '#8896a4', 'Норма': '#48a39a', 'Риск дефицита': '#cd6767'}
axes[0].barh([r['status'] for r in status], [int(r['sku_count']) for r in status],
             color=[colors[r['status']] for r in status])
for i, row in enumerate(status):
    axes[0].text(int(row['sku_count']) + 1, i, row['sku_count'], va='center')
axes[0].set_xlim(0, max(int(r['sku_count']) for r in status) * 1.18)
axes[0].set_title('Состояние запасов, SKU', loc='left', fontweight='bold')
axes[1].barh([r['category'] for r in categories],
             [int(r['order_budget']) / 1000 for r in categories], color='#376a8f')
axes[1].invert_yaxis()
axes[1].set_title('Расчётный бюджет пополнения', loc='left', fontweight='bold')
axes[1].set_xlabel('тыс. руб.')
fig.suptitle('Планирование запасов Wildberries', fontsize=18, fontweight='bold', x=.05, ha='left')
date_label = '.'.join(reversed(snapshot.split('-')))
fig.text(.05, .025, f'Синтетические данные • срез на {date_label} • расчётный сценарий, не фактический эффект', fontsize=10, color='#555555')
fig.tight_layout(rect=[0, .06, 1, .92])
fig.savefig(ROOT / 'assets/overview.png', dpi=160)
plt.close(fig)
