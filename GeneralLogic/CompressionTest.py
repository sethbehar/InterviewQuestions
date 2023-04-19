import json
class CompressionTest:

    def __init__(self, json_file):
        with open(json_file, 'r') as f:
            self.data = json.load(f)
            self.hospital_painter_rate = (31.25, 1)
            self.hospital_laborer_rate = (20.0, 0.5)
            self.shop_laborer_rate = (16.25, 1.25)

    # Take in start data and end data, calculate hours in between...
    def calculate_hours_worked(self, start, end):
        from datetime import datetime

        start_datetime = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
        end_datetime = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")

        seconds = (end_datetime - start_datetime).total_seconds()
        hours = seconds / 3600

        return hours

    # Calculate pay for a specific shift
    # 'multiplier' -> 1 for regular pay, 1.5 for overtime, and 2 for double time
    def get_hourly_rate(self, hours, job_area, job_type, multiplier):
        total_pay = 0
        total_benefits = 0
        if job_area == "Hospital":
            if job_type == "Laborer":
                total_pay += hours * self.hospital_laborer_rate[0] * multiplier
                total_benefits += hours * self.hospital_laborer_rate[1]

            if job_type == "Painter":
                total_pay += hours * self.hospital_painter_rate[0] * multiplier
                total_benefits += hours * self.hospital_painter_rate[1]

        if job_area == "Shop":
            if job_type == "Laborer":
                total_pay += hours * self.shop_laborer_rate[0] * multiplier
                total_benefits += hours * self.shop_laborer_rate[1]

        return (total_pay, total_benefits)

    def get_employee_info(self, data):
        employee_data = {} # result

        # Iterate over each employee
        for entry in data['employeeData']:
            is_regular_time = True
            is_overtime = False
            is_double_time = False
            total_pay = 0
            total_benefits = 0
            total_hours = 0
            # Iterate over each employee's hours
            for period in entry['timePunch']:
                current_job_area = period['job'].split('-')[0].strip() # Hospital or Shop
                current_job_type = period['job'].split('-')[1].strip() # Laborer or Painter
                hours = self.calculate_hours_worked(period['start'], period['end']) # Hours worked during shift
                total_hours += hours

                # Current shift transitions into overtime from regular time
                if total_hours > 40 and is_regular_time:
                    pay_benefits = self.get_hourly_rate(total_hours - 40, current_job_area, current_job_type, 1.5)
                    total_pay += pay_benefits[0]
                    total_benefits += pay_benefits[1]

                    pay_benefits = self.get_hourly_rate(hours - (total_hours - 40), current_job_area, current_job_type, 1)
                    total_pay += pay_benefits[0]
                    total_benefits += pay_benefits[1]

                    is_regular_time = False
                    is_overtime = True

                # Current shift transitions into double time from overtime
                elif total_hours > 48 and is_overtime:
                    pay_benefits = self.get_hourly_rate(total_hours - 48, current_job_area, current_job_type, 2)
                    total_pay += pay_benefits[0]
                    total_benefits += pay_benefits[1]

                    pay_benefits = self.get_hourly_rate(hours - (total_hours - 48), current_job_area, current_job_type,
                                                        1.5)
                    total_pay += pay_benefits[0]
                    total_benefits += pay_benefits[1]

                    is_overtime = False
                    is_double_time = True

                # Regular shift
                elif is_regular_time:
                    pay_benefits = self.get_hourly_rate(hours, current_job_area, current_job_type, 1)
                    total_pay += pay_benefits[0]
                    total_benefits += pay_benefits[1]

                # Overtime shift
                elif is_overtime:
                    pay_benefits = self.get_hourly_rate(hours, current_job_area, current_job_type, 1.5)
                    total_pay += pay_benefits[0]
                    total_benefits += pay_benefits[1]

                # Double time shift
                elif is_double_time:
                    pay_benefits = self.get_hourly_rate(hours, current_job_area, current_job_type, 2)
                    total_pay += pay_benefits[0]
                    total_benefits += pay_benefits[1]


            # Populate new json file as a dictionary...
            employee_data[entry['employee']] = {}
            employee_data[entry['employee']]['employee'] = entry['employee']

            # Now calculate regular, overtime, and double time hours...
            regular = 0.0
            overtime = 0.0
            double_time = 0.0
            if total_hours > 40 and total_hours < 48:
                overtime = total_hours - 40
                regular = 40.0
            elif total_hours > 48:
                double_time = total_hours - 48
                overtime = 8.0
                regular = 40.0
            else:
                regular = total_hours

            # Add rest of attributes
            employee_data[entry['employee']]['regular'] = regular.__round__(4)
            employee_data[entry['employee']]['overtime'] = overtime.__round__(4)
            employee_data[entry['employee']]['doubletime'] = double_time.__round__(4)
            employee_data[entry['employee']]['wageTotal'] = total_pay.__round__(4)
            employee_data[entry['employee']]['benefitTotal'] = total_benefits.__round__(4)

        return employee_data

    # Retrieve json file from 'get_employee_info'
    def start(self):
        employee_data = self.get_employee_info(self.data)
        for employee, info in employee_data.items():
            print(employee)
            for key, value in info.items():
                print("  ", key, ":", value)
            print()







if __name__ == '__main__':
    eb = CompressionTest('data.json')
    eb.start()