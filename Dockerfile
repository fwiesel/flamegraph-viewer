FROM python:3 as build

ADD *requirements.txt /build/
RUN mkdir /wheels && cd /build && pip wheel -w /wheels -r requirements.txt -r optional_requirements.txt

FROM python:3-slim
COPY --from=build /wheels /wheels
ADD . /flamegraphviewer
RUN pip install --no-cache-dir --no-index --find-links /wheels -e /flamegraphviewer[hiredis,lz4] && rm -fr /wheels

CMD ["python", "-m", "flamegraphviewer.visualizer"]
