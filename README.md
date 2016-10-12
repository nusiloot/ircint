#IRCINT 
##A tool for IRC Intelligence and logging

> so far it will only put all messages and links into the database
>
> the database is searchable with sql

Usage:

1. Create a database

2. Edit the settings.py with your settings

3. run 'python ircint.py'

4. ???

5. Profit!

The ircint.db database will contain all messages from the specified channels,
privmessages, and will filter out all links (starting with http or https) from
the irc into a seperate table


*Update 12.10.2016*
> * wrapped base functionality in classes
>
> * Added Threading
>
> * Edited settings syntax to support multiple server connections
>
> TODO: Inferface and searching the db






*written by robre 29.9.2016*
