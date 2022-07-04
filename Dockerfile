FROM ubuntu@sha256:62b95dd050572873dbe140d8c5ced653a02f08512585489ed8d7a6ef6ef7a727

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Ho_Chi_Minh
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install --no-install-recommends -y python3 python3-dev python3-pip build-essential git && \
	apt-get clean && rm -rf /var/lib/apt/lists/* && \
	useradd --create-home ops
USER ops

WORKDIR /app
ADD requirement.txt .
RUN pip3 install -U -r requirement.txt
ADD main.py .

CMD ["python3", "main.py"]

