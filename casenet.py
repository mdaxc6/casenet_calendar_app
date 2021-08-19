import pandas as pd
from pandas import Timestamp
import time
import os.path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# CHROME DRIVER
chromedriver_location = "chrome_driver/chromedriver"

# FUNCTIONS
# slices a list at a defined 'step' interval
def slice_per(source, step):
    return [source[i::step] for i in range(step)]

def get_info():
    start_date = input('Start Date(MM/DD/YYYY): ')
    end_date = input('End Date(MM/DD/YYYY): ')
    # get a list of dates in the range specified
    datelist = pd.date_range(start_date, end_date).tolist()
    # convert the dates to the desired format mm/dd/yyyy for casenet
    for i in range(len(datelist)):
        datelist[i] = datetime.strftime(datelist[i], '%m/%d/%Y')
    return datelist

def authenticate():
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/calendar']

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)

# FORM INPUT AND SUBMIT
def page_nav_df_create():
    # DATAFRAME
    main_df = pd.DataFrame({
        "date" : [],
        "case_num" : [],
        "case_style" : [],
        "time": [],
        "days": [],
        "event": [],
        "location": [],
        "judge": []
    })

    # XPATHS
    # Paths to each required search element in the field. 
    district_drop_down = '//*[@id="courtId"]'
    date_field = '//*[@id="inputVO.startDate"]'
    #seven_day_search_radio = '//*[@id="sevenDayRadio"]'
    search_by_attorney_radio = '//*[@id="searchAttorneyRadio"]'
    mobar_input = '//*[@id="inputVO.mobarNumber"]'
    submit_button = '//*[@id="findButton"]'

    # PAGE NAVIGATION
    # create an instance of the webdriver and load the inital calendar search page
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging']) #disables logging in console
    driver = webdriver.Chrome(executable_path=chromedriver_location, options=options)

    driver.get('https://www.courts.mo.gov/casenet/cases/calendarSearch.do')
    # 7 day search results
    #driver.find_element_by_xpath(seven_day_search_radio).click()
    # search by attorney
    driver.find_element_by_xpath(search_by_attorney_radio).click()
    # MOBAR number field 
    driver.find_element_by_xpath(mobar_input).send_keys(input("Enter MOBAR number: "))

    datelist = get_info()

    for date in datelist:
        # clear the date text box
        driver.find_element_by_xpath(date_field).clear()
        # store the district dropdown in an object using Select
        courtDistrictDrp = Select(driver.find_element_by_xpath(district_drop_down))
        courtDistrictDrp.select_by_value("CT11") # 11th District Saint Charles
        # date
        driver.find_element_by_xpath(date_field).send_keys(date)
        # without the pause, the inputs are too fast for casenet to handle
        time.sleep(1) 
        # submit 
        driver.find_element_by_xpath(submit_button).click()

        if len(driver.find_elements_by_xpath('//*[contains(text(), "Your query returned no matches to be viewed at this site.")]')) > 0:
            continue
        
        # INFO GATHERING
        i=1
        data = []
        raw_text = []
        # get current date
        current_date = driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr[2]/td/table/tbody/tr[1]/td/table/tbody/tr[1]/td[2]').text
        # collect information from the table
        while driver.find_elements_by_xpath(f'//td[@class="td{i}"]'):
            data.append(driver.find_elements_by_xpath(f'//td[@class="td{i}"]'))
            i += 1
        # parse text into a list
        for d in data:
            for i in d:
                raw_text.append(i.text)       
        # slices the data into lists of each feild 
        organized_data = slice_per(raw_text, 9)

        # create data frame to hold the data
        df = pd.DataFrame({
            "date" : current_date,
            "case_num" : organized_data[0],
            "case_style" : organized_data[1],
            "time": organized_data[2],
            "days": organized_data[3],
            "event": organized_data[5],
            "location": organized_data[7],
            "judge": organized_data[8]
        })
        # add collected data to main dataframe
        main_df = pd.concat([df, main_df], axis=0, join='inner')
        main_df.drop_duplicates(inplace=True)
        main_df.reset_index(drop=True, inplace=True)
        # go back to previous page
        driver.back()

    driver.close()
    return main_df

def check_existing_events(service):
    # Check for existing events
    existing_events = []
    now = datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=30, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    # if events exists, add their summary to the existing events list
    if not events:
        print('No upcoming events found.')
    for event in events:
        existing_events.append(event['summary'])
    return existing_events

        

def handle_events(service, main_df):

    # EVENT HANDLING

    existing_events = check_existing_events(service)

    for i in range(len(main_df)):
        
        event = {
            'summary': main_df['case_style'][i],
            'description': f'Case #: {main_df["case_num"][i]} \nEvent: {main_df["event"][i]} \n{main_df["judge"][i]} \n{main_df["location"][i]} \nDays: {main_df["days"][i]}',
            'start': {
                'dateTime': Timestamp.isoformat(pd.to_datetime(main_df['date'][i] + ' ' + main_df['time'][i])),
                'timeZone': 'America/Chicago',
            },
            'end': {
                'dateTime': Timestamp.isoformat(pd.to_datetime(main_df['date'][i] + ' ' + main_df['time'][i])),
                'timeZone': 'America/Chicago',
            },
        }
        
        if event['summary'] in existing_events:
            print('Event already exists.')
            continue
        else :
            print(f'Completed {i + 1} of {len(main_df) }')

        event = service.events().insert(calendarId='primary', body=event).execute()


def main():
    service = authenticate()
    #EMAIL = input('Enter email address: ')

    main_df = page_nav_df_create()
    handle_events(service, main_df)

    print("Sucessfully added events to Calendar.")

if __name__ == '__main__':
    main()