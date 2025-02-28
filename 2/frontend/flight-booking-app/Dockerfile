FROM node:18-alpine
WORKDIR /app
COPY /home/puneeth/Work/New_codebenders/rest_api_server/2/frontend/flight-booking-app/package*.json ./
RUN npm install
COPY /home/puneeth/Work/New_codebenders/rest_api_server/2/frontend/flight-booking-app . .
EXPOSE 5173
ENV NODE_ENV=production
CMD ["npm", "run", "dev", "--", "--host"]
