AppName = "To-do list"

WindowHeight = 500
WindowWidth = 800
ExtendedWindowHeight = 650

App = {
    # Length of characters
    'NameMinimumLength': 0,
    'NameMaximumLength': 15,

    # Length of characters
    'DescriptionMaximumLength': 50,
}

DisplayErrors = {
    'Login_InvalidPasswordLength': "Password must be more than 8 characters",
    'Login_InvalidUsername': 'This username is already in use',
    'App_InvalidName': 'You already have a {type} named "{msg}"',

    'App_InvalidNameLength': ('''{msg} must be between \n%s-%s characters'''
        %(App['NameMinimumLength'], App['NameMaximumLength'])),

    'App_InvalidDescriptionLength': ('''{msg} cannot exceed %s characters'''
        %(App['DescriptionMaximumLength'])),

    'App_InvalidTaskInput': 'Task name is a required field',
    'App_InvalidInput': '{msg} cannot contain any symbols'
}

BaseFont = "Arial"
