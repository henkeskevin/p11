from __future__ import annotations

from html import unescape
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .metrics import compute_metrics, top_products_table
from .pipeline import PipelineResult


COLORS = {
    "green": "#005747",
    "teal": "#008C7A",
    "orange": "#E86F2D",
    "gold": "#D7A928",
    "red": "#B23A48",
    "gray": "#6B7280",
    "light": "#E5E7EB",
    "ink": "#1F2937",
}


def _style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 15,
            "axes.titleweight": "bold",
            "axes.labelcolor": COLORS["ink"],
            "axes.edgecolor": COLORS["light"],
            "xtick.color": COLORS["gray"],
            "ytick.color": COLORS["gray"],
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )


def _save(fig: plt.Figure, output_dir: Path, stem: str) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for suffix in ["png", "svg"]:
        path = output_dir / f"{stem}.{suffix}"
        fig.savefig(path, dpi=180 if suffix == "png" else None, bbox_inches="tight")
        paths.append(path)
    plt.close(fig)
    return paths


def generate_figures(result: PipelineResult, output_dir: Path) -> list[Path]:
    _style()
    outputs: list[Path] = []
    metrics = compute_metrics(result)

    fig, ax = plt.subplots(figsize=(10, 5.4))
    labels = ["ERP", "ERP avec ID Web", "Produits Web avec SKU", "Produits rapprochés"]
    values = [
        metrics["source_rows"]["erp"],
        metrics["data_quality"]["liaison_non_null_web_ids"],
        metrics["data_quality"]["web_products_valid_sku"],
        metrics["data_quality"]["matched_web_products"],
    ]
    bars = ax.barh(labels[::-1], values[::-1], color=[COLORS["green"], COLORS["teal"], COLORS["gold"], COLORS["gray"]])
    ax.bar_label(bars, padding=6, fontweight="bold")
    ax.set_xlim(0, max(values) * 1.15)
    ax.set_title("Rapprochement traçable des sources")
    ax.set_xlabel("Nombre de références/lignes produit")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.grid(axis="x", color=COLORS["light"], linewidth=0.8)
    outputs.extend(_save(fig, output_dir, "01_rapprochement_sources"))

    top = top_products_table(result, 10).sort_values("ca_octobre_ttc")
    fig, ax = plt.subplots(figsize=(10, 6))
    names = (
        top["post_title"]
        .fillna(top["product_type"])
        .fillna("Non classé")
        .map(lambda value: unescape(str(value)))
    )
    labels = top["product_id"].astype(str) + " · " + names.str.slice(0, 34)
    bars = ax.barh(labels, top["ca_octobre_ttc"], color=COLORS["green"])
    ax.bar_label(
        bars,
        labels=[f"{v:,.0f} €".replace(",", " ") for v in top["ca_octobre_ttc"]],
        padding=5,
    )
    ax.set_title("Les 10 premières références ne concentrent qu'une part limitée du CA d'octobre")
    ax.set_xlabel("Chiffre d'affaires TTC d'octobre (€)")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.grid(axis="x", color=COLORS["light"], linewidth=0.8)
    outputs.extend(_save(fig, output_dir, "02_top10_ca_octobre"))

    ranked = result.analytic[["product_id", "ca_octobre_ttc"]].fillna({"ca_octobre_ttc": 0}).sort_values("ca_octobre_ttc", ascending=False).reset_index(drop=True)
    cumulative = ranked["ca_octobre_ttc"].cumsum() / ranked["ca_octobre_ttc"].sum()
    fig, ax = plt.subplots(figsize=(10, 5.6))
    ax.plot(np.arange(1, len(ranked) + 1), cumulative * 100, color=COLORS["green"], linewidth=2.5)
    ax.axhline(80, color=COLORS["orange"], linestyle="--", linewidth=1.5, label="80 % du CA")
    eighty_count = metrics["sales"]["references_for_80pct_revenue"]
    ax.axvline(eighty_count, color=COLORS["gray"], linestyle=":", linewidth=1.5)
    ax.annotate(f"{eighty_count} références", xy=(eighty_count, 80), xytext=(eighty_count + 35, 68), arrowprops={"arrowstyle": "->", "color": COLORS["gray"]})
    ax.set_ylim(0, 103)
    ax.set_xlim(1, len(ranked))
    ax.set_title("Le chiffre d'affaires d'octobre est diffus dans le catalogue")
    ax.set_xlabel("Références classées par CA décroissant")
    ax.set_ylabel("Part cumulée du CA (%)")
    ax.grid(color=COLORS["light"], linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    outputs.extend(_save(fig, output_dir, "03_pareto_ca_octobre"))

    price = result.analytic.loc[result.analytic["price"] > 0, ["product_id", "price", "prix_inhabituel_mad"]].sort_values("price").reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    normal = ~price["prix_inhabituel_mad"]
    ax.scatter(price.index[normal], price.loc[normal, "price"], s=18, color=COLORS["gray"], alpha=0.6, label="Plage habituelle")
    ax.scatter(price.index[~normal], price.loc[~normal, "price"], s=34, color=COLORS["orange"], label="Signal MAD robuste")
    ax.set_yscale("log")
    ax.set_title("Les prix élevés sont des signaux de revue, pas des erreurs automatiques")
    ax.set_xlabel("Références triées par prix")
    ax.set_ylabel("Prix TTC (€), échelle logarithmique")
    ax.legend(frameon=False)
    ax.grid(axis="y", color=COLORS["light"], linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    outputs.extend(_save(fig, output_dir, "04_prix_inhabituels"))

    segment_order = [
        "rupture_potentielle",
        "couverture_lt_1_mois",
        "couverture_1_a_3_mois",
        "couverture_3_a_6_mois",
        "surstock_6_a_12_mois",
        "surstock_gt_12_mois",
        "stock_sans_vente_octobre",
        "ni_stock_ni_vente",
        "quarantaine",
    ]
    labels_map = {
        "rupture_potentielle": "Ventes > 0, stock nul",
        "couverture_lt_1_mois": "Couverture < 1 mois",
        "couverture_1_a_3_mois": "Couverture 1–3 mois",
        "couverture_3_a_6_mois": "Couverture 3–6 mois",
        "surstock_6_a_12_mois": "Couverture 6–12 mois",
        "surstock_gt_12_mois": "Couverture > 12 mois",
        "stock_sans_vente_octobre": "Stock sans vente en octobre",
        "ni_stock_ni_vente": "Ni stock ni vente",
        "quarantaine": "Donnée en quarantaine",
    }
    counts = result.analytic["segment_stock"].value_counts().reindex(segment_order, fill_value=0)
    fig, ax = plt.subplots(figsize=(10, 6))
    bar_colors = [COLORS["red"], COLORS["orange"], COLORS["gold"], COLORS["teal"], COLORS["gray"], COLORS["orange"], COLORS["red"], COLORS["light"], COLORS["ink"]]
    bars = ax.barh([labels_map[x] for x in counts.index][::-1], counts.values[::-1], color=bar_colors[::-1])
    ax.bar_label(bars, padding=5, fontweight="bold")
    ax.set_title("Le stock au 31 octobre appelle des actions différentes selon les ventes d'octobre")
    ax.set_xlabel("Nombre de références rapprochées")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.grid(axis="x", color=COLORS["light"], linewidth=0.8)
    outputs.extend(_save(fig, output_dir, "05_segments_stock"))

    margin = result.analytic.loc[
        result.analytic["marge_octobre_ht"].notna(),
        ["product_type", "marge_octobre_ht", "prix_vente_ht", "total_sales"],
    ].copy()
    margin["ventes_ht"] = margin["prix_vente_ht"] * margin["total_sales"]
    by_type = margin.groupby("product_type", dropna=False)[["marge_octobre_ht", "ventes_ht"]].sum()
    by_type["taux_marque_pondere"] = by_type["marge_octobre_ht"] / by_type["ventes_ht"]
    by_type = by_type.sort_values("taux_marque_pondere")
    fig, ax = plt.subplots(figsize=(10, 5.5))
    bars = ax.barh(by_type.index.fillna("Non classé"), by_type["taux_marque_pondere"] * 100, color=COLORS["teal"])
    ax.bar_label(bars, labels=[f"{v:.1f} %" for v in by_type["taux_marque_pondere"] * 100], padding=5)
    ax.set_title("Le taux de marque pondéré varie selon le type — hypothèse TVA 20 %")
    ax.set_xlabel("Taux de marque pondéré par les ventes HT d'octobre")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.grid(axis="x", color=COLORS["light"], linewidth=0.8)
    outputs.extend(_save(fig, output_dir, "06_marge_ponderee_type"))

    corr_columns = ["price", "total_sales", "stock_quantity", "taux_marque"]
    correlation = result.analytic[corr_columns].corr(method="spearman")
    fig, ax = plt.subplots(figsize=(7.5, 6.3))
    image = ax.imshow(correlation, vmin=-1, vmax=1, cmap="RdBu_r")
    labels = ["Prix", "Ventes octobre", "Stock 31/10", "Taux de marque"]
    ax.set_xticks(range(len(labels)), labels=labels, rotation=25, ha="right")
    ax.set_yticks(range(len(labels)), labels=labels)
    for i in range(len(labels)):
        for j in range(len(labels)):
            ax.text(j, i, f"{correlation.iloc[i, j]:.2f}", ha="center", va="center", color="white" if abs(correlation.iloc[i, j]) > 0.5 else COLORS["ink"], fontweight="bold")
    fig.colorbar(image, ax=ax, shrink=0.8, label="Corrélation de Spearman")
    ax.set_title("Les corrélations décrivent octobre; elles n'établissent pas de causalité")
    outputs.extend(_save(fig, output_dir, "07_correlations_spearman"))

    issue_counts = result.quality_issues["category"].value_counts().reindex(["erreur_certaine", "anomalie_probable", "inhabituel_plausible"], fill_value=0)
    fig, ax = plt.subplots(figsize=(9, 4.8))
    issue_labels = ["Erreur certaine", "Anomalie probable", "Inhabituel mais plausible"]
    bars = ax.bar(issue_labels, issue_counts.values, color=[COLORS["red"], COLORS["orange"], COLORS["teal"]])
    ax.bar_label(bars, padding=5, fontweight="bold")
    ax.set_title("Les alertes ne doivent pas toutes déclencher une correction")
    ax.set_ylabel("Nombre de constats")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color=COLORS["light"], linewidth=0.8)
    outputs.extend(_save(fig, output_dir, "08_typologie_alertes"))

    dormant = result.analytic.loc[
        result.analytic["segment_stock"] == "stock_sans_vente_octobre",
        ["product_id", "post_title", "valeur_stock_cout_ht"],
    ].sort_values("valeur_stock_cout_ht")
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    dormant_labels = (
        dormant["product_id"].astype(str)
        + " · "
        + dormant["post_title"]
        .fillna("Produit non libellé")
        .map(lambda value: unescape(str(value)))
        .str.slice(0, 40)
    )
    bars = ax.barh(dormant_labels, dormant["valeur_stock_cout_ht"], color=COLORS["orange"])
    ax.bar_label(
        bars,
        labels=[
            f"{value:,.0f} €".replace(",", " ")
            for value in dormant["valeur_stock_cout_ht"]
        ],
        padding=5,
        fontweight="bold",
    )
    ax.set_title("14 959 € de stock n'ont généré aucune vente observée en octobre")
    ax.set_xlabel("Valeur du stock au coût d'achat HT au 31 octobre")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.grid(axis="x", color=COLORS["light"], linewidth=0.8)
    outputs.extend(_save(fig, output_dir, "09_stock_sans_vente_octobre"))

    anomaly = result.analytic.loc[result.analytic["taux_marque"] < 0].iloc[0]
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    values = [float(anomaly["prix_vente_ht"]), float(anomaly["purchase_price"])]
    bars = ax.bar(
        ["Prix de vente HT", "Coût d'achat HT"],
        values,
        color=[COLORS["teal"], COLORS["red"]],
        width=0.55,
    )
    ax.bar_label(bars, labels=[f"{value:.2f} €" for value in values], padding=5, fontweight="bold")
    ax.set_ylim(0, max(values) * 1.18)
    ax.set_title(f"Référence {anomaly['product_id']} : coût d'achat à confirmer avant toute décision")
    ax.set_ylabel("Euros HT")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color=COLORS["light"], linewidth=0.8)
    outputs.extend(_save(fig, output_dir, "10_anomalie_marge_reference_4355"))

    scatter = result.analytic.loc[
        (result.analytic["price"] > 0) & result.analytic["total_sales"].notna(),
        ["price", "total_sales"],
    ]
    rho = scatter.corr(method="spearman").iloc[0, 1]
    fig, ax = plt.subplots(figsize=(9.5, 5.5))
    ax.scatter(
        scatter["price"],
        scatter["total_sales"],
        s=24,
        color=COLORS["green"],
        alpha=0.48,
        edgecolors="none",
    )
    ax.set_xscale("log")
    ax.text(
        0.98,
        0.94,
        f"Spearman ρ = {rho:.2f}",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=12,
        fontweight="bold",
        color=COLORS["ink"],
    )
    ax.set_title("Prix et volumes sont associés en octobre, sans preuve d'effet causal")
    ax.set_xlabel("Prix TTC (€), échelle logarithmique")
    ax.set_ylabel("Unités vendues en octobre")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(color=COLORS["light"], linewidth=0.8)
    outputs.extend(_save(fig, output_dir, "11_prix_vs_ventes_octobre"))

    return outputs
