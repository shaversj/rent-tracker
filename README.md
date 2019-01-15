# rent-tracker

Rent-Tracker is a service that records and tracks the rent that I receive for my property each month. I rent one of my homes to a family member (never do it!), so he feels that he can pay me when/how he wants. Often times, I will get my rent at a family gathering, via Paypal, or in an envelope under my doormat. Tracking the amount he pays each month is challenging, so I needed a solution that makes it easy to record the payment as soon as I receive it.

## Script Overview
The app uses Twilio and Google Sheets to record a payment and check the account balance through SMS.

![google_sheet](gsheet.png)

## Example Usage

If I texted my Twilio number: **I received a $725 payment**

* The application would update the google spreadsheet with the date, description and amount and respond stating the update was made successfully.

If I texted the Twilio number: **Check balance**

* The application would respond with the following: **As of 1/1/2019, the account has a balance of $1,450.00**


## Built With

* [Gspread](https://github.com/burnash/gspread) - Google Spreadsheets Python API
* [Twilio](https://www.twilio.com) - Gives you the ability to send/receive SMS messages to your application.
* [Flask](http://flask.pocoo.org) - Flask is a micro web framework