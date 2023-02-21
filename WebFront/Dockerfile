FROM node:16.13.0 AS build

ARG PORT=6001

WORKDIR /app

COPY . ./

RUN npm install

RUN npm run build

EXPOSE ${PORT}

CMD HOST=0.0.0.0 PORT=${PORT} npm run dev
