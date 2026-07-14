FROM node:24-alpine

WORKDIR /app

COPY package.json package-lock.json ./

RUN npm ci

COPY . .

EXPOSE 5173

CMD ["sh", "-c", "sed -i 's/\\r$//' /app/scripts/docker-entrypoint.sh && exec sh /app/scripts/docker-entrypoint.sh"]
