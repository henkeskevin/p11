from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import warnings

import numpy as np
import pandas as pd

from .config import AnalysisConfig
from .outliers import mad_upper_flags
from .quality import (
    DataContractError,
    add_aggregate_issue,
    add_row_issues,
    assert_unique_non_null,
    issues_frame,
    normalize_identifier,
    require_columns,
)


ERP_COLUMNS = {
    "product_id",
    "onsale_web",
    "price",
    "stock_quantity",
    "stock_status",
    "purchase_price",
}
WEB_COLUMNS = {"sku", "total_sales", "product_type", "post_type"}
LIAISON_COLUMNS = {"product_id", "id_web"}


@dataclass
class PipelineResult:
    erp_raw: pd.DataFrame
    web_raw: pd.DataFrame
    liaison_raw: pd.DataFrame
    erp: pd.DataFrame
    web_products: pd.DataFrame
    liaison: pd.DataFrame
    catalogue: pd.DataFrame
    analytic: pd.DataFrame
    quality_issues: pd.DataFrame
    join_audit: pd.DataFrame
    loading_warnings: pd.DataFrame


def _read_excel(path: Path, source: str) -> tuple[pd.DataFrame, list[dict[str, str]]]:
    if not path.exists():
        raise FileNotFoundError(f"Source absente: {path}")
    captured: list[dict[str, str]] = []
    with warnings.catch_warnings(record=True) as records:
        warnings.simplefilter("always")
        frame = pd.read_excel(path)
    for warning in records:
        captured.append(
            {
                "source": source,
                "category": warning.category.__name__,
                "message": str(warning.message),
            }
        )
    return frame, captured


def _numeric_with_audit(
    frame: pd.DataFrame,
    column: str,
    *,
    source: str,
    key_column: str,
    issues: list[dict[str, object]],
) -> None:
    original = frame[column].copy()
    converted = pd.to_numeric(original, errors="coerce")
    failed = original.notna() & converted.isna()
    add_row_issues(
        issues,
        frame.assign(**{column: original}),
        failed,
        rule_id=f"{source.lower()}_{column}_type",
        source=source,
        key_column=key_column,
        value_column=column,
        severity="critical",
        category="erreur_certaine",
        description="Valeur non numérique dans une colonne quantitative obligatoire.",
        action="Corriger dans la source avant utilisation de l'indicateur.",
    )
    frame[column] = converted


