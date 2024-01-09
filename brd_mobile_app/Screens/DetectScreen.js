import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, StyleSheet, Switch, Image } from 'react-native';
import axiosInstance from '../Components/axiosInstance';
import { useIsFocused } from '@react-navigation/native';

const DetectScreen = () => {
    const [currentImage, setCurrentImage] = useState('');
    const [data, setData] = useState([]);
    const isFocused = useIsFocused();

    const fetchImage = async () => {
        try {
            const response = await axiosInstance.get(`/get_one_image?image_path=current_image.jpg`)
            setCurrentImage(response.data.image_base64)
            console.log('Checker that this fetchImage api is indeed fetching an image on a specified interval')
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    }

    const fetchData = async () => {
        try {
            const response = await axiosInstance.get(`/get_json?json_filename=all_products_count`)
            setData(response.data)
            console.log(response.data)
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    }

    const fetchImageAndData = async () => {
        try {
            await fetchImage();
            await fetchData();
        } catch (error) {
            console.error('Error fetching data or products:', error);
        }
    };


    useEffect(() => {
        let intervalId;

        if (isFocused) {
            fetchImageAndData();
            intervalId = setInterval(fetchImageAndData, 5000);
            console.log('Interval started');
        }

        // Cleanup: Stop the timer when the component unmounts or loses focus
        return () => {
            if (intervalId) {
                clearInterval(intervalId);
                console.log('Cleared interval');
            }
        };
    }, [isFocused]); // Empty dependency array to run the effect only once

    const renderItem = ({ item }) => (
        <View style={styles.listItem}>
            <Text style={styles.productText}>{item.product}</Text>
            <Text
                style={[
                    styles.countText,
                    item.count > item.threshold ? styles.whiteText : null,
                    item.count > 0 && item.count <= item.threshold ? styles.yellowText : null,
                    item.count === 0 ? styles.redText : null,
                ]}
            >
                {item.count}
            </Text>
        </View>
    );

    return (
        <View style={styles.container}>
            {currentImage && <Image source={{ uri: `data:image/jpg;base64,${currentImage}` }} style={styles.image} />}
            <FlatList
                data={data}
                renderItem={renderItem}
                keyExtractor={(item, index) => index.toString()}
            />
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#000',
    },
    topView: {
        padding: 20,
        borderBottomWidth: 1,
        borderBottomColor: '#1C1C1E'
    },
    listItem: {
        height: 100,
        justifyContent: 'center',
        alignItems: 'center',
        borderBottomWidth: 1,
        borderBottomColor: '#1C1C1E',
        paddingHorizontal: 16,
        color: '#FFFFFF'
    },
    listItemText: {
        color: 'white',
        fontFamily: 'Poppins-Regular',
        fontSize: 30,
        padding: 20
    },
    title: {
        color: '#FFFFFF',
        fontFamily: 'Poppins-Bold',
        fontSize: 30,
        padding: 20
    },
    whiteText: {
        fontFamily: 'Poppins-Bold',
        fontSize: 35,
        color: 'white', // Style for count > threshold
    },
    yellowText: {
        fontFamily: 'Poppins-Bold',
        fontSize: 35,
        // padding: 20,
        color: 'yellow', // Style for 0 < count <= threshold
    },
    redText: {
        fontFamily: 'Poppins-Bold',
        fontSize: 35,
        // padding: 20,
        color: 'red', // Style for count = 0
    },
    listItem: {
        flexDirection: 'row', // Display product and count side by side
        justifyContent: 'space-between', // Distribute space between them
        alignItems: 'center', // Align items vertically in the center
        height: 100,
        borderBottomWidth: 1,
        borderBottomColor: '#1C1C1E',
        paddingHorizontal: 16,
        color: '#FFFFFF',
    },
    productText: {
        color: 'white',
        fontFamily: 'Poppins-Bold',
        fontSize: 30,
        paddingLeft: 30
    },
    countText: {
        color: 'white',
        fontFamily: 'Poppins-Bold',
        fontSize: 30,
        paddingRight: 30
    },
    image: {
        width: 495,
        height: 495
    }
});

export default DetectScreen;