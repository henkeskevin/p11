from __future__ import annotations

import pandas as pd

from .pipeline import PipelineResult
from .quality import normalize_identifier


def compare_web_selection_methods(result: PipelineResult) -> pd.DataFrame:
    """Quantify the impact of serious alternatives for Web row selection."""

    web = result.web_raw[["sku", "total_sales", "post_type"]].copy()
    web["sku"] = normalize_identifier(web["sku"])
    web["total_sales"] = pd.to_numeric(web["total_sales"], errors="coerce")
    web = web.loc[web["sku"].notna() & web["total_sales"].notna()].copy()

    alternatives = {
        "filtre_semantique_product": web.loc[web["post_type"] == "product"].copy(),
        "filtre_attachment": web.loc[web["post_type"] == "attachment"].copy(),
        "dedoublonnage_garder_premiere_ligne": web.drop_duplicates("sku", keep="first"),
        "dedoublonnage_garder_derniere_ligne": web.drop_duplicates("sku", keep="last"),
        "somme_de_toutes_les_lignes": web.groupby("sku", as_index=False)["total_sales"].sum(),
    }
    prices = result.catalogue.loc[
        result.catalogue["id_web"].notna(), ["id_web", "price"]
    ].rename(columns={"id_web": "sku"})

    rows: list[dict[str, float | int | str]] = []
    for method, selected in alternatives.items():
        if selected["sku"].duplicated().any():
            raise AssertionError(f"Expérience invalide: SKU dupliqué pour {method}")
        merged = selected[["sku", "total_sales"]].merge(
            prices,
            how="inner",
            on="sku",
            validate="one_to_one",
        )
        rows.append(
            {
                "method": method,
                "matched_skus": int(len(merged)),
                "units": float(merged["total_sales"].sum()),
                "revenue_ttc": float((merged["total_sales"] * merged["price"]).sum()),
            }
        )
    comparison = pd.DataFrame(rows)
    reference = float(
        comparison.loc[
            comparison["method"] == "filtre_semantique_product", "revenue_ttc"
        ].iloc[0]
    )
    comparison["revenue_difference_vs_product"] = (
        comparison["revenue_ttc"] - reference
    )
    comparison["relative_difference_vs_product"] = (
        comparison["revenue_difference_vs_product"] / reference
    )
    comparison["decision"] = comparison["method"].map(
        {
            "filtre_semantique_product": "retenu: le type décrit l'entité métier",
            "filtre_attachment": "rejeté: une pièce jointe n'est pas une vente produit",
            "dedoublonnage_garder_premiere_ligne": "rejeté: résultat dépendant de l'ordre",
            "dedoublonnage_garder_derniere_ligne": "rejeté: résultat dépendant de l'ordre",
            "somme_de_toutes_les_lignes": "rejeté: double comptage",
        }
    )
    return comparison

