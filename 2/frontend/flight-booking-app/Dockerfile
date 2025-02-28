FROM node:18-alpine
WORKDIR /home/puneeth/Work/New_codebenders/rest_api_server/2/frontend/flight-booking-app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]
