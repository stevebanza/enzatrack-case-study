# Excerpt from EnzaTrack (full source is private). Shown to illustrate the design;
# it depends on the application's models and is not runnable on its own.
# © Steve KUBENGA BANZA. All rights reserved.
#
# Best-practice mining: approved, shareable, well-rated lessons that are linked by
# semantic similarity form clusters; each cluster of 3+ lessons becomes a candidate
# best practice, with metrics computed from its supporting lessons.

from __future__ import annotations

import hashlib
import math
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Iterable, List, Tuple

from django.apps import apps
from django.db import models

from core.constants import Visibility
from core.constants.workflow_status import Status
from core.models.lesson_learned import LessonLearned

@dataclass
class Cluster:
    key: str
    lesson_ids: List[int]
    edges: List[Tuple[int, int, float]]  # (src_id, dst_id, similarity)


def _hash_key(parts: Iterable[str]) -> str:
    return hashlib.sha256("|".join([p or "" for p in parts]).encode("utf-8")).hexdigest()[:32]


def _fetch_candidate_lessons(min_rating: float = 3.5, min_evidence: int = 2) -> List[LessonLearned]:
    """
    Pull only high-signal, approved, shareable lessons across orgs.
    """
    qs = (LessonLearned.objects
          .filter(status=Status.APPROVED)
          .filter(visibility__in=[Visibility.PARTNER, Visibility.PUBLIC])
          .filter(is_valid=True)
          .only("id", "programme_id", "department_id", "organization_id",
                "ratings_avg", "evidence_strength", "adoption_count",
                "title", "summary", "context", "actions", "outcomes",
                "lesson", "recommendations")
          )
    if min_rating:
        qs = qs.filter(models.Q(ratings_avg__gte=min_rating) | models.Q(ratings_avg__isnull=True))
    if min_evidence:
        qs = qs.filter(models.Q(evidence_strength__gte=min_evidence) | models.Q(evidence_strength__isnull=True))
    return list(qs[:5000])  # safety cap; tune as needed


def _cluster_with_lesson_similar(lessons: List[LessonLearned], min_sim: float = 0.78) -> List[Cluster]:
    """
    If a LessonSimilar table exists, build connected components by similarity.
    """
    try:
        LessonSimilar = apps.get_model("core", "LessonSimilar")
    except LookupError:
        return []

    id_set = {l.id for l in lessons}
    edges = []
    for row in (LessonSimilar.objects
                .filter(source_lesson_id__in=id_set, target_lesson_id__in=id_set, score__gte=min_sim)
                .values_list("source_lesson_id", "target_lesson_id", "score")):
        edges.append((int(row[0]), int(row[1]), float(row[2])))

    # build graph
    adj = defaultdict(list)
    for a, b, s in edges:
        adj[a].append((b, s))
        adj[b].append((a, s))

    visited = set()
    clusters: List[Cluster] = []

    for root in id_set:
        if root in visited:
            continue
        comp = []
        comp_edges = []
        dq = deque([root]); visited.add(root)
        while dq:
            u = dq.popleft()
            comp.append(u)
            for v, s in adj[u]:
                comp_edges.append((u, v, s))
                if v not in visited:
                    visited.add(v); dq.append(v)

        if len(comp) >= 3:  # minimum cluster size
            key = _hash_key([str(sorted(comp)), f"{min_sim:.2f}"])
            clusters.append(Cluster(key=key, lesson_ids=sorted(comp), edges=comp_edges))

    return clusters


def _fallback_cluster_by_program_domain(lessons: List[LessonLearned]) -> List[Cluster]:
    """
    Fallback: simple grouping by programme + top-level domain overlap.
    """
    # domains m2m available via prefetch? Keep a simple bucket by programme.
    buckets = defaultdict(list)
    for l in lessons:
        buckets[l.programme_id].append(l.id)

    clusters: List[Cluster] = []
    for prog, ids in buckets.items():
        if len(ids) >= 3:
            key = _hash_key([f"prog:{prog}", "fallback"])
            clusters.append(Cluster(key=key, lesson_ids=sorted(ids), edges=[]))
    return clusters


def _compute_cluster_metrics(lesson_qs: Iterable[LessonLearned]) -> Tuple[float, float, int, float]:
    """
    Returns: (avg_rating, avg_evidence_strength, support_count, adoption_rate)
    adoption_rate: min(1.0, log(1+sum(adoption_count))/log(1+N * 10))  # softly normalized 0..1
    """
    L = list(lesson_qs)
    if not L:
        return (0.0, 0.0, 0, 0.0)
    rs = [l.ratings_avg for l in L if l.ratings_avg is not None]
    es = [float(l.evidence_strength) for l in L if l.evidence_strength is not None]
    ac = [int(l.adoption_count or 0) for l in L]
    support_count = len(L)
    avg_rating = sum(rs) / len(rs) if rs else None
    avg_evidence = (sum(es) / len(es)) if es else None
    # adoption_rate in 0..1 with soft log scaling (assume 10 adoptions per lesson = strong)
    denom = max(1, support_count * 10)
    ar = min(1.0, math.log1p(sum(ac)) / math.log1p(denom))
    return (avg_rating or 0.0, avg_evidence or 0.0, support_count, ar)
