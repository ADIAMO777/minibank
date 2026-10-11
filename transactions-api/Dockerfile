FROM node:20-alpine

ENV NODE_ENV=production
WORKDIR /app

# Install dependencies in their own layer (cached until package.json changes).
COPY package.json .
RUN npm install --omit=dev && npm cache clean --force

COPY server.js .

# The official node image ships a non-root "node" user.
USER node

EXPOSE 3000
CMD ["node", "server.js"]