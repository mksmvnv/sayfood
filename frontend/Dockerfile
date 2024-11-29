# build env
FROM node:21.7.1-alpine as build

WORKDIR /app

COPY package*.json ./

RUN npm install -g npm@9.2.0

COPY . .

RUN npm run build

CMD cp -r build result_build
