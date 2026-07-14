FROM node:24-alpine

WORKDIR /app

COPY package.json package-lock.json ./

RUN npm ci

COPY . .

EXPOSE 5173

CMD ["sh", "/app/scripts/docker-entrypoint.sh"]
