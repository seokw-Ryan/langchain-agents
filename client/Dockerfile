FROM node:16-alpine

WORKDIR /app

COPY package.json .

# Create node_modules with the right permissions
RUN mkdir -p /app/node_modules && chown node:node /app/node_modules
RUN npm install

COPY . .

# Fix permissions
RUN chown -R node:node /app

USER node

EXPOSE 3000

CMD ["npm", "start"] 