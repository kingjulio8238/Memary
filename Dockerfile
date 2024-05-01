FROM python:3.10-slim@sha256:330173e29b1d14a58aecf60031d53fbda203886d5306c235d6a65e373ba172a0

# RUN echo "deb http://archive.debian.org/debian stretch main" > /etc/apt/sources.list
# RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -
RUN \
    apt-get update -y;

# RUN curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && echo "deb https://ngrok-agent.s3.amazonaws.com buster main"|tee /etc/apt/sources.list.d/ngrok.list && apt update && apt install ngrok

WORKDIR /brain/src
ADD . /brain/src
# COPY ./docker/nginx-app.conf /etc/nginx/sites-enabled/default

EXPOSE 3000
ARG ENVIRONMENT

# RUN npm install -s --save

ENV PYTHONUSERBASE /venv
ENV PATH="/venv/bin:${PATH}"
RUN ./docker/setup.sh

# RUN cp /brain/src/docker/nginx-app.conf /etc/nginx/sites-enabled/default
CMD ["streamlit"]
