# Stage 1: Build the Vue.js application
FROM node:20-alpine AS build-stage

WORKDIR /app

# Copy package.json and package-lock.json to leverage Docker cache
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application source code
COPY . .

# Build the application. The base path will be set in vite.config.js
RUN npm run build


# Stage 2: Serve the static files with Nginx
FROM nginx:stable-alpine

# Remove the default Nginx configuration file
RUN rm /etc/nginx/conf.d/default.conf

# Copy the built files from the build stage to a specific sub-directory
# This makes it easier to manage multiple applications on the same Nginx server
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Copy our custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf