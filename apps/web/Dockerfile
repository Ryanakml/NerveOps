# M0-01: build from the image context root in later issues (#3 owns Compose).
FROM node:20-alpine AS base
WORKDIR /app
COPY apps/web/package.json ./
RUN npm install --omit=dev
COPY apps/web ./
RUN npm run build
EXPOSE 3100
CMD ["npm", "start"]
