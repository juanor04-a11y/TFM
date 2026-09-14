"""
Con esta clase vamos a simular la ingesta streaming the tickets a partir de plataformas como Service Now.
Como estamos usando datos simulados en este caso usamos los datos que hemos creado en data/raw/
Esto podría reemplazarse mediante la ingesta de tickets de plataformas como Services Now o Jira

Esta clase se utiliza para generar tickets de Streaming en Kafka dentro de Confluent Cloud
"""

import os
import json
import time
import argparse
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from kafka import KafkaProducer


load_dotenv()


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--csv",
        type=Path,
        default=Path("../../data/raw/synthetic_ott_tickets.csv")
    )

    parser.add_argument(
        "--interval",
        type=float,
        default=1.0
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None
    )

    return parser.parse_args()


def clean_value(value):
    if pd.isna(value):
        return None

    if isinstance(value, pd.Timestamp):
        return value.isoformat()

    return value


def main():
    args = parse_args()

    bootstrap_server = os.environ["KAFKA_BOOTSTRAP_SERVER"]
    api_key = os.environ["KAFKA_API_KEY"]
    api_secret = os.environ["KAFKA_API_SECRET"]
    topic = os.getenv("KAFKA_TOPIC", "ott-tickets")

    if not args.csv.exists():
        raise FileNotFoundError(
            f"CSV not found: {args.csv.resolve()}"
        )

    df = pd.read_csv(args.csv)

    if args.limit:
        df = df.head(args.limit)

    producer = KafkaProducer(
        bootstrap_servers=bootstrap_server,

        security_protocol="SASL_SSL",
        sasl_mechanism="PLAIN",
        sasl_plain_username=api_key,
        sasl_plain_password=api_secret,

        key_serializer=lambda key:
            key.encode("utf-8"),

        value_serializer=lambda value:
            json.dumps(
                value,
                ensure_ascii=False,
                default=str
            ).encode("utf-8"),

        acks="all",
        retries=5
    )

    print(
        f"Publishing {len(df)} tickets "
        f"to '{topic}'"
    )

    for index, row in df.iterrows():

        payload = {
            column: clean_value(value)
            for column, value
            in row.to_dict().items()
        }

        ticket_id = str(
            payload.get(
                "ticket_id",
                f"row-{index}"
            )
        )

        metadata = producer.send(
            topic,
            key=ticket_id,
            value=payload
        ).get(timeout=20)

        print(
            f"[{index + 1}/{len(df)}] "
            f"{ticket_id} -> "
            f"partition={metadata.partition}, "
            f"offset={metadata.offset}"
        )

        if args.interval > 0:
            time.sleep(args.interval)

    producer.flush()
    producer.close()

    print("Finished.")


if __name__ == "__main__":
    main()