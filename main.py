from bot import Bot
from helpers import *
from validators import EmailValidator, PasswordValidator


def get_data_update_response(data_type):
    data = get_data_from_json(f'{data_type}.json')
    if len(data) > 0:
        return get_answers({
            'type': 'confirm',
            'name': 'update',
            'message': f'You have previously saved {data_type}, do you want to update them?',
            'default': True
        })
    else:
        return True


def get_browser_response():
    return get_answers({
        'type': 'list',
        'name': 'browser',
        'message': 'What browser do you want to use?',
        'choices': ['Firefox', 'Chrome', 'Edge', 'Safari'],
        'filter': lambda value: value.lower()
    })


def pre_show_table(data_type, data):
    if data_type == 'assignments':
        header = ['Title', 'Due Date', 'Course']
    else:
        header = ['Teacher', 'Message', 'Received Date']

    show_table(header, data, data_type)


def show_data():
    selected_option = get_answers({
        'type': 'list',
        'name': 'show',
        'message': 'What do you want to show?',
        'choices': ['Show assignments', 'Show notifications', 'Show both'],
        'filter': lambda value: value.split(' ')[1]
    })

    if selected_option == 'assignments' or selected_option == 'notifications':
        update_response = get_data_update_response(selected_option)

        if update_response:
            browser = get_browser_response()
            neo_bot = Bot(browser)
            response = neo_bot.run(selected_option)

            if response['has_error']:
                print(f'\n{response["payload"]}')
                return
            else:
                print(f'\nThe data was saved in \'{selected_option}.json\'')
                save_data_to_json(f'{selected_option}.json', response['payload'])
                pre_show_table(selected_option, response['payload'])
        else:
            pre_show_table(selected_option, get_data_from_json(f'{selected_option}.json'))
    else:
        assignments_response = get_data_update_response('assignments')
        notifications_response = get_data_update_response('notifications')

        if not assignments_response and not notifications_response:
            pre_show_table('assignments', get_data_from_json('assignments.json'))
            pre_show_table('notifications', get_data_from_json('notifications.json'))
            return

        browser = get_browser_response()
        neo_bot = Bot(browser)

        if assignments_response and not notifications_response:
            update_response = 'assignments'
            response = neo_bot.run('assignments')
        elif not assignments_response and notifications_response:
            update_response = 'notifications'
            response = neo_bot.run('notifications')
        else:
            update_response = 'both'
            response = neo_bot.run(selected_option)

        if response['has_error']:
            print(f'\n{response["payload"]}')
            return
        else:
            if update_response == 'both':
                assignments, notifications = response['payload']
                save_data_to_json('assignments.json', assignments)
                save_data_to_json('notifications.json', notifications)
                print('\nThe data was saved in \'assignments.json\' and \'notifications.json\'')
                pre_show_table('assignments', assignments)
                pre_show_table('notifications', notifications)
                return

            data = response['payload']
            save_data_to_json(f'{update_response}.json', data)
            print(f'\nThe data was saved in \'{update_response}.json\'')
            pre_show_table(update_response, data)

            if update_response == 'assignments':
                pre_show_table('notifications', get_data_from_json('notifications.json'))
            else:
                pre_show_table('assignments', get_data_from_json('assignments.json'))


def update_credentials(default_email=''):
    email, password = get_answers([
        {
            'type': 'input',
            'name': 'email',
            'message': 'Please enter your email',
            'default': default_email,
            'validate': EmailValidator
        },
        {
            'type': 'password',
            'name': 'password',
            'message': 'Please enter your password',
            'validate': PasswordValidator
        }
    ])

    save_data_to_json('credentials.json', {'email': email, 'password': password})


def main():
    while True:
        clear_screen()

        credentials = get_data_from_json('credentials.json')
        if len(credentials) == 0:
            update_credentials()

        selected_option = get_answers({
            'type': 'list',
            'name': 'menu',
            'message': 'What operation do you want to perform?',
            'choices': ['Show assignments/notifications', 'Update credentials', 'Exit'],
            'filter': lambda value: value.lower().split(' ')[0]
        })

        if selected_option == 'show':
            show_data()
            return
        elif selected_option == 'update':
            update_credentials(credentials['email'])
        else:
            return


if __name__ == '__main__':
    main()
