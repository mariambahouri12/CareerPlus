"""
Évaluation offline du pipeline de retrieval à partir de labeling_candidates.json.

Filtrage :
    seuls les candidats avec reranker_score >= SCORE_THRESHOLD
    sont pris en compte dans les métriques.

    Les candidats avec reranker_score < SCORE_THRESHOLD
    sont complètement ignorés.

    Si une requête n'a aucun candidat au-dessus du seuil,
    toute la requête est ignorée.

Usage:
    python eval_metrics.py

Le script calcule :
    - Precision@K
    - Recall@K
    - F1@K
    - MRR
    - nDCG@K

Les labels :
    0 = non pertinent
    1 = pertinent
    2 = très pertinent
"""

import json
import math
from pathlib import Path
from statistics import mean


LABELING_PATH = Path("labeling_candidates.json")

# ============================================================
# Configuration
# ============================================================

K = 5

# Seuil minimum du reranker_score
SCORE_THRESHOLD = 0.30


# ============================================================
# Chargement
# ============================================================

def load_data():

    if not LABELING_PATH.exists():
        raise FileNotFoundError(
            f"{LABELING_PATH} introuvable."
        )

    with open(LABELING_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# Filtrage
# ============================================================

def filter_results(results):
    """
    Conserve uniquement les candidats dont le
    reranker_score >= SCORE_THRESHOLD.

    Les candidats avec un score inférieur au seuil
    sont complètement ignorés.
    """

    filtered = [
        r
        for r in results
        if r.get("reranker_score", 0) >= SCORE_THRESHOLD
    ]

    return filtered


# ============================================================
# Métriques
# ============================================================

def precision_at_k(results, k):
    """
    Precision@K

    Nombre de documents pertinents dans les K premiers
    / nombre de documents effectivement évalués dans le top K.

    Ici, les documents avec score < seuil ont déjà été supprimés.
    """

    top_k = results[:k]

    if not top_k:
        return 0.0

    relevant = sum(
        1
        for r in top_k
        if r["relevance"] is not None
        and r["relevance"] > 0
    )

    return relevant / len(top_k)


def recall_at_k(results, k):
    """
    Recall@K

    Nombre de documents pertinents retrouvés dans les K premiers
    / nombre total de documents pertinents parmi les documents
      conservés après filtrage du score.
    """

    relevant_total = sum(
        1
        for r in results
        if r["relevance"] is not None
        and r["relevance"] > 0
    )

    if relevant_total == 0:
        return 0.0

    top_k = results[:k]

    relevant_found = sum(
        1
        for r in top_k
        if r["relevance"] is not None
        and r["relevance"] > 0
    )

    return relevant_found / relevant_total


def f1_at_k(results, k):
    """
    F1@K = 2 * Precision * Recall / (Precision + Recall)
    """

    p = precision_at_k(results, k)
    r = recall_at_k(results, k)

    if p + r == 0:
        return 0.0

    return 2 * p * r / (p + r)


def reciprocal_rank(results):
    """
    Reciprocal Rank.

    1 / rang du premier document pertinent.
    """

    for rank, result in enumerate(results, start=1):

        relevance = result["relevance"]

        if relevance is not None and relevance > 0:
            return 1.0 / rank

    return 0.0


def ndcg_at_k(results, k):
    """
    nDCG@K avec :

        0 = non pertinent
        1 = pertinent
        2 = très pertinent

    Seuls les candidats ayant un score >= seuil
    sont pris en compte.
    """

    def dcg(items):

        score = 0.0

        for rank, result in enumerate(items[:k], start=1):

            relevance = result["relevance"]

            if relevance is None:
                relevance = 0

            score += relevance / math.log2(rank + 1)

        return score

    # DCG réel
    actual_dcg = dcg(results)

    # Documents jugés
    judged = [
        r
        for r in results
        if r["relevance"] is not None
    ]

    # Classement idéal
    ideal_results = sorted(
        judged,
        key=lambda r: r["relevance"],
        reverse=True,
    )

    ideal_dcg = dcg(ideal_results)

    if ideal_dcg == 0:
        return 0.0

    return actual_dcg / ideal_dcg


# ============================================================
# Évaluation d'une requête
# ============================================================

def evaluate_query(results, k):

    return {
        f"precision@{k}": precision_at_k(
            results,
            k
        ),

        f"recall@{k}": recall_at_k(
            results,
            k
        ),

        f"f1@{k}": f1_at_k(
            results,
            k
        ),

        "mrr": reciprocal_rank(
            results
        ),

        f"ndcg@{k}": ndcg_at_k(
            results,
            k
        ),
    }


# ============================================================
# Affichage
# ============================================================

def print_query_results(rows, k):

    print("\n" + "=" * 110)
    print("MÉTRIQUES PAR REQUÊTE")
    print("=" * 110)

    header = (
        f"{'ID':<8}"
        f"{'Catégorie':<18}"
        f"{'Docs':<8}"
        f"{'P@'+str(k):<10}"
        f"{'R@'+str(k):<10}"
        f"{'F1@'+str(k):<10}"
        f"{'MRR':<10}"
        f"{'nDCG@'+str(k):<10}"
    )

    print(header)
    print("-" * 110)

    for row in rows:

        print(
            f"{row['query_id']:<8}"
            f"{row['category']:<18}"
            f"{row['num_candidates']:<8}"
            f"{row[f'precision@{k}']:<10.3f}"
            f"{row[f'recall@{k}']:<10.3f}"
            f"{row[f'f1@{k}']:<10.3f}"
            f"{row['mrr']:<10.3f}"
            f"{row[f'ndcg@{k}']:<10.3f}"
        )


def print_average(title, rows, k):

    print("\n" + "=" * 90)
    print(title)
    print("=" * 90)

    metrics = [
        f"precision@{k}",
        f"recall@{k}",
        f"f1@{k}",
        "mrr",
        f"ndcg@{k}",
    ]

    for metric in metrics:

        values = [
            row[metric]
            for row in rows
        ]

        print(
            f"{metric:<15}: {mean(values):.3f}"
        )


def print_category_results(rows, k):

    print("\n" + "=" * 90)
    print("MÉTRIQUES PAR CATÉGORIE")
    print("=" * 90)

    categories = sorted(
        set(
            row["category"]
            for row in rows
        )
    )

    metrics = [
        f"precision@{k}",
        f"recall@{k}",
        f"f1@{k}",
        "mrr",
        f"ndcg@{k}",
    ]

    for category in categories:

        subset = [
            row
            for row in rows
            if row["category"] == category
        ]

        print(
            f"\n[{category}] "
            f"({len(subset)} requêtes)"
        )

        for metric in metrics:

            values = [
                row[metric]
                for row in subset
            ]

            print(
                f"  {metric:<15}: "
                f"{mean(values):.3f}"
            )


# ============================================================
# Statistiques des jugements
# ============================================================

def print_relevance_statistics(data):

    print("\n" + "=" * 90)
    print("STATISTIQUES DES JUGEMENTS APRÈS FILTRAGE")
    print("=" * 90)

    total_queries = len(data)

    evaluated_queries = 0
    ignored_queries = 0

    total_documents = 0
    ignored_documents = 0

    relevant_documents = 0
    highly_relevant_documents = 0
    non_relevant_documents = 0

    for payload in data.values():

        candidates = payload["candidates"]

        filtered = filter_results(candidates)

        if not filtered:
            ignored_queries += 1
            ignored_documents += len(candidates)
            continue

        evaluated_queries += 1

        # Documents sous le seuil
        ignored_documents += (
            len(candidates) - len(filtered)
        )

        for result in filtered:

            relevance = result["relevance"]

            if relevance is None:
                continue

            total_documents += 1

            if relevance == 0:
                non_relevant_documents += 1

            elif relevance == 1:
                relevant_documents += 1

            elif relevance == 2:
                highly_relevant_documents += 1

    print(f"Requêtes totales       : {total_queries}")
    print(f"Requêtes évaluées      : {evaluated_queries}")
    print(f"Requêtes ignorées      : {ignored_queries}")

    print(f"Documents conservés    : {total_documents}")
    print(f"Documents ignorés      : {ignored_documents}")

    print(f"Non pertinents         : {non_relevant_documents}")
    print(f"Pertinents (1)         : {relevant_documents}")
    print(f"Très pertinents (2)    : {highly_relevant_documents}")

    print(
        f"\nSeuil reranker_score   : "
        f"{SCORE_THRESHOLD:.2f}"
    )


# ============================================================
# Main
# ============================================================

def main():

    data = load_data()

    rows = []

    for query_id, payload in data.items():

        results = payload["candidates"]

        # ====================================================
        # FILTRAGE PAR SCORE
        # ====================================================

        filtered_results = filter_results(results)

        # Si aucun candidat ne dépasse le seuil,
        # on ignore complètement la requête.
        if not filtered_results:
            continue

        # On ne garde que les candidats évaluables
        judged = [
            r
            for r in filtered_results
            if r["relevance"] is not None
        ]

        if not judged:
            continue

        # ====================================================
        # MÉTRIQUES
        # ====================================================

        metrics = evaluate_query(
            filtered_results,
            K
        )

        row = {
            "query_id": query_id,
            "category": payload["category"],
            "query": payload["query"],
            "num_candidates": len(filtered_results),
            **metrics,
        }

        rows.append(row)

    if not rows:

        print(
            "Aucune requête évaluable dans "
            f"{LABELING_PATH}"
        )

        return

    # ========================================================
    # AFFICHAGE
    # ========================================================

    print_relevance_statistics(data)

    print_query_results(
        rows,
        K
    )

    print_average(
        "MOYENNES GLOBALES",
        rows,
        K
    )

    print_category_results(
        rows,
        K
    )


if __name__ == "__main__":
    main()