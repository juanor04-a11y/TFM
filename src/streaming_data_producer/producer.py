"""
Con esta clase vamos a simular la ingesta streaming the tickets a partir de plataformas como Service Now.
Como estamos usando datos simulados en este caso usamos los datos que hemos creado en data/raw/
Esto podría reemplazarse mediante la ingesta de tickets de plataformas como Services Now o Jira

Posteriormente se usó la clase producer_confluent ya que esta se conecta a Confluent Cloud. Esta clase
se usó para las pruebas iniciales de streaming y está conectada a un servidor local de Kafka, que se generó usando Docker.
"""


from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import pandas as pd
from kafka import KafkaProducer


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", type=Path, default=Path("../../data/raw/synthetic_ott_tickets.csv"))
    p.add_argument("--bootstrap-server", default="localhost:9092")
    p.add_argument("--topic", default="ott-tickets")
    p.add_argument("--interval", type=float, default=1.0)
    p.add_argument("--limit", type=int, default=None)
    return p.parse_args()


def clean_value(value):
    if pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return value


def main():
    args = parse_args()

    if not args.csv.exists():
        raise FileNotFoundError(f"CSV not found: {args.csv.resolve()}")

    df = pd.read_csv(args.csv)
    if args.limit:
        df = df.head(args.limit)

    producer = KafkaProducer(
        bootstrap_servers=args.bootstrap_server,
        key_serializer=lambda x: x.encode("utf-8"),
        value_serializer=lambda x: json.dumps(x, ensure_ascii=False, default=str).encode("utf-8"),
        acks="all",
        retries=5,
    )

    print(f"Publishing {len(df)} tickets to {args.topic}")

    for i, row in df.iterrows():
        payload = {k: clean_value(v) for k, v in row.to_dict().items()}
        ticket_id = str(payload.get("ticket_id", f"row-{i}"))

        metadata = producer.send(
            args.topic,
            key=ticket_id,
            value=payload
        ).get(timeout=10)

        print(f"{ticket_id} -> partition={metadata.partition}, offset={metadata.offset}")

        if args.interval > 0:
            time.sleep(args.interval)

    producer.flush()
    producer.close()


if __name__ == "__main__":
    main()
