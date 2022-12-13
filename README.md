# jigsaw-crawler

## Main Features
Given list of individuals in CSV format (as exported from jigsaw search) this script below information for them:
* Start date of first assignment in the current Account.
* End Date of last assignment in the current Account.
* Duration (in Months) in account ( End date - Start Date)

## How the information provided could be useful
The information provided by this script could be used in various ways e.g. :
* Information about account duration could be used as an input for planning rotation of people.
* Information about End Date could be used to track and plan people coming out of account or fix any assignment miss.

## Installing Dependencies:
Get the checkout from the repo and run below command to install dependencies:

```pip install -r requirements.txt```

## Running the Script:
One needs to follow below steps:
* provide input csv: For this one can provide the targeted employees list 