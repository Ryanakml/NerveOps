# M0-01: build from the image context root in later issues (#3 owns Compose).
FROM node:20-alpine AS base
WORKDIR /app
COPY apps/control-plane/package.json ./
RUN npm install --omit=dev
COPY apps/control-plane ./
RUN npm run build
EXPOSE 3001
CMD ["npm", "start"]
