import datetime

import requests

# api-endpoint
token = "4ca5339a-7da4-46f9-81d1-076d4f681762"
api = "http://scheduling-interview-2021-265534043.us-west-2.elb.amazonaws.com/api"

if __name__ == '__main__':

    # endpoints to use for the api calls
    start_string = api + "/Scheduling/Start?token=" + token
    schedule_string = api + "/Scheduling/Schedule?token=" + token
    stop_string = api + "/Scheduling/Stop?token=" + token
    appointment_string = api + "/Scheduling/AppointmentRequest?token=" + token

    print("Doctor Appointment Scheduler")
    done = False

    data = []
    request_list = []

    # loop while the program is running
    while not done:
        print("Press 1 to start the system")
        print("Press 2 to retrieve the schedule")
        print("Press 3 to request an appointment")
        print("Press 4 to schedule the appointments")
        print("Press 5 to exit and show the schedule")
        val = input("Enter value: ")

        # reset the schedule
        if val == '1':
            r = requests.post(url=start_string)
            if r.status_code == 200:
                print("Successfully reset the system")
            else:
                print("Error resetting the schedule")

        # retrieve the schedule
        elif val == '2':
            r = requests.get(url=schedule_string)
            if r.status_code == 200:
                data = r.json()
                print("Successfully retrieved the schedule")
            else:
                print("Error retrieving the schedule")

        # receive an appointment request
        elif val == '3':
            r = requests.get(url=appointment_string)
            if r.status_code == 200:
                request_val = r.json()
                request_list.append(request_val)
                print("Successfully retrieved an appointment request")
            elif r.status_code == 204:
                print("No more appointment requests available")
            else:
                print("Error retrieving an appointment request")

        # schedule an appointment for each request
        elif val == '4':

            i = 1

            # loop through each request
            for val in request_list:

                isNew = val['isNew']
                day_list = val['preferredDays']
                doctor_list = val['preferredDocs']
                personId = val['personId']
                appointment = 0
                doctor_id = 0

                # iterate through each appointment and add the ones that exist for that person
                current_appointments = []
                if not isNew:
                    for appt in data:
                        if appt['personId'] == personId:
                            current_appointments.append(appt)

                # check validity for each preferred day
                for day in day_list:
                    date = day.replace('Z', '')
                    date = datetime.datetime.fromisoformat(date)

                    # check that the day isn't too close to an existing appointment
                    too_close = False
                    for appt in current_appointments:
                        appt_date = appt['appointmentTime']
                        appt_date = appt_date.replace('Z', '')
                        appt_date = datetime.datetime.fromisoformat(appt_date)
                        diff = appt_date - date
                        diff = abs(diff)
                        if diff.days < 6:
                            too_close = True
                            break

                    # skip day if too close
                    if too_close:
                        continue

                    # loop through each doctor in preferred doctors
                    for doctor in doctor_list:
                        hours = []

                        # add times that doctor is busy on the specific day we're looking at
                        for value in data:
                            if value['doctorId'] == doctor:
                                d = value['appointmentTime'].replace('Z', '')
                                d = datetime.datetime.fromisoformat(d)
                                if d.date() == date.date():
                                    hours.append(d.hour)

                        # find an available time for new patient
                        if isNew:
                            for j in range(15, 16):
                                if j not in hours:
                                    appointment = date.replace(hour=j)
                                    appointment = datetime.datetime.isoformat(appointment)
                                    doctor_id = doctor
                                    break

                        # find an available time for existing patient
                        else:
                            for j in range(8, 16):
                                if j not in hours:
                                    appointment = date.replace(hour=j)
                                    appointment = datetime.datetime.isoformat(appointment)
                                    doctor_id = doctor
                                    break

                        if appointment != 0:
                            break

                    if appointment != 0:
                        break

                # make parameters to send in request
                PARAMS = {
                    "doctorId": doctor_id,
                    "personId": val['personId'],
                    "appointmentTime": appointment,
                    "isNewPatientAppointment": val['isNew'],
                    "requestId": val['requestId']
                }

                headers = {
                    'Content-type': 'application/json',
                    'Accept': 'application/json'
                }

                r = requests.post(url=schedule_string, json=PARAMS, headers=headers)
                response = r.status_code

                if response == 200:
                    print("Successfully scheduled appointment " + str(i))

                    # add successful appointment to existing schedule
                    new_data = {
                        'doctorId': doctor_id,
                        'personId': personId,
                        'appointmentTime': appointment,
                        'isNewPatientAppointment': isNew
                    }
                    data.append(new_data)

                else:
                    print("Error scheduling appointment" + str(i))
                i = i + 1

            request_list = []

        # exist loop and display all data
        elif val == '5':
            r = requests.post(url=stop_string)
            response = r.json()
            for value in response:
                print(value)
            print(str(len(response)) + " total appointments")
            done = True