def _prepare_erp(
    raw: pd.DataFrame, issues: list[dict[str, object]]
) -> pd.DataFrame:
    require_columns(raw, ERP_COLUMNS, "ERP")
    erp = raw.copy(deep=True)
    erp["product_id_raw"] = erp["product_id"]
    erp["product_id"] = normalize_identifier(erp["product_id"])
    if erp["product_id"].isna().any():
        raise DataContractError("ERP: product_id contient une clé vide.")
    assert_unique_non_null(erp, "product_id", "ERP")

    for column in ["onsale_web", "price", "stock_quantity", "purchase_price"]:
        _numeric_with_audit(
            erp,
            column,
            source="ERP",
            key_column="product_id",
            issues=issues,
        )
    erp["stock_status"] = erp["stock_status"].astype("string").str.strip()

    add_row_issues(
        issues,
        erp,
        erp["price"].isna() | (erp["price"] <= 0),
        rule_id="erp_price_non_positive",
        source="ERP",
        key_column="product_id",
        value_column="price",
        severity="critical",
        category="erreur_certaine",
        description="Un prix de vente nul, négatif ou absent n'est pas exploitable.",
        action="Mettre en quarantaine; ne pas appliquer de valeur absolue.",
    )
    add_row_issues(
        issues,
        erp,
        erp["purchase_price"].isna() | (erp["purchase_price"] <= 0),
        rule_id="erp_purchase_price_non_positive",
        source="ERP",
        key_column="product_id",
        value_column="purchase_price",
        severity="critical",
        category="erreur_certaine",
        description="Un prix d'achat nul, négatif ou absent n'est pas exploitable.",
        action="Mettre en quarantaine pour les analyses de marge.",
    )
    add_row_issues(
        issues,
        erp,
        erp["stock_quantity"] < 0,
        rule_id="erp_stock_negative",
        source="ERP",
        key_column="product_id",
        value_column="stock_quantity",
        severity="high",
        category="anomalie_probable",
        description="Stock négatif à confirmer: correction, reliquat ou convention ERP possible.",
        action="Conserver brut et exclure des agrégats de stock jusqu'à revue métier.",
    )
    add_row_issues(
        issues,
        erp,
        ~erp["onsale_web"].isin([0, 1]),
        rule_id="erp_onsale_domain",
        source="ERP",
        key_column="product_id",
        value_column="onsale_web",
        severity="critical",
        category="erreur_certaine",
        description="onsale_web doit appartenir à {0, 1}.",
        action="Corriger dans l'ERP avant rapprochement.",
    )
    expected_status = pd.Series(
        np.where(erp["stock_quantity"] == 0, "outofstock", "instock"),
        index=erp.index,
        dtype="string",
    )
    status_mismatch = (erp["stock_quantity"] >= 0) & (
        erp["stock_status"] != expected_status
    )
    add_row_issues(
        issues,
        erp,
        status_mismatch,
        rule_id="erp_stock_status_inconsistent",
        source="ERP",
        key_column="product_id",
        value_column="stock_status",
        severity="medium",
        category="anomalie_probable",
        description="Le statut ne correspond pas à la règle quantité zéro / quantité positive.",
        action="Confirmer la règle métier et la synchronisation de l'ERP.",
    )
    return erp


def _prepare_web(
    raw: pd.DataFrame, issues: list[dict[str, object]]
) -> pd.DataFrame:
    require_columns(raw, WEB_COLUMNS, "WEB")
    web = raw.copy(deep=True)
    web["sku_raw"] = web["sku"]
    web["sku"] = normalize_identifier(web["sku"])
    web["post_type"] = web["post_type"].astype("string").str.strip()
    products = web.loc[web["post_type"] == "product"].copy()
    _numeric_with_audit(
        products,
        "total_sales",
        source="WEB",
        key_column="sku",
        issues=issues,
    )
    assert_unique_non_null(products, "sku", "WEB produits")
    add_row_issues(
        issues,
        products,
        products["sku"].isna(),
        rule_id="web_product_sku_missing",
        source="WEB",
        key_column="sku",
        value_column="sku_raw",
        severity="critical",
        category="erreur_certaine",
        description="Une ligne produit sans SKU ne peut pas être rapprochée.",
        action="Compléter le SKU; exclure du rapprochement sans imputation inventée.",
    )
    add_row_issues(
        issues,
        products,
        products["total_sales"].isna() | (products["total_sales"] < 0),
        rule_id="web_sales_invalid",
        source="WEB",
        key_column="sku",
        value_column="total_sales",
        severity="critical",
        category="erreur_certaine",
        description="Les ventes d'octobre doivent être renseignées et non négatives.",
        action="Mettre en quarantaine pour le calcul du chiffre d'affaires.",
    )
    blank_rows = int(web["post_type"].isna().sum())
    if blank_rows:
        add_aggregate_issue(
            issues,
            rule_id="web_blank_export_rows",
            source="WEB",
            column="post_type",
            value=blank_rows,
            severity="low",
            category="anomalie_probable",
            description="L'export contient des lignes sans type ni attribut produit utile.",
            action="Vérifier le paramétrage d'export; elles ne sont pas assimilées à des produits.",
        )

    attachments = web.loc[
        (web["post_type"] == "attachment") & web["sku"].notna(),
        ["sku", "total_sales"],
    ].copy()
    attachments["total_sales"] = pd.to_numeric(
        attachments["total_sales"], errors="coerce"
    )
    comparison = products.loc[products["sku"].notna(), ["sku", "total_sales"]].merge(
        attachments,
        on="sku",
        how="inner",
        suffixes=("_product", "_attachment"),
        validate="one_to_one",
    )
    comparison["sales_pair"] = comparison.apply(
        lambda row: f"product={row['total_sales_product']}; attachment={row['total_sales_attachment']}",
        axis=1,
    )
    add_row_issues(
        issues,
        comparison,
        comparison["total_sales_product"] != comparison["total_sales_attachment"],
        rule_id="web_product_attachment_sales_mismatch",
        source="WEB",
        key_column="sku",
        value_column="sales_pair",
        severity="high",
        category="anomalie_probable",
        description="Les lignes produit et pièce jointe portent des ventes différentes pour le même SKU.",
        action="Sélectionner explicitement post_type='product'; ne pas dédupliquer selon l'ordre.",
    )
    return products


