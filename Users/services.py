def validate_phone_number(model, phone_number):  
    while True:
        if len(phone_number) == 10 and phone_number.isdigit():
            if model.objects.filter(phone_number=phone_number).exists():
                print('\033[1;91m' + 'Error: Phone number already exists.' + '\033[0m')
            else:
                return phone_number
        else:
            print('\033[1;91m' + 'Error: Phone number must be 10 digits.' + '\033[0m')
            phone_number = input('Phone Number: ')

def create_admin_profile(model, user, phone_number):
    model.objects.create(
            user = user,
            phone_number = phone_number,
            designation = 'Staff Member',
            department = 'Admin'
        )