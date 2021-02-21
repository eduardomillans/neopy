import datetime
import re
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, ElementClickInterceptedException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from helpers import get_data_from_json


class Bot:
    def __init__(self, browser):
        try:
            # Create a driver
            if browser == 'chrome':
                self._driver = webdriver.Chrome()
            elif browser == 'edge':
                self._driver = webdriver.Edge()
            elif browser == 'safari':
                self._driver = webdriver.Safari()
            elif browser == 'firefox':
                self._driver = webdriver.Firefox()

            # Create a wait instance to reuse
            self._wait = WebDriverWait(self._driver, 5)  # 5 seconds wait approximately, may vary

            # Variable to save driver error
            self._driver_error = ''

            # Get email and password
            credentials = get_data_from_json('credentials.json')
            self._email = credentials['email']
            self._password = credentials['password']

        except Exception as ex:
            self._driver_error = str(ex).replace('\n', '')
            pass

    def __get_assignments(self):
        try:
            # Find calendar button
            calendar_button = self._wait.until(ec.element_to_be_clickable((By.XPATH, '/html/body/div[3]/header/div[4]/a[1]')))
            calendar_button.click()

            # Find all calendar's item
            calendar_day_elements = self._wait.until(ec.visibility_of_all_elements_located((By.CLASS_NAME, 'editable')))

            # Helper variables
            assignments = []
            now = datetime.datetime.now()
            flag = False

            # Find current calendar element
            for day in calendar_day_elements:
                if f'{now.year},{now.month},{now.day}' in day.get_attribute('data-add-event'):
                    flag = True

                if flag:
                    assignment_elements = day.find_elements(By.CLASS_NAME, 'general_event')
                    for assignment in assignment_elements:
                        _, title, due_date, course_tag, *_ = assignment.get_attribute('onmouseover').replace('\'', '').split(', ')
                        assignments.append({'title': title, 'due_date': due_date, 'course': re.sub(re.compile('<.*?>'), '', course_tag)})

            # Return the assignments
            return assignments

        except TimeoutException:
            raise TimeoutException

        except StaleElementReferenceException:
            raise StaleElementReferenceException

        except ElementClickInterceptedException:
            raise ElementClickInterceptedException

    def __get_notifications(self):
        try:
            # Find notification button
            notification_button = self._wait.until(ec.element_to_be_clickable((By.XPATH, '/html/body/div[3]/header/div[4]/div[2]/a')))
            notification_button.click()

            # Find all elements
            notifications = []
            teacher_elements = self._wait.until(ec.visibility_of_all_elements_located((By.CLASS_NAME, 'ms-user')))
            message_elements = self._wait.until(ec.visibility_of_all_elements_located((By.CLASS_NAME, 'ms-subject')))
            received_date_elements = self._wait.until(ec.visibility_of_all_elements_located((By.CLASS_NAME, 'ms-date')))

            for i in range(len(teacher_elements)):
                notifications.append({
                    'teacher': teacher_elements[i].text,
                    'message': message_elements[i].text,
                    'received_date': received_date_elements[i].text
                })

            # Return the notifications
            return notifications

        except TimeoutException:
            raise TimeoutException

        except StaleElementReferenceException:
            raise StaleElementReferenceException

        except ElementClickInterceptedException:
            raise ElementClickInterceptedException

    def run(self, data_type):
        if self._driver_error != '':
            return {'has_error': True, 'payload': self._driver_error}

        # Open UNID page
        self._driver.get('https://unid.neolms.com/')

        try:
            # Find login button and click it
            self._driver.find_element(By.XPATH, '/html/body/div[2]/header/nav/ol/li[6]/a').click()

            # Find office login button
            office_login_button = self._wait.until(ec.element_to_be_clickable((By.XPATH, '//*[@id="office365_sso_btn"]')))
            office_login_button.click()

            # Find email input and press enter
            email_input = self._wait.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="i0116"]')))
            email_input.send_keys(self._email)
            email_input.send_keys(Keys.ENTER)

            # Validate the email
            try:
                self._wait.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="usernameError"]')))
                return {'has_error': True, 'payload': 'This username may not be correct'}
            except WebDriverException:
                pass

            # Find password input
            password_input = self._wait.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="i0118"]')))
            password_input.send_keys(self._password)

            # Find microsoft office login button
            microsoft_office_login_button = self._wait.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="idSIButton9"]')))
            microsoft_office_login_button.click()

            # Validate the password
            try:
                self._wait.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="passwordError"]')))
                return {'has_error': True, 'payload': 'The account or password is incorrect'}
            except WebDriverException:
                pass

            # Find not keep the session button
            not_keep_session_button = self._wait.until(ec.element_to_be_clickable((By.XPATH, '//*[@id="idBtn_Back"]')))
            not_keep_session_button.click()

            # Close the popup if it exists
            try:
                not_keep_popup_button = self._wait.until(ec.visibility_of_element_located((By.XPATH, '/html/body/div[5]/div/div/div[3]/button[2]')))
                not_keep_popup_button.click()
                sleep(2)  # 2 seconds wait approximately, may vary
            except WebDriverException:
                pass

            # Validate what data we are going to save
            if data_type == 'assignments':
                return {'has_error': False, 'payload': self.__get_assignments()}
            elif data_type == 'notifications':
                return {'has_error': False, 'payload': self.__get_notifications()}
            else:
                notifications = self.__get_notifications()
                assignments = self.__get_assignments()
                return {'has_error': False, 'payload': [assignments, notifications]}

        except TimeoutException:
            return {'has_error': True, 'payload': 'There was not enough time to find the html element.'}

        except StaleElementReferenceException:
            return {'has_error': True, 'payload': 'The element no longer appears on the DOM of the page.'}

        except ElementClickInterceptedException:
            return {'has_error': True, 'payload': 'An html element could not be clicked.'}

        finally:
            self._driver.quit()


if __name__ == '__main__':
    print('You need to run \'main.py\'')