def _prepare_liaison(
    raw: pd.DataFrame, issues: list[dict[str, object]]
) -> pd.DataFrame:
    require_columns(raw, LIAISON_COLUMNS, "LIAISON")
    liaison = raw.copy(deep=True)
    liaison["product_id_raw"] = liaison["product_id"]
    liaison["id_web_raw"] = liaison["id_web"]
    liaison["product_id"] = normalize_identifier(liaison["product_id"])
    liaison["id_web"] = normalize_identifier(liaison["id_web"])
    if liaison["product_id"].isna().any():
        raise DataContractError("LIAISON: product_id contient une clé vide.")
    assert_unique_non_null(liaison, "product_id", "LIAISON")
    assert_unique_non_null(liaison, "id_web", "LIAISON")
    add_row_issues(
        issues,
        liaison,
        liaison["id_web"].isna(),
        rule_id="liaison_id_web_missing",
        source="LIAISON",
        key_column="product_id",
        value_column="id_web_raw",
        severity="medium",
        category="anomalie_probable",
        description="Référence ERP sans identifiant Web; peut correspondre à un produit hors ligne.",
        action="Confirmer le périmètre et compléter le mapping si le produit doit être vendu en ligne.",
    )
    return liaison


def _build_join_audit(
    erp: pd.DataFrame, liaison: pd.DataFrame, web_products: pd.DataFrame
) -> pd.DataFrame:
    erp_link = erp[["product_id"]].merge(
        liaison[["product_id", "id_web"]],
        how="outer",
        on="product_id",
        indicator=True,
        validate="one_to_one",
    )
    link_web = liaison.loc[liaison["id_web"].notna(), ["product_id", "id_web"]].merge(
        web_products.loc[web_products["sku"].notna(), ["sku"]],
        how="outer",
        left_on="id_web",
        right_on="sku",
        indicator=True,
        validate="one_to_one",
    )
    rows = [
        {
            "join": "ERP ↔ LIAISON",
            "status": status,
            "rows": int((erp_link["_merge"] == status).sum()),
        }
        for status in ["left_only", "right_only", "both"]
    ]
    rows.extend(
        {
            "join": "LIAISON (clé Web non vide) ↔ WEB produits",
            "status": status,
            "rows": int((link_web["_merge"] == status).sum()),
        }
        for status in ["left_only", "right_only", "both"]
    )
    return pd.DataFrame(rows)


