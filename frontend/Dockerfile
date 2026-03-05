FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Build the app
RUN npm run build

# Expose port
EXPOSE 3000

# Start the application with SPA routing support
CMD ["npx", "serve", "-s", "build", "-l", "3000"]
