
"""
Con esta clase generamos los tickets simulados que utilizaremos en el proyecto.
"""
from __future__ import annotations

import argparse
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = PROJECT_ROOT / "data"


@dataclass(frozen=True)
class IncidentTemplate:
    category: str
    platform: str
    device_type: str
    country: str
    service: str
    assigned_team: str
    error_code: str
    titles: tuple[str, ...]
    descriptions: tuple[str, ...]


INCIDENT_TEMPLATES = [
    IncidentTemplate(
        category="DRM",
        platform="Tizen",
        device_type="Smart TV",
        country="DK",
        service="Live TV",
        assigned_team="OTT Playback",
        error_code="DRM_403",
        titles=(
            "Playback fails on Samsung TV",
            "DRM error on Samsung devices",
            "Black screen when starting live TV",
            "Samsung playback returns 403",
        ),
        descriptions=(
            "Several customers cannot start playback on Samsung Smart TVs. DRM authorization returns error 403.",
            "Playback is failing on Tizen devices. Users report a black screen and DRM errors.",
            "Live TV does not start on Samsung televisions. The client reports DRM authorization failure.",
            "Users on Samsung Smart TV are unable to play content. Error 403 is observed during DRM validation.",
        ),
    ),
    IncidentTemplate(
        category="Authentication",
        platform="Android",
        device_type="Mobile",
        country="DK",
        service="Login",
        assigned_team="Identity",
        error_code="AUTH_401",
        titles=(
            "Android users cannot log in",
            "Login failing in Android app",
            "Authentication error on mobile",
            "401 when signing in on Android",
        ),
        descriptions=(
            "Customers using the Android app are unable to sign in and receive HTTP 401.",
            "Login attempts fail on Android mobile devices after entering valid credentials.",
            "Authentication requests from Android are rejected with 401 responses.",
            "The Android application does not complete login for multiple customers.",
        ),
    ),
    IncidentTemplate(
        category="CDN",
        platform="Web",
        device_type="Browser",
        country="DK",
        service="VOD",
        assigned_team="CDN Operations",
        error_code="CDN_BUFFERING",
        titles=(
            "High buffering on VOD",
            "VOD playback buffering in Denmark",
            "Slow video delivery from CDN",
            "Customers report repeated buffering",
        ),
        descriptions=(
            "VOD sessions show a significant increase in buffering for customers in Denmark.",
            "Users experience repeated buffering while watching on-demand content. CDN latency is elevated.",
            "Video delivery is slow and startup time has increased for browser clients.",
            "A high buffering ratio is observed across VOD sessions served by the primary CDN.",
        ),
    ),
    IncidentTemplate(
        category="Playback",
        platform="tvOS",
        device_type="Apple TV",
        country="SE",
        service="Live TV",
        assigned_team="OTT Playback",
        error_code="PLAYER_START",
        titles=(
            "Apple TV playback does not start",
            "Live TV fails on tvOS",
            "Player startup failure Apple TV",
            "Black screen on Apple TV",
        ),
        descriptions=(
            "Live channels do not start on Apple TV. The player remains on a black screen.",
            "tvOS clients are unable to initialize playback for live content.",
            "Customers report player startup failures on Apple TV devices.",
            "Playback requests on tvOS are accepted but video never starts.",
        ),
    ),
    IncidentTemplate(
        category="Metadata",
        platform="All",
        device_type="All",
        country="NO",
        service="EPG",
        assigned_team="Content Platform",
        error_code="EPG_MISSING",
        titles=(
            "EPG data missing",
            "TV guide has empty slots",
            "Missing programme information",
            "EPG not updating",
        ),
        descriptions=(
            "Programme guide data is missing for several channels in Norway.",
            "The EPG contains empty schedule slots and has not refreshed correctly.",
            "Customers cannot see programme titles for multiple live channels.",
            "TV guide metadata appears stale or missing across supported devices.",
        ),
    ),
    IncidentTemplate(
        category="Casting",
        platform="Chromecast",
        device_type="Casting Device",
        country="DK",
        service="VOD",
        assigned_team="OTT Playback",
        error_code="CAST_FAIL",
        titles=(
            "Chromecast playback fails",
            "Unable to cast VOD",
            "Cast session disconnects",
            "Chromecast cannot start stream",
        ),
        descriptions=(
            "Customers cannot start VOD playback through Chromecast.",
            "Casting begins but the session disconnects before video starts.",
            "The mobile app connects to Chromecast but playback fails to initialize.",
            "Chromecast sessions terminate unexpectedly during stream startup.",
        ),
    ),
    IncidentTemplate(
        category="Authorization",
        platform="All",
        device_type="All",
        country="DK",
        service="Subscription",
        assigned_team="Entitlements",
        error_code="ENTITLEMENT_DENIED",
        titles=(
            "Subscribed users cannot access content",
            "Entitlement check failing",
            "Subscription authorization denied",
            "Customers see not subscribed message",
        ),
        descriptions=(
            "Customers with an active subscription are denied access to entitled content.",
            "Entitlement validation incorrectly reports that users do not have a subscription.",
            "Valid subscribers receive an authorization denied response.",
            "Content access is blocked even though the subscription is active.",
        ),
    ),
    IncidentTemplate(
        category="Network",
        platform="Android TV",
        device_type="Set-top Box",
        country="DK",
        service="Live TV",
        assigned_team="Network Operations",
        error_code="TIMEOUT",
        titles=(
            "Live TV timeout on Android TV",
            "Stream timeout on set-top boxes",
            "Android TV loses connection",
            "Playback timeout on STB",
        ),
        descriptions=(
            "Android TV set-top boxes report connection timeouts while starting live channels.",
            "Live playback fails intermittently due to upstream timeout errors.",
            "Set-top boxes lose the streaming connection shortly after playback starts.",
            "Timeout errors are increasing for Android TV live sessions.",
        ),
    ),
]

