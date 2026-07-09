class MyError(Exception):
    pass

def check_age(age):
    if age < 18:
        raise MyError("Age 18 se kam hai")

# try:
#     check_age(15)
# except MyError as e:
#     print(e)
check_age(4)