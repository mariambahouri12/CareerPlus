"""
Script d'évaluation du pipeline de recherche hybride (FAISS + BM25 + RRF + reranker).

Usage:
    # Étape 1 — génère les résultats pour chaque requête de test, à juger à la main
    python eval_retrieval.py label

    # Étape 2 — une fois qrels.json rempli, calcule les métriques IR
    python eval_retrieval.py eval

Pourquoi ces deux étapes ?
    On ne peut pas calculer de Precision/Recall/nDCG sans savoir quels jobs sont
    "vraiment pertinents" pour chaque requête (jugement de pertinence = "qrels").
    Le mode `label` vous aide à construire ces jugements rapidement en vous montrant
    les résultats actuels ; vous n'avez qu'à noter 0/1/2 à côté de chaque URL.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

from rag.retriever import JobRetriever

QRELS_PATH = Path("qrels.json")
LABELING_OUTPUT_PATH = Path("labeling_candidates.json")

# ----------------------------------------------------------------------------
# Jeu de requêtes de test.
#
# Catégories volontairement variées pour stresser chaque composant du pipeline :
#   - "paraphrase"   : aucun mot-clé commun avec les offres -> teste FAISS seul
#   - "keyword"      : terme technique exact (stack, outil) -> teste BM25 seul
#   - "out_of_domain": requête hors sujet -> les scores doivent être bas
#   - "ambiguous"     : plusieurs bons candidats + distracteurs proches
#
# Adaptez/complétez cette liste avec des requêtes représentatives de vos vrais
# utilisateurs (ex: à partir de vos logs de prod une fois disponibles).
# ----------------------------------------------------------------------------

TEST_QUERIES = [
    # --- paraphrases (pas de mot-clé exact partagé) ---
    {
        "id": "q1",
        "category": "paraphrase",
        "query": "poste junior pour accompagner des entreprises dans leur transformation numérique par les données",
    },
    {
        "id": "q2",
        "category": "paraphrase",
        "query": "job de fin d'études autour de l'intelligence artificielle en agence conseil",
    },
    {
        "id": "q3",
        "category": "paraphrase",
        "query": "opportunité pour aider des grands groupes à mieux exploiter leurs données",
    },

    # --- mots-clés / stacks techniques précis ---
    {
        "id": "q4",
        "category": "keyword",
        "query": "C++",
    },
    {
        "id": "q5",
        "category": "keyword",
        "query": "Power BI",
    },
    {
        "id": "q6",
        "category": "keyword",
        "query": "Python SQL Google Analytics",
    },
    {
        "id": "q7",
        "category": "keyword",
        "query": "MLOps RAG architecture agentique",
    },

    # --- hors domaine (doit renvoyer peu / rien de pertinent) ---
    {
        "id": "q8",
        "category": "out_of_domain",
        "query": "recette de tarte aux pommes",
    },
    {
        "id": "q9",
        "category": "out_of_domain",
        "query": "location appartement Paris 3 pièces",
    },
    {
        "id": "q10",
        "category": "out_of_domain",
        "query": "meilleur restaurant italien Lyon",
    },

    # --- ambiguës / multi-candidats proches ---
    {
        "id": "q11",
        "category": "ambiguous",
        "query": "stage data",
    },
    {
        "id": "q12",
        "category": "ambiguous",
        "query": "consultant IA",
    },
    {
        "id": "q13",
        "category": "ambiguous",
        "query": "stage à Paris dans la tech",
    },

    # --- requêtes réalistes standard ---
    {
        "id": "q14",
        "category": "standard",
        "query": "Stage en stratégie Data et IA dans un cabinet de conseil",
    },
    {
        "id": "q15",
        "category": "standard",
        "query": "alternance data engineer",
    },
    {
        "id": "q16",
        "category": "standard",
        "query": "stage rémunéré data science 6 mois Paris",
    },
    {
        "id": "q17",
        "category": "standard",
        "query": "entreprise avec télétravail flexible pour un stage data",
    },
]


def run_labeling(top_k: int = 5) -> None:
    """
    Lance chaque requête de test sur le pipeline réel et affiche les résultats
    pour jugement manuel. Écrit aussi un JSON pré-rempli (relevance=null) que
    vous éditez ensuite à la main pour produire qrels.json.
    """

    retriever = JobRetriever()

    candidates: Dict[str, List[Dict]] = {}

    for item in TEST_QUERIES:
        query_id = item["id"]
        query = item["query"]
        category = item["category"]

        results = retriever.search(query=query, top_k=top_k, retrieval_k=30)

        print(f"\n=== [{query_id}] ({category}) \"{query}\" ===")

        entries = []
        for rank, r in enumerate(results, start=1):
            job = r["job"]
            url = job.get("url", "?")
            title = job.get("title", "?")
            company = job.get("company", "?")

            print(
                f"  {rank}. score={r.get('reranker_score', 0):.3f}  "
                f"faiss={r.get('faiss_score', 0):.3f}  "
                f"bm25={r.get('bm25_score', 0):.3f}  "
                f"[{title} @ {company}]  {url}"
            )

            entries.append(
                {
                    "index": r["index"],
                    "url": url,
                    "title": title,
                    "company": company,
                    "reranker_score": r.get("reranker_score"),
                    # A remplir à la main dans qrels.json :
                    #   2 = très pertinent, 1 = pertinent, 0 = non pertinent
                    "relevance": None,
                }
            )

        candidates[query_id] = {
            "query": query,
            "category": category,
            "candidates": entries,
        }

    LABELING_OUTPUT_PATH.write_text(
        json.dumps(candidates, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"\n\n➡ Résultats écrits dans {LABELING_OUTPUT_PATH}")
    print(
        "Éditez ce fichier : remplacez chaque \"relevance\": null par 0, 1 ou 2, "
        f"puis enregistrez-le sous {QRELS_PATH} au format attendu par le mode 'eval' "
        "(voir build_qrels_from_labeling ci-dessous)."
    )


def build_qrels_from_labeling() -> Dict[str, Dict[str, int]]:
    """
    Convertit labeling_candidates.json (une fois les 'relevance' remplis à la
    main) vers le format qrels attendu par les métriques : {query_id: {job_index: relevance}}.
    """

    if not LABELING_OUTPUT_PATH.exists():
        raise FileNotFoundError(
            f"{LABELING_OUTPUT_PATH} introuvable — lancez d'abord `python eval_retrieval.py label`."
        )

    data = json.loads(LABELING_OUTPUT_PATH.read_text(encoding="utf-8"))

    qrels: Dict[str, Dict[str, int]] = {}

    for query_id, payload in data.items():
        judged = {}
        for cand in payload["candidates"]:
            if cand["relevance"] is not None:
                judged[str(cand["index"])] = int(cand["relevance"])
        qrels[query_id] = judged

    QRELS_PATH.write_text(json.dumps(qrels, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"qrels générés dans {QRELS_PATH} à partir de {LABELING_OUTPUT_PATH}")

    return qrels


# ----------------------------------------------------------------------------
# Métriques IR (implémentation directe, sans dépendance externe)
# ----------------------------------------------------------------------------


def precision_at_k(ranked_indices: List[int], relevant: set, k: int) -> float:
    top = ranked_indices[:k]
    if not top:
        return 0.0
    hits = sum(1 for i in top if i in relevant)
    return hits / len(top)


def recall_at_k(ranked_indices: List[int], relevant: set, k: int) -> float:
    if not relevant:
        return 0.0
    top = ranked_indices[:k]
    hits = sum(1 for i in top if i in relevant)
    return hits / len(relevant)


def mrr(ranked_indices: List[int], relevant: set) -> float:
    for rank, i in enumerate(ranked_indices, start=1):
        if i in relevant:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(ranked_indices: List[int], graded_relevance: Dict[int, int], k: int) -> float:
    import math

    def dcg(indices: List[int]) -> float:
        return sum(
            graded_relevance.get(idx, 0) / math.log2(rank + 1)
            for rank, idx in enumerate(indices[:k], start=1)
        )

    ideal_order = sorted(graded_relevance.keys(), key=lambda i: graded_relevance[i], reverse=True)
    ideal = dcg(ideal_order)
    actual = dcg(ranked_indices)

    return actual / ideal if ideal > 0 else 0.0


def run_eval(top_k: int = 5) -> None:
    if not QRELS_PATH.exists():
        print(f"{QRELS_PATH} introuvable. Génération automatique depuis {LABELING_OUTPUT_PATH}...")
        build_qrels_from_labeling()

    qrels = json.loads(QRELS_PATH.read_text(encoding="utf-8"))
    retriever = JobRetriever()

    query_by_id = {q["id"]: q for q in TEST_QUERIES}

    rows = []

    for query_id, judged in qrels.items():
        if not judged:
            continue  # requête pas encore jugée, on l'ignore

        query = query_by_id[query_id]["query"]
        category = query_by_id[query_id]["category"]

        results = retriever.search(query=query, top_k=top_k, retrieval_k=30)
        ranked_indices = [r["index"] for r in results]

        graded_relevance = {int(idx): rel for idx, rel in judged.items()}
        relevant_set = {idx for idx, rel in graded_relevance.items() if rel > 0}

        row = {
            "query_id": query_id,
            "category": category,
            f"precision@{top_k}": precision_at_k(ranked_indices, relevant_set, top_k),
            f"recall@{top_k}": recall_at_k(ranked_indices, relevant_set, top_k),
            "mrr": mrr(ranked_indices, relevant_set),
            f"ndcg@{top_k}": ndcg_at_k(ranked_indices, graded_relevance, top_k),
        }
        rows.append(row)

    if not rows:
        print("Aucune requête jugée dans qrels.json — rien à évaluer.")
        return

    # Affichage par requête
    print(f"\n{'query_id':<8}{'category':<15}{'P@'+str(top_k):<10}{'R@'+str(top_k):<10}{'MRR':<10}{'nDCG@'+str(top_k):<10}")
    for row in rows:
        print(
            f"{row['query_id']:<8}{row['category']:<15}"
            f"{row[f'precision@{top_k}']:<10.3f}"
            f"{row[f'recall@{top_k}']:<10.3f}"
            f"{row['mrr']:<10.3f}"
            f"{row[f'ndcg@{top_k}']:<10.3f}"
        )

    # Moyennes globales + par catégorie
    def avg(key: str, subset=rows):
        return sum(r[key] for r in subset) / len(subset)

    print("\n--- Moyennes globales ---")
    for key in [f"precision@{top_k}", f"recall@{top_k}", "mrr", f"ndcg@{top_k}"]:
        print(f"{key}: {avg(key):.3f}")

    categories = sorted({r["category"] for r in rows})
    print("\n--- Moyennes par catégorie ---")
    for cat in categories:
        subset = [r for r in rows if r["category"] == cat]
        print(f"\n[{cat}] ({len(subset)} requêtes jugées)")
        for key in [f"precision@{top_k}", f"recall@{top_k}", "mrr", f"ndcg@{top_k}"]:
            print(f"  {key}: {avg(key, subset):.3f}")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "label"

    if mode == "label":
        run_labeling()
    elif mode == "eval":
        run_eval()
    else:
        print("Usage: python eval_retrieval.py [label|eval]")