STATUSES = ("Open", "In Progress", "Resolved", "Closed")
PRIORITIES = ("Low", "Medium", "High", "Critical")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a reproducible synthetic OTT ticket dataset for the TFM."
    )
    parser.add_argument("--tickets", type=int, default=1000, help="Total number of tickets.")
    parser.add_argument("--incidents", type=int, default=50, help="Number of underlying incidents.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help="Output directory.",
    )
    return parser.parse_args()


def mutate_text(text: str, rng: random.Random) -> str:
    """Introduce small realistic variations without destroying semantic meaning."""
    replacements = [
        ("customers", "users"),
        ("Customers", "Users"),
        ("cannot", "can't"),
        ("playback", "streaming"),
        ("fails", "is failing"),
        ("error", "issue"),
        ("device", "client"),
    ]
    if rng.random() < 0.35:
        old, new = rng.choice(replacements)
        text = text.replace(old, new)

    if rng.random() < 0.08 and len(text) > 20:
        # Small typo.
        idx = rng.randint(5, len(text) - 5)
        if text[idx].isalpha():
            text = text[:idx] + text[idx + 1 :]  # remove one character

    if rng.random() < 0.08:
        text += " Please investigate."

    return text


def choose_priority(rng: random.Random) -> str:
    return rng.choices(PRIORITIES, weights=(10, 45, 35, 10), k=1)[0]


def build_incidents(num_incidents: int, rng: random.Random) -> list[dict]:
    incidents = []
    start = datetime(2026, 1, 1, 0, 0, 0)

    for i in range(1, num_incidents + 1):
        template = rng.choice(INCIDENT_TEMPLATES)
        incident_start = start + timedelta(
            days=rng.randint(0, 180),
            hours=rng.randint(0, 23),
            minutes=rng.randint(0, 59),
        )
        incidents.append(
            {
                "incident_id": f"INC{i:04d}",
                "category": template.category,
                "platform": template.platform,
                "device_type": template.device_type,
                "country": template.country,
                "service": template.service,
                "assigned_team": template.assigned_team,
                "error_code": template.error_code,
                "incident_start": incident_start,
                "template": template,
            }
        )

    return incidents


