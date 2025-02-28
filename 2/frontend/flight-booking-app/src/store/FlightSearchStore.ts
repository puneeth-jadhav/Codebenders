import { create } from 'zustand';
import { FlightSearchForm, TravelType, TravelDetails, TravelersDetails, SpecialFare } from '../types/FlightTypes';

interface FlightSearchState extends FlightSearchForm {
  setTravelType: (type: TravelType) => void;
  addTrip: (trip: TravelDetails) => void;
  removeTrip: (index: number) => void;
  updateTrip: (index: number, trip: Partial<TravelDetails>) => void;
  setTravelers: (travelers: TravelersDetails) => void;
  toggleSpecialFare: (fareId: number) => void;
  resetSearch: () => void;
}

const initialState: FlightSearchForm = {
  travelType: 'one-way',
  trips: [{ from: '', to: '', departureDate: new Date() }],
  travelers: {
    adults: 1,
    children: 0,
    infants: 0,
    travelClass: 'Economy'
  },
  specialFares: [
    { id: 1, type: 'Student', description: 'Special fares for students', isSelected: false },
    { id: 2, type: 'Senior Citizen', description: 'Discounts for seniors', isSelected: false }
  ]
};

export const useFlightSearchStore = create<FlightSearchState>((set) => ({
  ...initialState,
  
  setTravelType: (type) => set({ travelType: type }),
  
  addTrip: (trip) => set((state) => ({
    trips: [...state.trips, trip]
  })),
  
  removeTrip: (index) => set((state) => ({
    trips: state.trips.filter((_, i) => i !== index)
  })),
  
  updateTrip: (index, trip) => set((state) => ({
    trips: state.trips.map((t, i) => i === index ? { ...t, ...trip } : t)
  })),
  
  setTravelers: (travelers) => set({ travelers }),
  
  toggleSpecialFare: (fareId) => set((state) => ({
    specialFares: state.specialFares.map(fare => 
      fare.id === fareId ? { ...fare, isSelected: !fare.isSelected } : fare
    )
  })),
  
  resetSearch: () => set(initialState)
}));