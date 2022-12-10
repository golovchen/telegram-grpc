FROM python:3.10.6
RUN pip install telethon
RUN pip install grpcio
RUN pip install grpcio-tools
COPY *.py /telethon/
COPY protos.proto /telethon/
WORKDIR /telethon
CMD ["python", "server.py"]