def generate_dataset(total_tickets: int, num_incidents: int, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    if total_tickets < num_incidents:
        raise ValueError("--tickets must be >= --incidents")

    rng = random.Random(seed)
    incidents = build_incidents(num_incidents, rng)

    # Allocate most tickets to known incidents.
    isolated_count = max(1, int(total_tickets * 0.10))
    duplicate_count = max(1, int(total_tickets * 0.05))
    clustered_count = total_tickets - isolated_count - duplicate_count

    tickets: list[dict] = []

    for idx in range(clustered_count):
        incident = rng.choice(incidents)
        template: IncidentTemplate = incident["template"]
        created_at = incident["incident_start"] + timedelta(minutes=rng.randint(0, 240))
        resolution_minutes = rng.randint(20, 720)
        status = rng.choices(STATUSES, weights=(10, 20, 50, 20), k=1)[0]
        resolved_at = (
            created_at + timedelta(minutes=resolution_minutes)
            if status in ("Resolved", "Closed")
            else None
        )

        title = mutate_text(rng.choice(template.titles), rng)
        description = mutate_text(rng.choice(template.descriptions), rng)

        # Occasionally inject imperfect labels / nulls.
        category = template.category if rng.random() > 0.08 else rng.choice(
            [t.category for t in INCIDENT_TEMPLATES]
        )
        priority = choose_priority(rng)
        if rng.random() < 0.03:
            priority = None

        tickets.append(
            {
                "ticket_id": f"T{idx + 1:06d}",
                "created_at": created_at,
                "title": title,
                "description": description,
                "priority": priority,
                "status": status,
                "category": category,
                "platform": template.platform,
                "device_type": template.device_type,
                "country": template.country,
                "service": template.service,
                "assigned_team": template.assigned_team,
                "error_code": template.error_code,
                "resolved_at": resolved_at,
                "incident_id": incident["incident_id"],
                "is_isolated": False,
                "is_duplicate": False,
            }
        )

    # Isolated tickets should not belong to any known group.
    generic_isolated = [
        ("Remote control issue", "One customer reports that the remote control is not responding."),
        ("Subtitle preference reset", "Subtitle language preference resets after application restart."),
        ("Profile avatar not saved", "A user cannot save a new profile avatar."),
        ("Volume mismatch", "Volume level changes between two specific channels."),
        ("Search spelling result", "Search gives an unexpected result for one misspelled title."),
    ]
    for _ in range(isolated_count):
        idx = len(tickets) + 1
        title, description = rng.choice(generic_isolated)
        created_at = datetime(2026, 1, 1) + timedelta(
            days=rng.randint(0, 180),
            hours=rng.randint(0, 23),
            minutes=rng.randint(0, 59),
        )
        tickets.append(
            {
                "ticket_id": f"T{idx:06d}",
                "created_at": created_at,
                "title": mutate_text(title, rng),
                "description": mutate_text(description, rng),
                "priority": choose_priority(rng),
                "status": rng.choice(STATUSES),
                "category": "Other",
                "platform": rng.choice(("Web", "Android", "iOS", "Tizen")),
                "device_type": rng.choice(("Browser", "Mobile", "Smart TV")),
                "country": rng.choice(("DK", "SE", "NO")),
                "service": "Other",
                "assigned_team": "Customer Support",
                "error_code": None,
                "resolved_at": None,
                "incident_id": None,
                "is_isolated": True,
                "is_duplicate": False,
            }
        )

    # Add deliberate duplicates with a new ticket id.
    source_pool = tickets[:clustered_count]
    for _ in range(duplicate_count):
        original = rng.choice(source_pool).copy()
        idx = len(tickets) + 1
        original["ticket_id"] = f"T{idx:06d}"
        original["created_at"] = original["created_at"] + timedelta(minutes=rng.randint(1, 30))
        original["is_duplicate"] = True
        tickets.append(original)

    df = pd.DataFrame(tickets)

    # Shuffle rows while keeping reproducibility.
    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)

    ground_truth = pd.DataFrame(
        [
            {
                "incident_id": i["incident_id"],
                "category": i["category"],
                "platform": i["platform"],
                "device_type": i["device_type"],
                "country": i["country"],
                "service": i["service"],
                "assigned_team": i["assigned_team"],
                "error_code": i["error_code"],
                "incident_start": i["incident_start"],
            }
            for i in incidents
        ]
    )

    return df, ground_truth


def main() -> None:
    args = parse_args()

    raw_dir = args.out_dir / "raw"
    gt_dir = args.out_dir / "ground_truth"
    raw_dir.mkdir(parents=True, exist_ok=True)
    gt_dir.mkdir(parents=True, exist_ok=True)

    tickets, ground_truth = generate_dataset(
        total_tickets=args.tickets,
        num_incidents=args.incidents,
        seed=args.seed,
    )

    tickets_path = raw_dir / "synthetic_ott_tickets.csv"
    truth_path = gt_dir / "incident_ground_truth.csv"

    tickets.to_csv(tickets_path, index=False)
    ground_truth.to_csv(truth_path, index=False)

    print(f"Generated {len(tickets):,} tickets -> {tickets_path}")
    print(f"Generated {len(ground_truth):,} incidents -> {truth_path}")
    print("\nTicket breakdown:")
    print(f"  Isolated:   {int(tickets['is_isolated'].sum()):,}")
    print(f"  Duplicates: {int(tickets['is_duplicate'].sum()):,}")
    print(f"  With incident_id: {int(tickets['incident_id'].notna().sum()):,}")


if __name__ == "__main__":
    main()
