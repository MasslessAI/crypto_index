from cqt.error_msg import error


class ValuationParameters(object):
    def __init__(self, param_dict):
        pass


class ValuationParametersMovingAverage(ValuationParameters):
    def __init__(self, param_dict):
        super(ValuationParametersMovingAverage, self).__init__(param_dict)

        self.type = 'moving_average'

        if 'window_size' in param_dict.keys():
            self.window_size = param_dict['window_size']
        else:
            error('window_size needs to be given when method = moving_average')

        if 'tolerance_up' in param_dict.keys():
            self.tolerance_up = param_dict['tolerance_up']
        else:
            self.tolerance_up = 100

        if 'tolerance_down' in param_dict.keys():
            self.tolerance_down = param_dict['tolerance_down']
        else:
            self.tolerance_down = 1

        if 'calculation_period' in param_dict.keys():
            self.calculation_period = param_dict['calculation_period']
        else:
            self.calculation_period = 1

        if 'damping_factor' in param_dict.keys():
            self.damping_factor = param_dict['damping_factor']
        else:
            self.damping_factor = 1
