import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import HomeScreen from './Screens/HomeScreen';
import DetectScreen from './Screens/DetectScreen';
import AnalyticsScreen from './Screens/AnalyticsScreen';

// Import icons for your tabs (you may need to install @expo/vector-icons or a similar package)
import { MaterialIcons } from 'react-native-vector-icons';

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

const HomeStack = () => {
    return (
        <Stack.Navigator initialRouteName="Home">
            <Stack.Screen
                name="Home"
                component={HomeScreen}
                options={{
                    // headerShown: false,
                    headerStyle: {
                        backgroundColor: 'black',
                    },
                    headerTitleStyle: {
                        color: 'white',
                        fontFamily: 'Poppins-Regular',
                    },
                }}
            />
        </Stack.Navigator>
    );
}

const DetectStack = () => {
    return (
        <Stack.Navigator>
            <Stack.Screen
                name="Detect"
                component={DetectScreen}
                options={{
                    // headerShown: false,
                    headerStyle: {
                        backgroundColor: 'black',
                    },
                    headerTitleStyle: {
                        color: 'white',
                        fontFamily: 'Poppins-Regular',
                    },
                }}
            />
        </Stack.Navigator>
    );
}

const AnalyticsStack = () => {
    return (
        <Stack.Navigator>
            <Stack.Screen
                name="Analytics"
                component={AnalyticsScreen}
                options={{
                    // headerShown: false,
                    headerStyle: {
                        backgroundColor: 'black',
                    },
                    headerTitleStyle: {
                        color: 'white',
                        fontFamily: 'Poppins-Regular',
                    },
                }}
            />
        </Stack.Navigator>
    );
}

const AppNavigator = () => {
    return (
        <NavigationContainer>
            <Tab.Navigator
                screenOptions={{
                    // title: '',
                    headerStyle: { backgroundColor: 'black' },
                    tabBarStyle: { backgroundColor: 'black', borderTopWidth: 0.5 },
                }}
            >
                <Tab.Screen
                    name="HomeTab"
                    component={HomeStack}
                    options={{
                        tabBarIcon: ({ color, size }) => (
                            <MaterialIcons name="home" size={size} color={color} />
                        ),
                        headerShown: false,
                        title: 'Home'
                    }}
                />
                <Tab.Screen
                    name="DetectTab"
                    component={DetectStack}
                    options={{
                        tabBarIcon: ({ color, size }) => (
                            <MaterialIcons name="computer" size={size} color={color} />
                        ),
                        headerShown: false,
                        title: 'Detect'
                    }}
                />
                <Tab.Screen
                    name="AnalyticsTab"
                    component={AnalyticsStack}
                    options={{
                        tabBarIcon: ({ color, size }) => (
                            <MaterialIcons name="analytics" size={size} color={color} />
                        ),
                        headerShown: false,
                        title: 'Analytics'
                    }}
                />
            </Tab.Navigator>
        </NavigationContainer>
    );
};

export default AppNavigator;
