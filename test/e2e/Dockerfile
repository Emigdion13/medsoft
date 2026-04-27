FROM mcr.microsoft.com/playwright:v1.40.0

WORKDIR /app/test/e2e

# Copy all test files at once
COPY . .

# Install dependencies
RUN npm install

# Create results directory for HTML report
RUN mkdir -p test-results/html

CMD ["npm", "run", "test"]
