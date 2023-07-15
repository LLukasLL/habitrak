# HABITRAK
#### Video Demo: https://youtu.be/3YuTMnoHEMQ
#### Description: Simple Habit Tracker Web app like the Finance Problem Set. You can add tasks to your board and click a checkbox if you accomplished that tasks on this day. The app automatically creates the task board. It creates rows for every day between your start date and today. You can change the start date manually. You can also add and remove tasks, which are displayed as columns. By clicking submit you can send your changes to the server. The thing basically works like a simple bullet journal. It's aim is to improve your mental health.
#### Intro Code explanation: The app uses the login and register structure from the finance problem set. If you register, there will also be a registration date set into the user-table in the database. This date will be used as start date for the habit-table and can be changed manually.
#### Functions: Several functions have been added to automate the sql stuff. The idea was to make the code shorter. I think most of them are used only one time, so this is not exactly a big thing. Another function creates a python dictionary. This dictionary serves as a datatype to store information about every checkbox. A very important part about this ist that every checkbox has an id. This id gets written into the value of the html-chekbox.
#### /habits GET: at the start the code gets all relevant information from the database and builds some lists with date information and lists with all the task-ids and task-names of the user. It then builds a nested list (like a table). The columns represent the tasks. The first element of every row contains the date, every subsequent one holds the information about the checkbox element. This table is then used by the /habits template to build the checkbox-table by using two nested jinja-for-loops. The task-names-list fills the names-row by another jinja-for-loop. 
#### /habits POST: At first the code checks if tasks get added or removed. If you want to remove a task you have to type in the correct task name. It then calls the corresponding functions which do the sql-stuff(add/remove the row from the tasks table and remove all rows of the task_entries table of the task). Then it checks if a new start date has been submitted. If the date is valid it modifies the corresponding entry in the user-database. In the end it checks which checkboxes are checked when the users clicks submit (it gets a list of all the values of the checked checkboxes => these are the ids of the checkboxes as explained before) and modifies the task_entry database to hold only the checked entries. (the bool value in the db is therefore not neded. I was too lazy to remove it, since it doesn't crash my code...) 
#### /journal: SADLY STILL TO DO: The idea is to use the existing infrastructure to build a table with journal entries. 
#### Additional comments: Most challenging for me was to completely plan a whole project. While this project is simpler than the finance project, i had to work much harder to make the code elegant and functioning. I also made many wrong design choices, the end result was far simpler than some previous stuff.