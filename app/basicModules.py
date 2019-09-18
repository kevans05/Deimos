import time

def parse_a_database_return_a_list(database_target, whole_database_data, tailboard):
    #create a list for the data to be put into
    list_of_values = []
    #check to see if there is data present in this presenets list
    if len(tailboard[database_target]) > 0:
        db_target = whole_database_data[database_target]
        for split_tailboard_data in tailboard[database_target].split(";"):
            list_of_values.append(db_target.find_one(id=split_tailboard_data))
        return list_of_values
    else:
        return None


def parse_a_database_return_a_list_users(whole_database_data,tailboard):
    list_of_values = []
    if len(tailboard['presentStaff']) > 0:
        present_users = tailboard['presentStaff'].split(";")

        if tailboard['presentStaffConfirmed'] is not None:
            presnet_users_confirmed = tailboard['presentStaffConfirmed'].split(";")
        else:
            presnet_users_confirmed = []

        for user in present_users:
            user_temp = whole_database_data['staff'].find_one(id=user)
            if user in presnet_users_confirmed:
                user_temp.update({'present': True})
            else:
                user_temp.update({'present': False})
            list_of_values.append(user_temp)
        return list_of_values
    else:
        return None
