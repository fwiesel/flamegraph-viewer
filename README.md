# Flamegraph Viewer

A viewer for flamegraphs stored in a database. Based on [nylas-perftools](https://github.com/nylas/nylas-perftools), but stripped down to the web-interface.
The data is currently stored in a redis database in redis sorted sets, where the score is a epoch timestamp. The key should identify the source of the flamegraph.
Each value is in the [flamegraph line format](https://github.com/brendangregg/FlameGraph#2-fold-stacks), optionally compressed with lz4.

## Build

```
docker build .
```

## Run

docker run -ti -e DB_URL=redis://<your-redis-url> -p 9999:5555 <image-id>

Then visit e.g. `http://localhost:5555?from=-15minutes` to see data from the past 15 minutes.

# Questions? Issues?

Don't hesitate to get in touch!
