import React, { useState, useEffect, useRef, useCallback } from 'react';
import { View, Text, ScrollView, Dimensions, StyleSheet } from 'react-native';
import { LineChart } from 'react-native-chart-kit';
import axiosInstance from '../Components/axiosInstance';
import { useIsFocused } from '@react-navigation/native';

const screenWidth = Dimensions.get("window").width;

const AnalyticsScreen = () => {
    // const productList = ['bottle', 'tissue', 'cup', 'chair', 'person', 'bowl'];
    const [productList, setProductList] = useState([]);
    const [groupedData, setGroupedData] = useState({});
    const isFetchingData = useRef(false);
    const isScrolling = useRef(false); // Add this ref to track scrolling
    const isFocused = useIsFocused();

    const fetchAllProducts = async () => {
        try {
            const response = await axiosInstance.get(`/get_all_products`);
            setProductList(response.data.all_products);
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    };

    const fetchData = async () => {
        if (isFetchingData.current || isScrolling.current) {
            // If data fetching or scrolling is already in progress, return early
            return;
        }
        isFetchingData.current = true;

        for (let i = 0; i < productList.length; i++) {
            try {
                const response = await axiosInstance.get(
                    `/generate_graph?product_codename=${productList[i]}`
                );
                const responseData = response.data;
                // console.log('responseData', response.data)
                console.log('UseEffect hook in "Analytics Screen" is currently running~')

                // Update the existing data in groupedData or add new data
                setGroupedData((prevGroupedData) => ({
                    ...prevGroupedData,
                    [productList[i]]: {
                        Date_created: responseData.map((item) => item.Date_created),
                        Product_count: responseData.map((item) => item.Product_count),
                    },
                }));
            } catch (error) {
                console.error(`Error fetching data for ${productList[i]}`);
            }
        }

        isFetchingData.current = false;
    };

    const fetchDataAndProducts = async () => {
        try {
            console.log('Interval started');
            await fetchAllProducts();
            await fetchData();
            console.log('Fetching done!')
        } catch (error) {
            console.error('Error fetching data or products:', error);
        }
    };

    useEffect(() => {
        let intervalId;

        // const fetchDataAndProducts = async () => {
        //     try {
        //         // Set up a timer to fetch data every 30 seconds
        //         intervalId = setInterval(fetchDataAndProducts, 30000);
        //         console.log('Interval started');

        //         // First, wait for fetchAllProducts() to complete and return
        //         await fetchAllProducts();

        //         // Now, fetch data
        //         await fetchData();


        //     } catch (error) {
        //         console.error('Error fetching data or products:', error);
        //     }
        // };

        if (isFocused) {
            fetchDataAndProducts();
            intervalId = setInterval(fetchDataAndProducts, 5000);
            console.log('Interval started');
        }

        // Cleanup: Stop the timer when the component unmounts or loses focus
        return () => {
            if (intervalId) {
                clearInterval(intervalId);
                console.log('Cleared interval');
            }
        };
    }, [isFocused]);

    // useEffect(() => {
    //     let intervalId;

    //     if (isFocused) {
    //         // Start fetching data initially
    //         // fetchAllProducts();
    //         fetchData();

    //         // Set up a timer to fetch data every 30 seconds
    //         intervalId = setInterval(fetchData, 30000);
    //         console.log('Interval started');
    //     }

    //     // Cleanup: Stop the timer when the component unmounts or loses focus
    //     return () => {
    //         if (intervalId) {
    //             clearInterval(intervalId);
    //             console.log('Cleared interval');
    //         }
    //     };
    //     // if (isFocused) {
    //     //     // Start fetching data initially
    //     //     fetchData();

    //     //     // Set up a timer to fetch data every 30 seconds
    //     //     intervalId = setInterval(fetchData, 30000);
    //     // }

    //     // // Cleanup: Stop the timer when the component unmounts or loses focus
    //     // return () => {
    //     //     if (intervalId) {
    //     //         clearInterval(intervalId);
    //     //         console.log('Cleared interval of Analytics Screen!');
    //     //     }
    //     // };
    // }, [isFocused]);

    // Handle scroll events
    const handleScroll = () => {
        // Set isScrolling to true when scrolling starts
        isScrolling.current = true;

        // Set a timeout to reset isScrolling after a short delay (e.g., 100ms)
        setTimeout(() => {
            isScrolling.current = false;
        }, 100);
    };

    const LineChartExample = ({ Date_created, Product_count }) => {
        // Slice Date_created to keep only the last 5 elements
        const latestDate_created = Date_created.slice(-10);
        // const latestDate_created = Date_created;
        // Slice Product_count to match the length of latestDate_created
        const latestProduct_count = Product_count.slice(-10);
        // const latestProduct_count = Product_count;
        // const yLabels = ["0", "2", "4", "6", "8", "10"]

        // console.log('LATEST DATE CREATED:', Date_created.slice(-4))
        // console.log('LATEST PRODUCT COUNT:', Product_count.slice(-4))

        const max = Math.max(...latestProduct_count)
        const data = {
            labels: latestDate_created,
            datasets: [
                {
                    data: latestProduct_count,
                    color: (opacity = 1) => `rgba(0, 0, 255, ${opacity})`,
                    strokeWidth: 2,
                },
                {
                    data: [0], // min
                    withDots: false
                },
                // {
                //     data: max,
                //     withDots: false
                // }
            ],
        };

        // console.log('DATA:', data)

        // const chartConfig = {
        //     backgroundGradientFrom: 'blue', // Dark background color
        //     backgroundGradientTo: 'black', // Dark background color
        //     color: (opacity = 1) => `rgba(255, 255, 255, ${opacity})`, // Label and legend color (white)
        //     labelColor: (opacity = 1) => `rgba(255, 255, 255, ${opacity})`, // Label color (white)
        //     propsForDots: {
        //         r: 6, // Dot radius
        //         strokeWidth: '1',
        //         stroke: '#ffffff', // Dot border color
        //     },
        // };

        const customDecorator = (x, y, value) => {
            return (
                <View key={value} style={{ position: 'absolute', left: x, top: y - 20 }}>
                    <Text style={{ color: 'black', fontSize: 12 }}>{value}</Text>
                </View>
            );
        };

        chartConfig = {
            // backgroundColor: "yellow",
            // labelCount: 30,
            backgroundGradientFrom: "#000024",
            backgroundGradientTo: "#000024",
            // fillShadowGradientFrom: "white",
            // fillShadowGradientTo: "white",
            decimalPlaces: 2, // optional, defaults to 2dp
            color: (opacity = 1) => `rgba(255, 255, 255, ${opacity})`,
            labelColor: (opacity = 1) => `rgba(255, 255, 255, ${opacity})`,
            style: {
                borderRadius: 16
            },
            propsForDots: {
                r: "6",
                strokeWidth: "1.5",
                stroke: "white"
            },
            propsForLabels: {
                fontFamily: "Poppins-Regular",
                fontSize: 12,
                width: 50, // Set a fixed width for y-axis labels
                textAlign: 'right', // Align the labels to the right
                paddingRight: 5, // Add some padding to the right of the labels
            },
            decorator: customDecorator
        }

        // const axisLabelStyle = {
        //     fontFamily: 'Poppins-Regular', // Replace 'YourCustomFont' with your actual custom font family
        //     fontSize: 12, // Adjust the font size as needed
        //     fontWeight: 'normal', // Adjust the font weight as needed
        //     color: 'white', // Adjust the label color as needed
        // };

        return (
            <ScrollView horizontal={true} onScroll={handleScroll}>
                <View>
                    <LineChart
                        // onDataPointClick={()=>{console.log(data)}} 
                        data={data}
                        width={1800} // Width of the chart
                        height={220} // Height of the chart
                        // width={600} // Width of the chart
                        // height={650} // Height of the chart
                        chartConfig={chartConfig}
                        withInnerLines={true}
                        withOuterLines={true}
                        // verticalLabelRotation={90}
                        yAxisSuffix=""
                        color='black'
                        // yAxisInterval={max}
                        segments={4}
                    // yLabelsOffset={5}
                    // yAxisLabelStyle={axisLabelStyle} // Apply custom style to Y-axis labels
                    // xAxisLabelStyle={axisLabelStyle}
                    // style={{
                    //     marginVertical: 5,
                    // }}
                    // renderDotContent={({ x, y, index }) => (
                    //     // You can customize the dots here if needed
                    //     <View
                    //         key={index}
                    //         style={{
                    //             position: 'absolute',
                    //             left: x - 10,
                    //             top: y - 10,
                    //             width: 10,
                    //             height: 10,
                    //             borderRadius: 5,
                    //             backgroundColor: 'blue',
                    //         }}
                    //     />
                    // )}
                    />
                </View>
            </ScrollView>
        );
    };

    return (
        <ScrollView style={styles.main} onScroll={handleScroll}>
            {productList.map((product, index) => {
                const data = groupedData[product];
                if (!data) {
                    // Data not available yet
                    return null;
                }
                const { Date_created, Product_count } = data;

                return (
                    <View key={product}>
                        <Text style={styles.label}>{product}</Text>
                        <LineChartExample
                            key={index}
                            product={product}
                            Date_created={Date_created}
                            Product_count={Product_count}
                        />
                    </View>
                );
            })}
        </ScrollView>
    );
};

const styles = StyleSheet.create({
    main: {
        flex: 1,
        backgroundColor: 'black',
        padding: 16
        // paddingTop: 100,
        // paddingBottom: 16,
        // paddingLeft: 16,
        // paddingRight: 16
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
        borderWidth: 1,
    },
    label: {
        fontSize: 30,
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
        // borderColor: 'black',
        // borderWidth: 1,
        width: '100%',
        padding: 30
    }
});

export default AnalyticsScreen;

// import React, { useState, useEffect, useRef, useCallback } from 'react';
// import { View, Text, ScrollView, Dimensions, StyleSheet } from 'react-native';
// import { LineChart } from 'react-native-chart-kit';
// import axiosInstance from '../Components/axiosInstance';

// const screenWidth = Dimensions.get("window").width;

// const GraphScreen = () => {
//     const productList = ['bottle', 'tissue', 'cup', 'chair', 'person', 'bowl'];

//     const [groupedData, setGroupedData] = useState({});
//     const isFetchingData = useRef(false);

//     const fetchData = async () => {
//         if (isFetchingData.current) {
//             // If data fetching is already in progress, return early
//             return;
//         }
//         isFetchingData.current = true;

//         for (let i = 0; i < productList.length; i++) {
//             try {
//                 const response = await axiosInstance.get(
//                     `/generate_graph?product_codename=${productList[i]}`
//                 );
//                 const responseData = response.data;
//                 // console.log('responseData', response.data)
//                 console.log('USEEFECTTTTTTTTTTTTTTTTTTTTTT TRIGGERED!')

//                 // Update the existing data in groupedData or add new data
//                 setGroupedData((prevGroupedData) => ({
//                     ...prevGroupedData,
//                     [productList[i]]: {
//                         Date_created: responseData.map((item) => item.Date_created),
//                         Product_count: responseData.map((item) => item.Product_count),
//                     },
//                 }));
//             } catch (error) {
//                 console.error(`Error fetching data for ${productList[i]}`);
//             }
//         }

//         isFetchingData.current = false;
//     };


//     useEffect(() => {
//         // Fetch data initially
//         fetchData();

//         // Set up a timer to fetch data every 15 seconds
//         const intervalId = setInterval(() => {
//             fetchData();
//         }, 45000);

//         // Clean up the timer when the component unmounts
//         return () => clearInterval(intervalId);
//     }, []);


//     // useEffect(() => {
//     //     const fetchData = async () => {
//     //         for (let i = 0; i < productList.length; i++) {
//     //             try {
//     //                 const response = await axiosInstance.get(
//     //                     `/generate_graph?product_codename=${productList[i]}`
//     //                 );
//     //                 const responseData = response.data;
//     //                 console.log('responseData', response.data)

//     //                 // Update the existing data in groupedData or add new data
//     //                 setGroupedData((prevGroupedData) => ({
//     //                     ...prevGroupedData,
//     //                     [productList[i]]: {
//     //                         Date_created: responseData.map((item) => item.Date_created),
//     //                         Product_count: responseData.map((item) => item.Product_count),
//     //                     },
//     //                 }));
//     //             } catch (error) {
//     //                 console.error(`Error fetching data for ${productList[i]}`);
//     //             }
//     //         }
//     //     };

//     //     // Fetch data initially
//     //     fetchData();

//     //     // Set up a timer to fetch data every 15 seconds
//     //     const intervalId = setInterval(fetchData, 15000);

//     //     // Clean up the timer when the component unmounts
//     //     return () => clearInterval(intervalId);
//     // }, []);

//     // Handle scroll events
//     const handleScroll = () => {
//         if (!isFetchingData.current) {
//             // Fetch data only if data fetching is not in progress
//             fetchData();
//         }
//     };

//     const LineChartExample = ({ Date_created, Product_count }) => {
//         // Slice Date_created to keep only the last 5 elements
//         // const latestDate_created = Date_created.slice(-4);
//         const latestDate_created = Date_created;
//         // Slice Product_count to match the length of latestDate_created
//         // const latestProduct_count = Product_count.slice(-4);
//         const latestProduct_count = Product_count;
//         // const yLabels = ["0", "2", "4", "6", "8", "10"]

//         // console.log('LATEST DATE CREATED:', Date_created.slice(-4))
//         // console.log('LATEST PRODUCT COUNT:', Product_count.slice(-4))

//         const data = {
//             labels: latestDate_created,
//             datasets: [
//                 {
//                     data: latestProduct_count,
//                     color: (opacity = 1) => `rgba(0, 0, 255, ${opacity})`,
//                     strokeWidth: 2,
//                 },
//                 {
//                     data: [0], // min
//                     withDots: false
//                 },
//                 // {
//                 //     data: Math.max(latestProduct_count),
//                 //     withDots: false
//                 // }
//             ],
//         };

//         // console.log('DATA:', data)

//         // const chartConfig = {
//         //     backgroundGradientFrom: 'blue', // Dark background color
//         //     backgroundGradientTo: 'black', // Dark background color
//         //     color: (opacity = 1) => `rgba(255, 255, 255, ${opacity})`, // Label and legend color (white)
//         //     labelColor: (opacity = 1) => `rgba(255, 255, 255, ${opacity})`, // Label color (white)
//         //     propsForDots: {
//         //         r: 6, // Dot radius
//         //         strokeWidth: '1',
//         //         stroke: '#ffffff', // Dot border color
//         //     },
//         // };

//         const customDecorator = (x, y, value) => {
//             return (
//                 <View key={value} style={{ position: 'absolute', left: x, top: y - 20 }}>
//                     <Text style={{ color: 'black', fontSize: 12 }}>{value}</Text>
//                 </View>
//             );
//         };

//         chartConfig = {
//             // backgroundColor: "yellow",
//             // labelCount: 30,
//             backgroundGradientFrom: "black",
//             backgroundGradientTo: "blue",
//             fillShadowGradientFrom: "white",
//             fillShadowGradientTo: "white",
//             decimalPlaces: 2, // optional, defaults to 2dp
//             color: (opacity = 1) => `rgba(255, 255, 255, ${opacity})`,
//             labelColor: (opacity = 1) => `rgba(255, 255, 255, ${opacity})`,
//             style: {
//                 borderRadius: 16
//             },
//             propsForDots: {
//                 r: "6",
//                 strokeWidth: "1.5",
//                 stroke: "white"
//             },
//             propsForLabels: {
//                 fontFamily: 'Poppins-Regular',
//                 fontSize: 12
//             },
//             decorator: customDecorator
//         }

//         // const axisLabelStyle = {
//         //     fontFamily: 'Poppins-Regular', // Replace 'YourCustomFont' with your actual custom font family
//         //     fontSize: 12, // Adjust the font size as needed
//         //     fontWeight: 'normal', // Adjust the font weight as needed
//         //     color: 'white', // Adjust the label color as needed
//         // };

//         return (
//             <ScrollView horizontal={true} onScroll={handleScroll}>
//                 <View>
//                     <LineChart
//                         data={data}
//                         width={1800} // Width of the chart
//                         height={220} // Height of the chart
//                         chartConfig={chartConfig}
//                         withInnerLines={true}
//                         withOuterLines={true}
//                         // verticalLabelRotation={90}
//                         yAxisSuffix=""
//                         color='black'
//                         // yAxisInterval={1}
//                         segments={4}
//                     // yLabelsOffset={5}
//                     // yAxisLabelStyle={axisLabelStyle} // Apply custom style to Y-axis labels
//                     // xAxisLabelStyle={axisLabelStyle}
//                     // style={{
//                     //     marginVertical: 5,
//                     // }}
//                     // renderDotContent={({ x, y, index }) => (
//                     //     // You can customize the dots here if needed
//                     //     <View
//                     //         key={index}
//                     //         style={{
//                     //             position: 'absolute',
//                     //             left: x - 10,
//                     //             top: y - 10,
//                     //             width: 10,
//                     //             height: 10,
//                     //             borderRadius: 5,
//                     //             backgroundColor: 'blue',
//                     //         }}
//                     //     />
//                     // )}
//                     />
//                 </View>
//             </ScrollView>
//         );
//     };

//     return (
//         <ScrollView style={styles.main} onScroll={handleScroll}>
//             {productList.map((product, index) => {
//                 const data = groupedData[product];
//                 if (!data) {
//                     // Data not available yet
//                     return null;
//                 }
//                 const { Date_created, Product_count } = data;

//                 return (
//                     <View key={product}>
//                         <Text style={styles.label}>{product}</Text>
//                         <LineChartExample
//                             key={index}
//                             product={product}
//                             Date_created={Date_created}
//                             Product_count={Product_count}
//                         />
//                     </View>
//                 );
//             })}
//         </ScrollView>
//     );
// };

// const styles = StyleSheet.create({
//     main: {
//         flex: 1,
//         backgroundColor: 'black',
//         padding: 16,
//     },
//     container: {
//         flex: 1,
//         padding: 16,
//         backgroundColor: 'black',
//         color: '#FFFFFF',
//         justifyContent: 'center',
//         alignItems: 'center',
//         borderColor: '#ccc',
//         borderRadius: 5,
//         borderWidth: 1
//     },
//     label: {
//         fontSize: 30,
//         fontFamily: 'Poppins-Bold',
//         color: '#FFFFFF'
//     },
//     input: {
//         borderWidth: 1,
//         borderColor: '#ccc',
//         borderRadius: 5,
//         padding: 10,
//         marginBottom: 15,
//         color: "#FFFFFF",
//         fontFamily: 'Poppins-Regular',
//     },
//     validator: {
//         borderRadius: 5,
//         padding: 10,
//         marginBottom: 15,
//         color: "#FFFFFF",
//         fontFamily: 'Poppins-Regular',
//     },
//     toggleContainer: {
//         marginTop: 8,
//         marginBottom: 16,
//         width: 60,
//         height: 30,
//         borderRadius: 25,
//         padding: 5,
//     },
//     toggleCircle: {
//         width: 24,
//         height: 24,
//         borderRadius: 12,
//     },
//     button: {
//         marginTop: 32,
//         backgroundColor: '#007AFF',
//     },
//     checker: {
//         flex: 1,
//         // borderColor: 'black',
//         // borderWidth: 1,
//         width: '100%',
//         padding: 30
//     }
// });

// export default GraphScreen;

