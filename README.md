# powerMeterRead

I wanted a way to download and store 15-minute-interval readings from my power meter, and make them available to me on my local network in a database. 
The end goal was not totally clear but one possible use case would be to integrate this with the power consumption tools available in Home Assistant. 
I may modify this to use a different database storage method to be more friendly with Home Assistant as it is most compatible with SQLLite. 


## Setup and Usage

This is implemented specifically for someone living in Texas. 

In Texas, we have grid providers such as CenterPoint Energy who service the capital infrastructure, while the power is sold to consumers via 3rd-party wholesalers. 

There is a web tool jointly operated by a few of the main power generating companies, designed to give consumers a more unified experience for grabbing and reading data from their smart meters regardless of who their provider is: 

[Smart Meter Texas](https://www.smartmetertexas.com/quickrefguides)

This tool *does* have an API - however, it is meant for use by the electricity wholesalers and not really for end consumers. 

You will find when looking into the API that the signup process is very manual and is clearly meant for wholesale businesses. 

I did not try to sign up. 

Instead, as a consumer, this tool has an option for sending .csv files with 15-minute-interval readings from your meter to an email of your choice. 

It will only send you data on a daily basis, so the data is not even close to near-real-time, but its better than daily resolution data from your wholesaler and since there are so many of those, the availability of your data from them may vary widely depending on who you have. 


### Creating the csv subscription 

Create an account on the SmartMeterTexas site. 

You will need basic info from your power bill like your ESID and/or meter number, and your service address. 

If you have multiple service locations, you can have them all under one account which is nice. 

Once you have your meter set up in your account, you can create the subscription: 
1. Go to Manage Subscriptions 
1. Select Create New Subscription 
1. Select the options you want. In my case I chose "Energy Data 15 Min Interval", Daily, as CSV, via Email, and then my ESID number. 
1. Click Submit and it should send to your account email the following day. It seems to come around 11AM. 

Note that there is an API radio button when setting up a subscription - you cannot use this without going through the aforementioned API enrollment process not intended for consumers. 


### Environment Variables 

I used poetry to manage this python. Install poetry, initialize the repo, and run `poetry install` to get the dependencies on your local machine. 

Currently it just looks for a .env file for the environment variables like your email, the password, the destination database info, and local folders for the CSV files. 

See the `.env-example` file for the variables you will need. 

Define your variables in the file and just name it `.env` and place that in the repo root directory. 

I might enhance this later to use a more robust config file or maybe some kind of key vault. 


### Email 

The program is set up to look for emails from a specified sender that include attachments. The SmartMeterTexas site sends the CSV files from the same account every day so you can define that account as the sender email. 

It is set up to use an email with an IMAP connection, so you will need an account that you can access via IMAP with a stored user/password. 

Yahoo Mail works for this since you can create app credentials for the account which are separate from the main email login. 

Basically, the CSV files will get sent to your email and this program will download all the relevant CSV files to a local directory when it is run. 


### Database 
Currently, this is designed to work with Microsoft SQL Server via pyodbc. 

There's no reason you can't use a different database, since SQL Server is overkill. I'm just most familiar with it. 

The SQL Driver is hard-coded in the DB connect method currently so you will have to change that and possibly the creation of the connect string if you want a different DB. 

The process reads the CSV files and inserts every row regardless of whether or not it has been loaded previously. 

There are two SQL objects to help make the data friendly for usage. 

Run the four scripts in the /src/sql directory. 

First run the two table creation scripts: 

- `tbl_raw_PowerUsage.sql` - this is the RAW table that will recieve the content of the CSVs and is formatted exactly like the CSVs. 
- `tbl_PowerUsage.sql` - this is the merged table managed by `sp_PowerUsageMergeToMain` to remove any duplication of rows from re-running. 


Then run the stored procedure create and the view create. 

The stored procedure `sp_PowerUsageMergeToMain` is referenced in the code - its job is to maintain a second table aside from the "raw" table where every row will get inserted regardless of duplication. 

The PowerUsage table that results is a merged version of the data which ensures that primary keys are able to be maintained. 


The view `v_raw_PowerUsage_Transform` is designed to display only the most recent revision/iteration of each 15-minute-interval reading. 

The Smart Meter Texas CSV files contain a revision date column - theoretically this makes it possible for them to send a revision to a specific date/time reading. The view ensures that you only are seeing the most recent iteration of each reading. 

So the result of this view will show you only one row per date/time combination. 

This view is what you might want to use for any downstream visualization or reporting. 


### Running 
Ensure you have some emails with CSV attachments fitting the from sender variable. 

Run the main.py file and it should begin. 

You can configure this to run on a scheduler or however you want. 

The stored procedure is called in the code so you do not need to separately schedule that. 