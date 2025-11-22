# Use an official Node.js image
FROM node:16

# Set the working directory
WORKDIR /app

# Copy the frontend code
COPY . .

# Install dependencies
RUN npm install

# Build the frontend
RUN npm run build

# Expose the frontend port
EXPOSE 80

# Serve the frontend using a static server
CMD ["npx", "serve", "-s", "build", "-l", "80"]