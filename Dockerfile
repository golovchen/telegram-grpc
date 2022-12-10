FROM python:3.10.6
RUN pip install telethon
RUN pip install grpcio
RUN pip install grpcio-tools
COPY *.py /telegram/
COPY protos.proto /telegram/
WORKDIR /telegram
RUN python -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=. protos.proto
CMD ["python", "server.py"]