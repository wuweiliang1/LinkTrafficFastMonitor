import CheckFlow
import time
import Utils.Alert


class Link:
    def __init__(self, name, speed, mgmt_ip, community, ifindex, threshold_in, threshold_out, description, mib_interval,
                 multiplier,
                 loosetimes):
        self.name = name
        self.cir = speed
        self.mgmt_ip = mgmt_ip
        self.community = community
        self.ifIndex = ifindex
        self.threshold_in = threshold_in
        self.threshold_out = threshold_out
        self.description = description
        self.multiplier = multiplier
        self.update_interval = float(mib_interval) * int(self.multiplier)
        self.loosetimes = int(loosetimes)
        self.maximum_dampening = self.loosetimes * 3
        self.warning_count_in = 0
        self.warning_count_out = 0
        self.last_record_time = None
        self.warning_timestamp_in = 0
        self.warning_timestamp_out = 0
        self.record_in = CircleArray()
        self.record_out = CircleArray()
        self.curr_speed_in = 0
        self.curr_speed_out = 0

    def update_record(self, engine):
        start_timestamp_in = time.time()
        self.record_in.insert(
            (CheckFlow.get_snmp_data(self.mgmt_ip, self.ifIndex, self.community, 'in', engine), start_timestamp_in))
        start_timestamp_out = time.time()
        self.record_out.insert(
            (CheckFlow.get_snmp_data(self.mgmt_ip, self.ifIndex, self.community, 'out', engine), start_timestamp_out))

    def check_speed(self):
        if self.warning_count_out <= self.maximum_dampening and self.calculate_speed('in') >= int(self.threshold_in):
            self.warning_count_in += 1
        elif self.warning_count_in != 0:
            self.warning_count_in -= 1
        if self.warning_count_out <= self.maximum_dampening and self.calculate_speed('out') >= int(self.threshold_out):
            self.warning_count_out += 1
        elif self.warning_count_out != 0:
            self.warning_count_out -= 1
        if self.warning_count_in >= self.loosetimes:
            if time.time() - self.warning_timestamp_in > 90:
                self.send_notification('in')
                self.warning_timestamp_in = time.time()
        if self.warning_count_out >= self.loosetimes:
            if time.time() - self.warning_timestamp_out > 90:
                self.send_notification('out')
                self.warning_timestamp_out = time.time()
        self.curr_speed_in = int(self.calculate_speed('in'))
        self.curr_speed_out = int(self.calculate_speed('out'))
        return True

    def calculate_speed(self, direction):
        if direction == 'in':
            return self.record_in.get_delta() * 8 / (self.update_interval * 1000 * 1000)
        elif direction == 'out':
            return self.record_out.get_delta() * 8 / (self.update_interval * 1000 * 1000)

    def send_notification(self, direction):
        # For the open source version, you have to complete the code of sending notification on your own.
        if direction == 'in':
            Utils.Alert.send_notification(self.mgmt_ip,
                                          '%s(%s)inbound traffic has exceeded threshold for more then %s seconds(%sMbps/%sMbps). Current calculated traffic speed is %sMbps.' % (
                                              self.name, self.description, int(self.update_interval) * self.loosetimes,
                                              self.threshold_in,
                                              self.cir, self.curr_speed_in))
        elif direction == 'out':
            Utils.Alert.send_notification(self.mgmt_ip,
                                          '%s(%s)outbound traffic has exceeded threshold for more then %s seconds(%sMbps/%sMbps). Current calculated traffic speed is %sMbps.' % (
                                              self.name, self.description, int(self.update_interval) * self.loosetimes,
                                              self.threshold_out,
                                              self.cir, self.curr_speed_out))


class CircleArray:
    def __init__(self, size=3):
        self.internal_array = []
        self.counter = 0
        self.array_size = size

    def insert(self, data):
        if len(self.internal_array) < self.array_size:
            self.internal_array.append(data)
            self.counter += 1
        elif len(self.internal_array) == self.array_size:
            self.internal_array[self.counter % self.array_size] = data
            self.counter += 1
        elif len(self.internal_array) > self.array_size:
            exit('buffer exceeded!')

    def get_delta(self):
        if len(self.internal_array) <= 1:
            return 0
        else:
            return self.internal_array[(self.counter - 1) % self.array_size][0] - self.internal_array[
                (self.counter - 2) % self.array_size][0]

            # def get_interval(self):
            #     if len(self.internal_array) <= 1:
            #         return 9999
            #     else:
            #         return self.internal_array[(self.counter - 1) % self.array_size][1] - self.internal_array[
            #             (self.counter - 2) % self.array_size][1]
