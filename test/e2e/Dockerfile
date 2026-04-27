FROM mcr.microsoft.com/playwright:v1.59.1-jammy

WORKDIR /app

# Install Playwright browser dependencies
RUN npx playwright install-deps chromium

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

CMD ["npx", "playwright", "test", "--reporter=html"]
