# Telegram over GRPC
Telegram client as a GRPC service

[Docker hub](https://hub.docker.com/repository/docker/golovchen/telegram_grpc)

## Quick start
Get your api id and api hash [there](https://core.telegram.org/api/obtaining_api_id)
```shell
docker run -e API_ID=... -e API_HASH=... -p 50051:50051 -it --rm golovchen/telegram_grpc
```
Login with your phone number.

Now you can access the api at grpc://localhost:50051
```protobuf
service TelegramClient {
  rpc GetUser(GetUserRequest) returns (FullUser);
  rpc GetNewMessages(GetNewMessagesRequest) returns (stream NewMessageEvent);
  rpc Forward(ForwardRequest) returns (ForwardResponse);
}
```

## How to build
```
docker build -t telegram_grpc .
```

## Run and save the session
```
touch session.session
docker run -e API_ID=... -e API_HASH=... -v `pwd`/session.session:/telegram/session.session -p 50051:50051 -it --rm golovchen/telegram_grpc
```