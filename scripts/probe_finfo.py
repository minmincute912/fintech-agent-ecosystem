"""Live probe of VNDirect finfo (M2 Task 6): layouts, the last quarters' dates, item lists.

Run: uv run python -I scripts/probe_finfo.py [--items]. Free, no key. Research-only source.
"""

import sys

from vsi.finfo import FinfoClient

TICKERS = ("VNM", "FPT", "HPG", "VCB", "ACB", "SSI", "SHS", "BVH", "ACV")


def main() -> None:
    client = FinfoClient()
    items_for = {}
    for t in TICKERS:
        try:
            q = client.statements(t, "QUARTER")
            name, models = client.layout_models(t)
        except Exception as e:  # probe: report and keep going
            print(f"{t}: {type(e).__name__}: {e}")
            continue
        items_for.setdefault(name, (t, models))
        periods = (q.groupby("fiscal_date").agg(created_min=("created", "min"), created_max=("created", "max"),
                                                modified_max=("modified", "max"), rows=("value", "size"))
                   .sort_index(ascending=False).head(6))
        print(f"\n{t} layout={name} models={models} quarter rows={len(q)}")
        print(periods.to_string())
        a = client.statements(t, "ANNUAL")
        ap = a.groupby("fiscal_date").agg(created=("created", "min"), modified=("modified", "max")).sort_index().tail(3)
        print("annual:\n" + ap.to_string())
    if "--items" in sys.argv:
        for name, (t, models) in items_for.items():
            names = client.item_names(t, list(models))
            latest = client.statements(t, "QUARTER")
            latest = latest[latest["fiscal_date"] == latest["fiscal_date"].max()]
            values = {(r.model_type, r.item_code): r.value for r in latest.itertuples()}
            print(f"\n## items {name} ({t}, latest quarter {latest['fiscal_date'].max()})")
            for (m, code), (vn, en, order) in sorted(names.items(), key=lambda kv: (kv[0][0], kv[1][2])):
                print(f"{m}\t{code}\t{order:g}\t{values.get((m, code), '')}\t{vn} | {en}")


if __name__ == "__main__":
    main()
