FROM kettlebell-python-base
MAINTAINER Yaroslav Kholod

LABEL Name=simple-distillation-mgr
LABEL Vendor="Cold Soft" License=MIT
LABEL Version=0.1.0
LABEL INSTALL="docker run --rm --name NAME -d --network="bridge" IMAGE"
LABEL UNINSTALL="docker rm --force NAME"

RUN mkdir /simple_distillation_mgr
WORKDIR /simple_distillation_mgr
COPY simple_distillation_mgr/* /simple_distillation_mgr/

CMD ["python", "/simple_distillation_mgr/simple_distillation_mgr.py"]
