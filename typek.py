''' thermocouples '''

from bisect import bisect

class Interpolate(object):
    '''given two arrays with the x_array having a standard interval,
    interpolate a result from an input using the slope of the line.
    '''
    def __init__(self, x_interval, x_array, y_array):
        self.x_interval = int(x_interval)
        self.x_array = x_array
        self.y_array = y_array

    def from_x(self, x_value):
        '''find the y result given x'''
        idx = int(x_value//self.x_interval+28) # faster than bisect
        x = x_value % 10

        y1 = self.y_array[idx-1]
        y2 = self.y_array[idx]

        # (rise over run) * x + b; run is always 10
        y = ((y2 - y1) / float(self.x_interval)) * x + y1

        return y

    def from_y(self, y_value):
        ''' find the x result given y'''
        idx = bisect(self.y_array, y_value)
        offset = self.x_array[idx-1]

        y1 = self.y_array[idx-1]
        y2 = self.y_array[idx]
        y = y_value - y1

        # (rise over run) * x + b; rise is always 10
        x = (float(self.x_interval) / (y2 - y1)) * y + offset

        return x

class RangeError(Exception):
    '''tried to interpolate beyond ends of data set'''
    pass

class ThermocoupleMixin(object):
    '''functions generic to all thermocouple types'''
    def __init__(self):
        self.interp = Interpolate(self.degrees_interval, self.degrees, self.millivolts)
        return

    def degs_to_mv(self, degrees):
        ''' converts degrees to voltage of a junction '''
        if not self.min_degrees <= degrees < self.max_degrees:
            raise RangeError('{}mV out of range.'.format(degrees))

        mv = self.interp.from_x(degrees)
        return mv

    def mv_to_degs(self, mv):
        ''' converts junction voltage to degrees '''
        if not self.min_mv <= mv < self.max_mv:
            raise RangeError('{}mV out of range.'.format(mv))

        degrees = self.interp.from_y(mv)
        return degrees

    def temperature(self, reference_temperature, thermocouple_millivolts):
        ''' returns real temperature of the sense junction in degrees
        given the junctions voltage in mV
        and reference temperature in degrees
        '''
        return self.mv_to_degs(self.degs_to_mv(reference_temperature) + thermocouple_millivolts)

class TypeK(ThermocoupleMixin):
    ''' class of constants for a particular thermocouple'''
    scale = 'Celsius'
    degrees_interval = 10
    min_degrees = -270
    max_degrees = 1370
    min_mv = -6.458
    max_mv = 54.818

    # type K decades from https://srdata.nist.gov/its90/download/type_k.tab
    degrees = list(range(min_degrees, max_degrees+degrees_interval, degrees_interval))
    millivolts = [-6.458, -6.441, -6.404, -6.344, -6.262, -6.158, -6.035, -5.891,\
        -5.730, -5.550, -5.354, -5.141, -4.913, -4.669, -4.411, -4.138, -3.852, -3.554,\
        -3.243, -2.920, -2.587, -2.243, -1.889, -1.527, -1.156, -0.778, -0.392, 0.000,\
        0.397, 0.798, 1.203, 1.612, 2.023, 2.436, 2.851, 3.267, 3.682, 4.096, 4.509,\
        4.920, 5.328, 5.735, 6.138, 6.540, 6.941, 7.340, 7.739, 8.138, 8.539, 8.940,\
        9.343, 9.747, 10.153, 10.561, 10.971, 11.382, 11.795, 12.209, 12.624, 13.040,\
        13.457, 13.874, 14.293, 14.713, 15.133, 15.554, 15.975, 16.397, 16.820, 17.243,\
        17.667, 18.091, 18.516, 18.941, 19.366, 19.792, 20.218, 20.644, 21.071, 21.497,\
        21.924, 22.350, 22.776, 23.203, 23.629, 24.055, 24.480, 24.905, 25.330, 25.755,\
        26.179, 26.602, 27.025, 27.447, 27.869, 28.289, 28.710, 29.129, 29.548, 29.965,\
        30.382, 30.798, 31.213, 31.628, 32.041, 32.453, 32.865, 33.275, 33.685, 34.093,\
        34.501, 34.908, 35.313, 35.718, 36.121, 36.524, 36.925, 37.326, 37.725, 38.124,\
        38.522, 38.918, 39.314, 39.708, 40.101, 40.494, 40.885, 41.276, 41.665, 42.053,\
        42.440, 42.826, 43.211, 43.595, 43.978, 44.359, 44.740, 45.119, 45.497, 45.873,\
        46.249, 46.623, 46.995, 47.367, 47.737, 48.105, 48.473, 48.838, 49.202, 49.565,\
        49.926, 50.286, 50.644, 51.000, 51.355, 51.708, 52.060, 52.410, 52.759, 53.106,\
        53.451, 53.795, 54.138, 54.479, 54.819]

def main():
    '''test basic operation, both directions'''
    import matplotlib.pyplot as plt
    tc = TypeK()

    plt.title('degrees to millivolts')
    plt.plot(tc.degrees, tc.millivolts, 'o')

    xdata = range(-270, 1370)
    ydata = [tc.degs_to_mv(x) for x in xdata]

    plt.plot(xdata, ydata)
    plt.show()

    plt.title('millivolts to degrees')
    plt.plot(tc.degrees, tc.millivolts, 'o')

    ydata = range(int(tc.min_mv*1000), int(tc.max_mv*1000))
    ydata = [y/1000 for y in ydata]
    xdata = [tc.mv_to_degs(y) for y in ydata]

    plt.plot(xdata, ydata)
    plt.show()

    try:
        reference_temperature = 20 #degrees c
        junction_voltage = 14 #millivolts
        degrees = tc.temperature(reference_temperature, junction_voltage)
        print('thermocouple temperature is {} {}'.format(degrees, tc.scale))

        junction_voltage = 60
        degrees = tc.temperature(reference_temperature, junction_voltage)

    except RangeError as err:
        print(err)
        
        
if __name__ == "__main__":
    main()
