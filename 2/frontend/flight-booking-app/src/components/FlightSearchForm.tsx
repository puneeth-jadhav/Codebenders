import React, { useState } from 'react';
import { 
  Box, 
  Button, 
  Container, 
  FormControl, 
  FormControlLabel, 
  Radio, 
  RadioGroup, 
  TextField, 
  Typography 
} from '@mui/material';
import { useForm, Controller } from 'react-hook-form';
import { useFlightSearchStore } from '../store/FlightSearchStore';
import { FlightService } from '../services/FlightService';

export const FlightSearchForm: React.FC = () => {
  const { 
    travelType, 
    trips, 
    travelers, 
    specialFares, 
    setTravelType, 
    updateTrip, 
    setTravelers,
    toggleSpecialFare 
  } = useFlightSearchStore();

  const { control, handleSubmit, formState: { errors } } = useForm();

  const [multiCityTrips, setMultiCityTrips] = useState(trips);

  const handleSearchFlights = async () => {
    try {
      const flights = await FlightService.searchFlights(trips, travelers);
      console.log('Found Flights:', flights);
      // TODO: Navigate to flight results page
    } catch (error) {
      console.error('Flight search failed', error);
    }
  };

  const renderTripInputs = () => {
    return multiCityTrips.map((trip, index) => (
      <Box key={index} sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <TextField
          label="From"
          variant="outlined"
          value={trip.from}
          onChange={(e) => updateTrip(index, { from: e.target.value })}
          error={!!errors[`from_${index}`]}
        />
        <TextField
          label="To"
          variant="outlined"
          value={trip.to}
          onChange={(e) => updateTrip(index, { to: e.target.value })}
          error={!!errors[`to_${index}`]}
        />
        <TextField
          label="Departure Date"
          type="date"
          InputLabelProps={{ shrink: true }}
          value={trip.departureDate.toISOString().split('T')[0]}
          onChange={(e) => updateTrip(index, { departureDate: new Date(e.target.value) })}
          error={!!errors[`departureDate_${index}`]}
        />
      </Box>
    ));
  };

  return (
    <Container maxWidth="md">
      <Box component="form" onSubmit={handleSubmit(handleSearchFlights)} sx={{ mt: 4 }}>
        <Typography variant="h4" gutterBottom>Flight Search</Typography>
        
        <FormControl component="fieldset" sx={{ mb: 2 }}>
          <RadioGroup 
            row 
            value={travelType} 
            onChange={(e) => setTravelType(e.target.value as 'one-way' | 'round-trip' | 'multi-city')}
          >
            <FormControlLabel value="one-way" control={<Radio />} label="One Way" />
            <FormControlLabel value="round-trip" control={<Radio />} label="Round Trip" />
            <FormControlLabel value="multi-city" control={<Radio />} label="Multi City" />
          </RadioGroup>
        </FormControl>

        {renderTripInputs()}

        {/* Travelers & Class Modal Placeholder */}
        {/* Special Fares Section Placeholder */}

        <Button 
          type="submit" 
          variant="contained" 
          color="primary" 
          fullWidth 
          sx={{ mt: 2 }}
        >
          Search Flights
        </Button>
      </Box>
    </Container>
  );
};