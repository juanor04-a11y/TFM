from __future__ import annotations

import json
import random
from typing import Any


class IncidentSummarizer:
    """
    Generates structured operational summaries for detected
    ticket clusters using an OpenAI-compatible client.

    The class does not perform clustering. It only interprets
    groups produced by the upstream pipeline.
    """

    EXPECTED_FIELDS = [
        "generated_title",
        "generated_summary",
        "probable_issue",
        "affected_scope",
        "recommended_action",
        "warning",
    ]

    SYSTEM_PROMPT = """
You are an assistant supporting the operation of an OTT platform.

You receive support tickets that have been automatically grouped
using semantic embeddings and clustering.

Your task is to summarize the operational information contained
in the supplied tickets.

Important rules:
- Base your conclusions only on the supplied tickets.
- Do not invent technical information.
- Do not assume that all tickets necessarily have the same root cause.
- Distinguish observations from probable interpretations.
- Recommended actions must be reasonable investigation or operational
  next steps based only on the available evidence.
- If the cluster appears to contain multiple different problems,
  explicitly indicate this in the warning.
- If the evidence is insufficient to identify a probable issue,
  say so explicitly.

Return ONLY valid JSON with exactly this structure:

{
  "generated_title": "...",
  "generated_summary": "...",
  "probable_issue": "...",
  "affected_scope": "...",
  "recommended_action": "...",
  "warning": "..."
}
"""

    def __init__(
        self,
        client: Any,
        model_name: str,
        max_tickets: int = 20,
        random_seed: int = 42,
    ):
        if max_tickets < 1:
            raise ValueError(
                "max_tickets must be at least 1."
            )

        self.client = client
        self.model_name = model_name
        self.max_tickets = int(max_tickets)
        self.random_seed = int(random_seed)

    def sample_tickets(
        self,
        ticket_texts,
        cluster_id: int,
    ) -> list[str]:
        """
        Select a deterministic random sample of ticket texts.

        A cluster-specific seed ensures reproducibility while avoiding
        selection of exactly the same sequence for every cluster.
        """

        if ticket_texts is None:
            return []

        texts = [
            str(text).strip()
            for text in ticket_texts
            if text is not None
            and str(text).strip()
        ]

        if len(texts) <= self.max_tickets:
            return texts

        rng = random.Random(
            self.random_seed + int(cluster_id)
        )

        return rng.sample(
            texts,
            self.max_tickets,
        )

    def _build_user_prompt(
        self,
        cluster_id: int,
        ticket_count: int,
        ticket_texts: list[str],
    ) -> str:
        tickets = "\n\n".join(
            f"Ticket {index + 1}: {text}"
            for index, text in enumerate(ticket_texts)
        )

        return f"""
Cluster ID: {cluster_id}
Total number of tickets in cluster: {ticket_count}
Number of tickets supplied as context: {len(ticket_texts)}

Tickets analyzed:
{tickets}
"""

    def _parse_response(
        self,
        response_text: str,
    ) -> dict:
        if not response_text:
            raise ValueError(
                "The GenAI service returned an empty response."
            )

        result = json.loads(
            response_text
        )

        missing_fields = [
            field
            for field in self.EXPECTED_FIELDS
            if field not in result
        ]

        if missing_fields:
            raise ValueError(
                "Missing fields in GenAI response: "
                f"{missing_fields}"
            )

        return result

    def summarize(
        self,
        cluster_id: int,
        ticket_count: int,
        ticket_texts,
    ) -> dict:
        """
        Generate one structured incident-group summary.
        """

        sampled_tickets = self.sample_tickets(
            ticket_texts=ticket_texts,
            cluster_id=cluster_id,
        )

        if not sampled_tickets:
            raise ValueError(
                f"Cluster {cluster_id} contains no valid ticket texts."
            )

        user_prompt = self._build_user_prompt(
            cluster_id=cluster_id,
            ticket_count=ticket_count,
            ticket_texts=sampled_tickets,
        )

        response = (
            self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": self.SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
            )
        )

        response_text = (
            response
            .choices[0]
            .message
            .content
        )

        generated = self._parse_response(
            response_text
        )

        return {
            "cluster_id": int(cluster_id),
            "ticket_count": int(ticket_count),
            "tickets_used_for_context":
                len(sampled_tickets),
            **generated,
        }