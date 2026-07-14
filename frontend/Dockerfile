FROM node:22-alpine

WORKDIR /app

COPY package.json package-lock.json ./

RUN npm ci

COPY . .
RUN chmod +x /app/scripts/docker-entrypoint.sh

EXPOSE 5173

CMD ["/app/scripts/docker-entrypoint.sh"]
