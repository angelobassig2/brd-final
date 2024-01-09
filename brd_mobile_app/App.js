import React, { useState, useEffect } from 'react';
import AppNavigator from './AppNavigator';
import * as Font from 'expo-font';

const App = () => {
  const [fontLoaded, setFontLoaded] = useState(false)

  useEffect(() => {
    Font.loadAsync({
      'Poppins-Regular': require('./assets/fonts/Poppins-Regular.ttf'),
      'Poppins-Bold': require('./assets/fonts/Poppins-Bold.ttf'),
    })
      .then(() => {
        setFontLoaded(true)
      })
  }, [])
  
  if (!fontLoaded) return null

  return (
    <AppNavigator />
  );
};

export default App;