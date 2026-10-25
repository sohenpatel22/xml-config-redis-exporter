# XML to Redis exporter

This command-line app reads subdomains and cookie values from an XML file and writes them to Redis. Docker Compose runs Redis and the Python exporter in separate containers.

## Run it

You need Docker Engine on Linux and the Docker Compose plugin. From this directory, run:

```sh
./export.sh -v /path/to/config.xml
```

The `-v` option prints each Redis key written. Without it, the script prints a short summary. You can try the included configuration with:

```sh
./export.sh -v ./sample/config.xml
```

The sample contains 38 subdomains and 46 cookies, so 47 keys are written in total.
The exporter uses host networking to connect to Redis on `127.0.0.1`; Redis is published on localhost only. This avoids bridge-network connectivity issues in containerized Linux environments.

## Redis keys

- `subdomains` stores the subdomains as a JSON array.
- `cookie:<NAME>:<HOST>` stores the cookie value as a string.

For example, `cookie:dlp-avast:amazon` contains `mmm_amz_dlp_777_ppc_m`. The cookie values are kept as they appear in the XML.

Redis data is kept in a Docker volume between runs. To remove the volume as well as the containers, run:

```sh
docker compose down -v
```

## Tests

The tests use a small fake Redis client, so Redis does not need to be running:

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest -q
```
