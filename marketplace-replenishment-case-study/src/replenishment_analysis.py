"""Local inventory coverage and replenishment analysis for an XLSX workbook or CSV."""
from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

SOURCE_COLUMNS = {
    "category": "Категория",
    "discounted_price": "Цена после скидки",
    "on_hand_units": "На OZON сейчас, шт.",
    "daily_sales_units": "Продажи в день, шт.",
    "recommended_supply_units": "Необходимо поставить, шт.",
}
SAMPLE_COLUMNS = list(SOURCE_COLUMNS)
SENSITIVE_COLUMNS = [
    "Артикул Ozon", "Баркод", "Артикул поставщика", "Наименование", "Бренд",
    "SKU", "barcode", "product_name", "brand", "supplier_sku",
]


def read_input(path: Path, sheet: str, file_format: str) -> pd.DataFrame:
    if file_format == "csv" or path.suffix.lower() == ".csv":
        raw = pd.read_csv(path)
        missing = [c for c in SAMPLE_COLUMNS if c not in raw.columns]
        if missing:
            raise ValueError(f"В CSV нет обязательных полей: {', '.join(missing)}")
        return raw[SAMPLE_COLUMNS].copy()

    raw = pd.read_excel(path, sheet_name=sheet, engine="openpyxl")
    missing = [c for c in SOURCE_COLUMNS.values() if c not in raw.columns]
    if missing:
        raise ValueError(
            "Не найдены ожидаемые поля на листе. Проверьте название листа и строку заголовков: "
            + ", ".join(missing)
        )
    data = raw[list(SOURCE_COLUMNS.values())].copy()
    data.columns = SAMPLE_COLUMNS
    return data


def analyze(data: pd.DataFrame, risk_days: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    data = data.copy()
    for column in ["discounted_price", "on_hand_units", "daily_sales_units", "recommended_supply_units"]:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    data["category"] = data["category"].fillna("Не указано").astype(str).str.strip()
    data.loc[data["category"].eq(""), "category"] = "Не указано"
    data["stock_cover_days"] = data["on_hand_units"].div(
        data["daily_sales_units"].where(data["daily_sales_units"].gt(0))
    )
    data["stockout_risk"] = data["stock_cover_days"].lt(risk_days).fillna(False)
    data["recommended_gap_units"] = (
        data["recommended_supply_units"].fillna(0) - data["on_hand_units"].fillna(0)
    ).clip(lower=0)

    # Public-facing/local result omits all product-level identifiers and names.
    product_view = data.drop(columns=[c for c in SENSITIVE_COLUMNS if c in data.columns], errors="ignore")
    summary = data.groupby("category", dropna=False).agg(
        assortment_size=("category", "size"),
        median_stock_cover_days=("stock_cover_days", "median"),
        at_risk_count=("stockout_risk", "sum"),
        recommended_supply_units=("recommended_supply_units", "sum"),
        recommended_gap_units=("recommended_gap_units", "sum"),
    ).reset_index()
    summary["at_risk_share"] = (summary["at_risk_count"] / summary["assortment_size"]).round(4)
    return product_view, summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Путь к исходной книге или CSV")
    parser.add_argument("--sheet", default="Анабар Озон год", help="Лист Excel с данными")
    parser.add_argument("--format", choices=["xlsx", "csv"], default="xlsx", help="Формат входа")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/local_analysis"))
    parser.add_argument("--risk-days", type=float, default=7.0, help="Порог риска в днях запаса")
    args = parser.parse_args()

    if not args.input.is_file():
        parser.error(f"Файл не найден: {args.input}")
    if args.risk_days <= 0:
        parser.error("--risk-days должен быть больше нуля")

    data = read_input(args.input, args.sheet, args.format)
    product_view, summary = analyze(data, args.risk_days)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    product_view.to_csv(args.output_dir / "products.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(args.output_dir / "category_summary.csv", index=False, encoding="utf-8-sig")
    print(f"Обработано строк: {len(product_view):,}")
    print(f"Результаты сохранены в: {args.output_dir.resolve()}")
    print("Проверьте, что локальные результаты не добавлены в публичный Git-репозиторий.")


if __name__ == "__main__":
    main()
