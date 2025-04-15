FROM node:16-alpine

WORKDIR /app

# Only copy package.json and package-lock.json initially
COPY package*.json ./

# Create node_modules with the right permissions
RUN mkdir -p /app/node_modules && chown node:node /app/node_modules
RUN npm install

# Don't copy the source code - it will be mounted as a volume
# COPY . .

# Fix permissions
RUN chown -R node:node /app

USER node

EXPOSE 3000

# Use react-scripts start for development with hot reloading
CMD ["npm", "start"] 