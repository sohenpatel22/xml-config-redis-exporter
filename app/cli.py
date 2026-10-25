import argparse
import os
import sys
from pathlib import Path

import redis

from app.exporter import export_to_redis
from app.xml_parser import parse_xml


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Export subdomains and cookies from XML to Redis."
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="print the keys written"
    )
    parser.add_argument("xml_path", type=Path, help="path to the XML file")
    args = parser.parse_args(argv)

    try:
        data = parse_xml(args.xml_path)
        client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            db=int(os.getenv("REDIS_DB", "0")),
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
        client.ping()
        keys = export_to_redis(client, data)
    except (FileNotFoundError, ValueError, redis.RedisError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.verbose:
        print("\n".join(keys))
    else:
        print(f"Exported {len(keys)} keys to Redis.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
