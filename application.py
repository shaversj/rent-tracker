import datetime
import re
from config import service_account_key_file, google_sheet_key
import gspread
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from oauth2client.service_account import ServiceAccountCredentials


application = Flask(__name__)


scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    service_account_key_file, scope)

gc = gspread.authorize(credentials)

wks = gc.open_by_key(google_sheet_key)
worksheet = wks.worksheet('rent_sheet')


@application.route('/')
def main():

    # Get the message that was sent from Twilio
    body = request.values.get('Body', None)
    body = str(body).lower()

    # Extract numbers from body
    amountRegex = re.compile(r'\d+')

    # Start our TwiML response
    response = MessagingResponse()

    if 'payment' in body:
        amount = amountRegex.search(body)
        amount = float(amount.group(0))
        answer = apply_payment_amount(amount)
        response.message(answer)

        return str(response)

    elif 'add rent' in body:
        amount = amountRegex.search(body)
        amount = float(amount.group(0))
        answer = add_rent_to_balance(amount)
        response.message(answer)

        return str(response)

    elif 'balance' in body:
        answer = retrieve_balance()
        response.message(answer)

        return str(response)

    else:
        response.message(
            'Enter "{amount} payment" to apply payment to account.\nEnter "Balance" to retrieve the account balance.\nEnter "Add rent {amount}" to increase balance of the account.')

        return str(response)


@application.route('/applyPayment/<amount>')
def apply_payment_amount(amount: int):
    """Apply payment"""

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

        return f'The payment of ${amount:.2f} was successfully applied to the account.'


@application.route('/addRent/<amount>')
def add_rent_to_balance(amount: float):
    """Add rent to the balance of the account"""

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
        return f'${amount:.2f} was added to the balance of the account.'


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


if __name__ == "__main__":
    application.run()
