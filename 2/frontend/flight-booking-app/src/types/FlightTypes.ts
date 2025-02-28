export type TravelType = 'one-way' | 'round-trip' | 'multi-city';

export interface TravelDetails {
  from: string;
  to: string;
  departureDate: Date;
  returnDate?: Date;
}

export interface TravelersDetails {
  adults: number;
  children: number;
  infants: number;
  travelClass: 'Economy' | 'Premium Economy' | 'Business' | 'First Class';
}

export interface SpecialFare {
  id: number;
  type: string;
  description: string;
  isSelected: boolean;
}

export interface FlightSearchForm {
  travelType: TravelType;
  trips: TravelDetails[];
  travelers: TravelersDetails;
  specialFares: SpecialFare[];
}