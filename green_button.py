import sys, datetime
from bs4 import BeautifulSoup

class Reading(object):
    """ Reading object, contains cost, value and date"""


    def __init__(self, date_string, cost, value):
        """ Date String should be passed as POSIX

        - Cost is in thousands of a cent 2691 = .02691 cents
        - Value is Energy used Watt hours.  so 897 = .897 kwh
        """
        try:
            self.cost = int(cost)
            self.value = int(value)
        except ValueError as e:
            print "Couldn't parse cost:%s or value:%s, %s" % (cost, value, e.message)

        try:
            self.date = datetime.datetime.utcfromtimestamp(float(date_string))
        except Exception, e:
            print "Couldn't parse date: %s" % e.message

    def is_weekday(self):
        if self.date.isoweekday() in [6, 7]:
            return False
        else:
            return True

class GreenButton(object):
    """Green Button object which has the full list of reaings for an address"""

    def __init__(self, reading_list):
        self.reading_list = reading_list

    """ Get all readings for a Given day of the week and start time"""
    def get_by_day_and_time(self, dow, start_time):
        readings = []
        for reading in self.reading_list:
            if reading.date.isoweekday() != dow:
                continue
            elif reading.date.hour != start_time:
                continue
            else:
                readings.append(reading)

        return readings


    def calculate_averages(self, reading_list):
        """ For a list of readings calculate the averages for Total Paid, cost, value

        This is used to pass in a list of readings from the same day of week
        and time to show average cost for this time period.

        Value returned is tuple that contains averages of

        1) Total Paid (divide by 100000000 to get real dollar value)
        2) Cost (divide by 100000 for cents)
        3) Value (divide by 1000 for KWH)
        
        """
        
        r_cnt = 0
        real_cost, tot_cost, tot_value = 0, 0, 0
        
        for reading in reading_list:
            r_cnt += 1

            tot_cost += reading.cost
            tot_value += reading.value
            real_cost += (reading.value * reading.cost)
            print "reading %s, value: %s, cost: %s" % (r_cnt, reading.value, reading.cost)

        print "Total cost for %s readings: %s" % (r_cnt, real_cost)

        return (real_cost / r_cnt, tot_cost / r_cnt, tot_value / r_cnt)

    def compare_prices(self, date):
        """  For a given start time check how much you would save per KWH over
        The next few hours

        """
        print "Checking prices for %s" % date
        cost_comparison = {}
        now_averages = self.calculate_averages(self.get_by_day_and_time(date.isoweekday(), date.hour))
        for i in range(1,4):
            next_date = date + datetime.timedelta(hours=i)
            next_avgs = self.calculate_averages(self.get_by_day_and_time(next_date.isoweekday(),
                                                                         next_date.hour))
            save_per_kwh = (now_averages[1] * 1000) - (next_avgs[1] * 1000)
            cost_comparison["%s:00" % next_date.hour] = save_per_kwh

        return cost_comparison
    
            
    

def parse_readings(file_name):
    """ Parse xml file to get a list of all the readings """

    print "Going to parse: %s" % file_name
    soup = BeautifulSoup()
    try:
        print "trying this shit out"
        full_file = open(file_name, 'r')
        soup = BeautifulSoup(full_file)
        full_file.close()
    except (IOError, OSError) as iErr:
        print "Couln't open file: %s, %s" % (file_name, iErr.message)

    readings = soup.find_all('intervalreading')

    reading_list = []
    for reading in readings:
        #print "reading"
        cost = reading.find('cost').string
        value = reading.find('value').string
        start = reading.find('timeperiod').find('start').string

        try:
            
            reading = Reading(start, cost, value)
            reading_list.append(reading)
        except Exception, e:
            print "Exception creating Reading object"

    return reading_list


def main():
    file_name = "C:\\Documents and Settings\\Jason\\Desktop\\temp.xml"
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    readings = parse_readings(file_name)
    
    now = datetime.datetime.utcnow()
    gb = GreenButton(readings)
    readings_for_nows_timeperiod = gb.get_by_day_and_time(now.isoweekday(),
                                                          now.hour)
    avgs = gb.calculate_averages(readings_for_nows_timeperiod)
    cost_comparison = gb.compare_prices(now)
    
    print """
        It is currently: %s,

        The average cost to you for this time period is: %s
        Your average usage is: %s

        Average total price for the hour is : %s
        """ % (now, avgs[1], avgs[2], float(float(avgs[0]) / 100000000))

    for k, v in cost_comparison.items():
        print "If you wait until %s: You will save %s per KWH" % (k, float(v)/100000000)   

    print "\n All done..."
    
if __name__ == "__main__":
     main()
