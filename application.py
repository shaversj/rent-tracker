import datetime
from config import service_account_key_file, google_sheet_key
import gspread
from flask import Flask
from oauth2client.service_account import ServiceAccountCredentials


application = Flask(__name__)

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    service_account_key_file, scope)

gc = gspread.authorize(credentials)

wks = gc.open_by_key(google_sheet_key)
worksheet = wks.worksheet('rent_sheet')


# TODO setup cron job to run the apply_rent_due_amount function at the beginning of every month
# TODO setup Twillio connection
# TODO Provide a way to call the apply_payment_amount function with input from the user
# TODO Provide a way to call the retrieve_balance function with input from the user


@application.route('/applyPayment/<amount>')
def apply_payment_amount(amount: float):
    """Apply payment amount to spreadsheet"""

    date_cell, description_cell, payment_received_cell, rent_due_cell = find_empty_cell()

    try:
        worksheet.update_cell(date_cell.row,
                              date_cell.col, '=TODAY()')
        worksheet.update_cell(description_cell.row,
                              description_cell.col, 'Payment Received')
        worksheet.update_cell(payment_received_cell.row,
                              payment_received_cell.col, amount)

    except gspread.exceptions.GSpreadException:
        return 'Your update was not successful. Please try again.'
    else:
        return f'The payment of ${amount} was successfully applied to the spreadsheet.'


@application.route('/applyRent/<amount>')
def apply_rent_due_amount(amount: float):
    """Applies the amount of rent due each month."""

    date_cell, description_cell, payment_received_cell, rent_due_cell = find_empty_cell()

    try:
        worksheet.update_cell(date_cell.row,
                              date_cell.col, '=TODAY()')
        worksheet.update_cell(description_cell.row,
                              description_cell.col, 'Rent Due')
        worksheet.update_cell(rent_due_cell.row,
                              rent_due_cell.col, amount)

    except gspread.exceptions.GSpreadException:
        return 'Your update was not successful. Please try again.'
    else:
        return f'${amount} was added to the balance.'


@application.route('/retrieveBalance')
def retrieve_balance():
    """Retrieve the total amount due."""

    balance = worksheet.cell(39, 5).value
    x = datetime.datetime.now()

    return f'As of {x.strftime("%x")}, the account has a balance of ${balance[1:-1]}'


def find_empty_cell():
    """Find the first empy cell in the date column."""

    for x in range(1, 38):
        if worksheet.cell(x, 1).value == '':
            date_cell = worksheet.cell(x, 1)
            description_cell = worksheet.cell(x, 2)
            payment_received_cell = worksheet.cell(x, 3)
            rent_due_cell = worksheet.cell(x, 4)

            return date_cell, description_cell, payment_received_cell, rent_due_cell

        else:
            continue


# Row is first number and Column is second number
# print(apply_payment_amount(675))
# print(apply_rent_due_amount(790))
# print(retrieve_balance())


if __name__ == "__main__":
    application.run
