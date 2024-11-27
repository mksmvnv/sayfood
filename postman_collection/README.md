## Postman collection for testing API

The `sayfood.postman_collection.json` file contains a postman collection - a set of pre-prepared queries for testing API operation.

## Preparing a Django project to run the collection

1. Make sure the virtual environment is deployed and activated, and the project dependencies are installed.
2. To test the API locally, in the `settings.py` settings, connect SQLite3 as a database
and set `DEBUG = True`.
3. Run migrations; create at least 2 ingredients and 3 tags in the database.
4. Start the development web server.

*After preparing the project, create a copy of the `db.sqlite3` database file:
it may come in handy in case of a failure.*

## Uploading the collection to Postman:

1. Launch Postman.
2. In the upper left corner, click `File` -> `Import`.
3. A pop-up window will prompt you to drag and drop a file with the collection into it or select a file using the file manager window.
Upload the `sayfood.postman_collection.json` file to Postman.

## Running a collection

1. After completing the previous steps, an imported collection will appear in the left part of the Postman window in the `Collections` tab.
Hover over it, click on the three dots opposite the collection name and select `Run collection` from the drop-down list. A list of collection requests will appear in the center of the screen,
and a menu for configuring the launch parameters will appear on the right side of the screen.
2. In the right menu, enable the `Persist responses for a session` function - this will allow you to view API responses after running the collection.
3. Click the `Run <collection name>` button.
4. The center of the screen will display the result of running the collection and tests. Failed tests can be filtered by going to the `Failed` tab.
View the details of the executed request and the received response: to do this, click on the test.

## Restarting a collection

1. Go to the `postman_collection` directory in the root of the project.
2. With the project's virtual environment activated, run the script to clear the database of objects created when executing collection queries: `bash clear_db.sh`.

When the script is executed, all users and objects created during the previous collection run will be deleted (provided that the `on_delete` parameters are correctly configured in the project models).

If the database clearing fails, use the backup copy of the `db.sqlite3` file: replace the current database file with this copy.

You can also create a new database and fill it with the objects necessary for the correct launch of the collection (as described in p.3 of the section *Preparing a Django project to launch a collection*).

## Limitations from Postman developers

The free version of Postman has a technical limitation: a collection can be freely launched 25 times a month.
Once this limit is reached, Postman will not turn into a pumpkin: it will still launch collections, but the launch will sometimes be blocked for 30 seconds (sometimes twice in a row), and during this time the program interface will offer to purchase a paid version.
You can buy a paid version, or you can just continue using the free version, interrupted from time to time by watching ads.

There are no restrictions for sending individual requests.
