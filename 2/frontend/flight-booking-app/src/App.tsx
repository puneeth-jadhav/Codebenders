import React from 'react';
import { CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import { FlightSearchForm } from './components/FlightSearchForm';

const theme = createTheme({
  palette: {
    primary: {
      main: '#FF6B00', // Orange theme as specified
    },
  },
  typography: {
    fontFamily: 'Roboto, sans-serif',
  },
});

const App: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <FlightSearchForm />
    </ThemeProvider>
  );
};

export default App;