// it22003850/surfapp--frontend/SurfApp--frontend-e324eabe43c305ffac4f3010e13f33c56e3743db/components/ForecastChart.js
import React, { useState, useEffect } from 'react'; // CHANGED: Added useState, useEffect
import { LineChart } from 'react-native-chart-kit';
import { Dimensions, ActivityIndicator, View, Text } from 'react-native'; // CHANGED: Added imports
import { get7DayForecast } from '../data/surfApi'; // CHANGED: Import from the new API file

const ForecastChart = () => {
  const [chartData, setChartData] = useState(null); // CHANGED: State for data
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await get7DayForecast();
        setChartData(data);
      } catch (e) {
        console.error("Failed to load chart data:", e);
        setChartData({ labels: [], datasets: [{ data: [0] }] }); // Set minimal data on failure
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);
  
  if (loading) {
    return (
      <View style={{ height: 220, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="small" color="#007bff" />
        <Text style={{marginTop: 5}}>Loading forecast data...</Text>
      </View>
    );
  }

  if (!chartData || chartData.datasets[0].data.length === 0) {
    return (
      <View style={{ height: 220, justifyContent: 'center', alignItems: 'center' }}>
        <Text>Forecast data not available.</Text>
      </View>
    );
  }

  return (
    <LineChart
      data={chartData}
      width={Dimensions.get('window').width - 20}
      height={220}
      yAxisSuffix="m"
      chartConfig={{
        backgroundColor: '#e26a00',
        backgroundGradientFrom: '#007bff',
        backgroundGradientTo: '#ffa726',
        decimalPlaces: 1,
        color: (opacity = 1) => `rgba(255, 255, 255, ${opacity})`,
        labelColor: (opacity = 1) => `rgba(255, 255, 255, ${opacity})`,
        style: { borderRadius: 16 },
        propsForDots: { r: '6', strokeWidth: '2', stroke: '#ffa726' },
      }}
      bezier
      style={{ marginVertical: 8, borderRadius: 16, alignSelf: 'center' }}
    />
  );
};

export default ForecastChart;