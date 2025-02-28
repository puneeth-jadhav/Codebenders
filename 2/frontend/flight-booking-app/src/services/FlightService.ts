import axios from 'axios';
import { TravelDetails, TravelersDetails } from '../types/FlightTypes';

const BASE_URL = 'http://50.16.209.202:8000';

export const FlightService = {
  async searchFlights(
    trips: TravelDetails[], 
    travelers: TravelersDetails
  ) {
    try {
      const response = await axios.get(`${BASE_URL}/flights`, {
        params: {
          departure_city: trips[0].from,
          arrival_city: trips[0].to,
          departure_date: trips[0].departureDate.toISOString(),
          return_date: trips[0].returnDate?.toISOString(),
          adults: travelers.adults,
          children: travelers.children,
          infants: travelers.infants,
          travel_class: travelers.travelClass
        }
      });
      return response.data;
    } catch (error) {
      console.error('Flight search error:', error);
      throw error;
    }
  },

  async getAvailableFares() {
    try {
      const response = await axios.get(`${BASE_URL}/fares`);
      return response.data;
    } catch (error) {
      console.error('Fares fetch error:', error);
      throw error;
    }
  }
};