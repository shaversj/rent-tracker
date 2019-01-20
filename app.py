import datetime
import re
from chalicelib import config
import pygsheets
from chalice import Chalice, Response

app = Chalice(app_name="lambda-rent-tracker")

gc = pygsheets.authorize(service_account_file="chalicelib/creds.json")

wks = gc.open_by_key(config.google_sheet_key)
worksheet = wks.worksheet("title", "rent_sheet")


@app.route("/")
def main():

    request_body = app.current_request.to_dict()
    app.log.error(request_body)

    body_of_request = str(request_body["query_params"]["Body"])
    body = body_of_request.lower()

    # Extract numbers from body
    amountRegex = re.compile(r"\d+")

    if "payment" in body:
        amount = amountRegex.search(body)
        amount = float(amount.group(0))
        answer = apply_payment_amount(amount)

        return Response(body=answer, headers={"Content-Type": "text/plain"})

    elif "balance" in body:
        answer = retrieve_balance()

        return Response(body=answer, headers={"Content-Type": "text/plain"})

    else:

        return Response(
            body='Enter "{amount} payment" to apply payment to account.\nEnter "Balance" to retrieve the account balance.',
            headers={"Content-Type": "text/plain"},
        )


@app.route("/applyPayment/{amount}")
def apply_payment_amount(amount: int):
    """Apply payment"""

    date_cell, description_cell, payment_received_cell, rent_due_cell = find_empty_cell()

    try:
        worksheet.update_value((date_cell.row, date_cell.col), "=TODAY()")
        worksheet.update_value(
            (description_cell.row, description_cell.col), "Payment Received"
        )
        worksheet.update_value(
            (payment_received_cell.row, payment_received_cell.col), amount
        )

    except pygsheets.exceptions.PyGsheetsException:
        return "Your update was not successful. Please try again."
    else:
        return f"The payment of ${amount:.2f} was successfully applied to the account."


@app.route("/addRent/{amount}")
def add_rent_to_balance(amount: float):
    """Add rent to the balance of the account"""

    date_cell, description_cell, payment_received_cell, rent_due_cell = find_empty_cell()

    try:
        worksheet.update_value((date_cell.row, date_cell.col), "=TODAY()")
        worksheet.update_value((description_cell.row, description_cell.col), "Rent Due")
        worksheet.update_value((rent_due_cell.row, rent_due_cell.col), amount)

    except pygsheets.exceptions.PyGsheetsException:
        return "Your update was not successful. Please try again."
    else:
        return f"${amount:.2f} was added to the balance of the account."


@app.route("/retrieveBalance")
def retrieve_balance():
    """Retrieve the total amount due."""

    balance = worksheet.cell((39, 5)).value
    x = datetime.datetime.now()

    return f'As of {x.strftime("%x")}, the account has a balance of ${balance[1:-1]}'


def find_empty_cell():
    """Find the first empy cell in the date column."""

    for x in range(1, 38):
        if worksheet.cell((x, 1)).value == "":
            date_cell = worksheet.cell((x, 1))
            description_cell = worksheet.cell((x, 2))
            payment_received_cell = worksheet.cell((x, 3))
            rent_due_cell = worksheet.cell((x, 4))

            return date_cell, description_cell, payment_received_cell, rent_due_cell

        else:
            continue
