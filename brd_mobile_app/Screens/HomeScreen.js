import React, { useEffect, useState } from 'react';
import { View, StyleSheet, Text, TextInput, TouchableOpacity, Switch, Keyboard, KeyboardAvoidingView } from 'react-native';
import axiosInstance from '../Components/axiosInstance';

const HomeScreen = ({ navigation }) => {
    const [timeInterval, setTimeInterval] = useState('');
    const [threshold, setThreshold] = useState('');
    const [isEnabled, setIsEnabled] = useState(false);
    const [timeIntervalValidator, setTimeIntervalValidator] = useState(false);
    const [thresholdValidator, setThresholdValidator] = useState(false);
    const [allProducts, setAllProducts] = useState([]);

    const toggleSwitch = (timeInterval, threshold) => {
        Keyboard.dismiss()
        setIsEnabled((previousState) => !previousState);

        // Run when the Switch is clicked
        if (!isEnabled) {
            // Run when the Switch is turned on
            console.log('Switch is turned ON');
            if (timeInterval === '' || threshold === '') {
                if (timeInterval === '') {
                    setTimeIntervalValidator(true)
                }
                if (threshold === '') {
                    setThresholdValidator(true)
                }
            }
            else {
                detectObjects(timeInterval, threshold)
            }
        } else {
            // Run when the Switch is turned off
            setTimeIntervalValidator(false)
            setThresholdValidator(false)
            console.log('Switch is turned OFF');
            stopWebcam()
        }
    };

    const stopWebcam = async () => {
        const response = await axiosInstance.post(`/stop_webcam`)
    }

    const detectObjects = async (timeInterval, threshold) => {
        const response = await axiosInstance.get(`/detect_objects?timeInterval=${timeInterval}&threshold=${threshold}&allProducts=${allProducts}`)
    }

    const fetchData = async () => {
        try {
            const response = await axiosInstance.get(`/get_all_products`);
            setAllProducts(response.data.all_products);
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    };

    useEffect(() => {
        fetchData()
    }, [])

    return (
        <View style={styles.main}>
            <View style={styles.checker}>
            </View>

            <View style={styles.checker}>
                <Text style={styles.label}>Time Interval:</Text>
                <TextInput
                    style={styles.input}
                    placeholder="Enter the time interval (secs) when the AI will detect objects"
                    placeholderTextColor="white"
                    value={timeInterval}
                    onChangeText={setTimeInterval}
                    keyboardType="numeric"
                    maxLength={5}
                />
                {timeIntervalValidator ? <Text style={styles.validator}>*Please input a Time Interval greater than 0!</Text> : null}
                <Text style={styles.label}>Threshold:</Text>
                <TextInput
                    style={styles.input}
                    placeholder="Enter the number of remaining products when the AI should alert"
                    placeholderTextColor="white"
                    value={threshold}
                    onChangeText={setThreshold}
                    keyboardType="numeric"
                    maxLength={5}
                />
                {thresholdValidator ? <Text style={styles.validator}>*Please input a Threshold greater than or equal to 0!</Text> : null}
                <Text style={styles.label}>Turn on AI:</Text>
                <View style={styles.container}>
                    <Switch
                        value={isEnabled}
                        onValueChange={() => { toggleSwitch(timeInterval, threshold) }}
                        trackColor={{ false: "#ff0000", true: "0000ff" }}
                        thumbColor={isEnabled ? "#00ff00" : "#0000ff"}
                        ios_backgroundColor="#ff0000"
                    />
                </View>
            </View>

            <View style={styles.checker}>
            </View>
        </View>
    );
};

const styles = StyleSheet.create({
    main: {
        flex: 1,
        backgroundColor: 'black',
        padding: 16,
    },
    container: {
        flex: 1,
        padding: 16,
        backgroundColor: 'black',
        color: '#FFFFFF',
        justifyContent: 'center',
        alignItems: 'center',
        borderColor: '#ccc',
        borderRadius: 5,
        borderWidth: 1
    },
    label: {
        fontSize: 24,
        fontFamily: 'Poppins-Bold',
        color: '#FFFFFF'
    },
    input: {
        borderWidth: 1,
        borderColor: '#ccc',
        borderRadius: 5,
        padding: 10,
        marginBottom: 15,
        color: "#FFFFFF",
        fontFamily: 'Poppins-Regular',
    },
    validator: {
        borderRadius: 5,
        padding: 10,
        marginBottom: 15,
        color: "#FFFFFF",
        fontFamily: 'Poppins-Regular',
    },
    toggleContainer: {
        marginTop: 8,
        marginBottom: 16,
        width: 60,
        height: 30,
        borderRadius: 25,
        padding: 5,
    },
    toggleCircle: {
        width: 24,
        height: 24,
        borderRadius: 12,
    },
    button: {
        marginTop: 32,
        backgroundColor: '#007AFF',
    },
    checker: {
        flex: 1,
        width: '100%',
        padding: 30
    }
});


export default HomeScreen;