def _build_catalogue(
    erp: pd.DataFrame,
    liaison: pd.DataFrame,
    web_products: pd.DataFrame,
    issues: list[dict[str, object]],
    vat_rate: float,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    catalogue = erp.merge(
        liaison[["product_id", "id_web", "id_web_raw"]],
        how="left",
        on="product_id",
        validate="one_to_one",
    )
    # Exclude null keys before merging: pandas otherwise matches null to null,
    # unlike ordinary SQL semantics. Non-null id_web uniqueness was certified
    # in the liaison contract above.
    web_columns = ["sku", "sku_raw", "total_sales", "product_type", "post_type"]
    if "post_title" in web_products.columns:
        web_columns.append("post_title")
    web_selected = web_products.loc[web_products["sku"].notna(), web_columns]
    catalogue = catalogue.merge(
        web_selected,
        how="left",
        left_on="id_web",
        right_on="sku",
        indicator="web_match_status",
        validate="many_to_one",
    )

    missing_web = catalogue["id_web"].notna() & (
        catalogue["web_match_status"] == "left_only"
    )
    add_row_issues(
        issues,
        catalogue,
        missing_web,
        rule_id="liaison_web_product_missing",
        source="RAPPROCHEMENT",
        key_column="product_id",
        value_column="id_web",
        severity="medium",
        category="anomalie_probable",
        description="Identifiant Web présent dans la liaison mais absent des lignes produit Web.",
        action="Vérifier désactivation, obsolescence ou défaut d'export.",
    )
    add_row_issues(
        issues,
        catalogue,
        (catalogue["onsale_web"] == 1) &
        (catalogue["web_match_status"] == "left_only"),
        rule_id="erp_marked_online_but_web_missing",
        source="RAPPROCHEMENT",
        key_column="product_id",
        value_column="id_web",
        severity="high",
        category="anomalie_probable",
        description="Référence marquée en vente en ligne dans l'ERP mais absente des produits Web rapprochés.",
        action="Contrôler la publication Web et le mapping.",
    )

    analytic = catalogue.loc[catalogue["web_match_status"] == "both"].copy()
    add_row_issues(
        issues,
        analytic,
        (analytic["onsale_web"] == 0) & (analytic["total_sales"] > 0),
        rule_id="web_sales_while_erp_offline",
        source="RAPPROCHEMENT",
        key_column="product_id",
        value_column="total_sales",
        severity="high",
        category="anomalie_probable",
        description="Des ventes Web existent alors que l'ERP marque le produit hors ligne.",
        action="Contrôler la synchronisation des statuts ERP/Web.",
    )
    ca_valid = (
        analytic["price"].notna()
        & (analytic["price"] > 0)
        & analytic["total_sales"].notna()
        & (analytic["total_sales"] >= 0)
    )
    analytic["ca_octobre_ttc"] = np.where(
        ca_valid, analytic["price"] * analytic["total_sales"], np.nan
    )
    analytic["prix_vente_ht"] = np.where(
        analytic["price"] > 0, analytic["price"] / (1 + vat_rate), np.nan
    )
    margin_valid = (
        ca_valid
        & analytic["purchase_price"].notna()
        & (analytic["purchase_price"] > 0)
    )
    analytic["marge_unitaire_ht"] = np.where(
        margin_valid,
        analytic["prix_vente_ht"] - analytic["purchase_price"],
        np.nan,
    )
    analytic["taux_marque"] = np.where(
        margin_valid,
        analytic["marge_unitaire_ht"] / analytic["prix_vente_ht"],
        np.nan,
    )
    analytic["taux_marge_sur_cout"] = np.where(
        margin_valid,
        analytic["marge_unitaire_ht"] / analytic["purchase_price"],
        np.nan,
    )
    analytic["marge_octobre_ht"] = np.where(
        margin_valid,
        analytic["marge_unitaire_ht"] * analytic["total_sales"],
        np.nan,
    )

    stock_valid = analytic["stock_quantity"].notna() & (
        analytic["stock_quantity"] >= 0
    )
    analytic["valeur_stock_cout_ht"] = np.where(
        stock_valid & (analytic["purchase_price"] > 0),
        analytic["stock_quantity"] * analytic["purchase_price"],
        np.nan,
    )
    analytic["valeur_stock_vente_ttc"] = np.where(
        stock_valid & (analytic["price"] > 0),
        analytic["stock_quantity"] * analytic["price"],
        np.nan,
    )
    analytic["couverture_au_rythme_octobre_mois"] = np.where(
        stock_valid & (analytic["total_sales"] > 0),
        analytic["stock_quantity"] / analytic["total_sales"],
        np.nan,
    )

    conditions = [
        (~stock_valid) | analytic["total_sales"].isna() | (analytic["total_sales"] < 0),
        (analytic["stock_quantity"] == 0) & (analytic["total_sales"] > 0),
        (analytic["stock_quantity"] > 0) & (analytic["total_sales"] == 0),
        (analytic["stock_quantity"] == 0) & (analytic["total_sales"] == 0),
        analytic["couverture_au_rythme_octobre_mois"] < 1,
        analytic["couverture_au_rythme_octobre_mois"].between(1, 3, inclusive="left"),
        analytic["couverture_au_rythme_octobre_mois"].between(3, 6, inclusive="left"),
        analytic["couverture_au_rythme_octobre_mois"].between(6, 12, inclusive="both"),
        analytic["couverture_au_rythme_octobre_mois"] > 12,
    ]
    labels = [
        "quarantaine",
        "rupture_potentielle",
        "stock_sans_vente_octobre",
        "ni_stock_ni_vente",
        "couverture_lt_1_mois",
        "couverture_1_a_3_mois",
        "couverture_3_a_6_mois",
        "surstock_6_a_12_mois",
        "surstock_gt_12_mois",
    ]
    analytic["segment_stock"] = np.select(conditions, labels, default="non_classe")

    negative_margin = analytic["taux_marque"] < 0
    add_row_issues(
        issues,
        analytic,
        negative_margin,
        rule_id="margin_negative",
        source="ANALYSE",
        key_column="product_id",
        value_column="purchase_price",
        severity="high",
        category="anomalie_probable",
        description="Prix d'achat supérieur au prix de vente HT sous hypothèse de TVA à 20 %.",
        action="Confirmer unité, saisie du coût et définition de la TVA avant décision.",
    )

    price_flags = mad_upper_flags(analytic["price"])
    add_row_issues(
        issues,
        analytic,
        price_flags,
        rule_id="price_high_mad",
        source="ANALYSE",
        key_column="product_id",
        value_column="price",
        severity="info",
        category="inhabituel_plausible",
        description="Prix élevé selon le z-score modifié MAD; un vin premium peut rester parfaitement valide.",
        action="Revue métier priorisée; aucune correction ou exclusion automatique.",
    )
    analytic["prix_inhabituel_mad"] = price_flags
    return catalogue, analytic


def run_pipeline(config: AnalysisConfig | None = None) -> PipelineResult:
    config = config or AnalysisConfig.default()
    issues: list[dict[str, object]] = []
    all_warnings: list[dict[str, str]] = []

    erp_raw, captured = _read_excel(config.raw_dir / "erp.xlsx", "ERP")
    all_warnings.extend(captured)
    web_raw, captured = _read_excel(config.raw_dir / "web.xlsx", "WEB")
    all_warnings.extend(captured)
    liaison_raw, captured = _read_excel(
        config.raw_dir / "liaison.xlsx", "LIAISON"
    )
    all_warnings.extend(captured)

    erp = _prepare_erp(erp_raw, issues)
    web_products = _prepare_web(web_raw, issues)
    liaison = _prepare_liaison(liaison_raw, issues)
    join_audit = _build_join_audit(erp, liaison, web_products)
    catalogue, analytic = _build_catalogue(
        erp, liaison, web_products, issues, config.vat_rate
    )

    return PipelineResult(
        erp_raw=erp_raw,
        web_raw=web_raw,
        liaison_raw=liaison_raw,
        erp=erp,
        web_products=web_products,
        liaison=liaison,
        catalogue=catalogue,
        analytic=analytic,
        quality_issues=issues_frame(issues),
        join_audit=join_audit,
        loading_warnings=pd.DataFrame(
            all_warnings, columns=["source", "category", "message"]
        ),
    )
