# Telegram over GRPC
Telegram client as a GRPC service

## Quick start
Get your api id and api hash [there](https://core.telegram.org/api/obtaining_api_id)
```
docker run -e API_ID=... -e API_HASH=... -it --rm telegram_grpc
```

## How to build
```
docker build -t telegram_grpc .
```

## Run and save the session
```
touch session
docker run -e API_ID=... -e API_HASH=... -v `pwd`/session:/telegram/session.session -it --rm telegram_grpc
```