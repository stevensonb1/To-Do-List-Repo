WindowHeight = 500
WindowWidth = 700
ExtendedWindowHeight = 650

App = {
    'NameMinimumLength': 0,
    'NameMaximumLength': 15,
}

DisplayErrors = {
    'Login_InvalidPasswordLength': "Password must be more than 8 characters",
    'Login_InvalidUsername': 'This username is already in use',
    'App_InvalidName': 'You already have a {type} named "{name}"',
    'App_InvalidNameLength': '''{name} must be between \n%s-%s characters'''%(App['NameMinimumLength'], App['NameMaximumLength']),
    'App_InvalidTaskInputLength': 'Task must have a name and description',
    'App_InvalidInputRegex': '{name} cannot contain any symbols'
}

BaseFont = "Arial"