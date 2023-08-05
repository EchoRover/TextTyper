#imports -------


try:
	import sys
	import time
	import random
	import mysql.connector
	from tabulate import tabulate
    
except ImportError as e:
    missing_modules = str(e).split()[-1]
    print(f"Error: The module '{missing_modules}' is missing.\n")
    print("Please install the required modules using the following commands in commandline:\n")
    print("For mysql-connector-python: 'pip install mysql-connector-python'\n")
    print("For tabulate: 'pip install tabulate'\n")
    sys.exit(1)


#globals variables -------
FILE_SEPERATOR = "==="
TIME_WEIGHT = 1
ACCURACY_WEIGHT = 1.8
WORDS_TYPED_WEIGHT = 0.3
PPRINT_ALLOWED = True
SQL_USERNAME = "root"
SQL_HOST = "localhost"
SQL_PASSWORD = "mysql"
CONNECT = None
MYCURSOR = None
DATABASE_NAME = "TypingMasterdb"
TABLE_NAME = "TypingMaster"

LOGONAME = """
╔╦╗┬ ┬┌─┐┬┌┐┌┌─┐  ╔╦╗┌─┐┌─┐┌┬┐┌─┐┬─┐
 ║ └┬┘├─┘│││││ ┬  ║║║├─┤└─┐ │ ├┤ ├┬┘
 ╩  ┴ ┴  ┴┘└┘└─┘  ╩ ╩┴ ┴└─┘ ┴ └─┘┴└─
"""





#sql functions -------



def create_database():
	MYCURSOR.execute(f"create database if not exists {DATABASE_NAME}")

def create_table():
	MYCURSOR=CONNECT.cursor()
	MYCURSOR.execute(f"use {DATABASE_NAME}")
	MYCURSOR.execute(f"create table if not exists {TABLE_NAME}(username varchar(30) primary key, score int, time decimal(4,2), accuracy decimal(4,2), words_typed int)")



def show_table():
    MYCURSOR.execute(f"USE {DATABASE_NAME}")
    MYCURSOR.execute(f"SELECT username, time, accuracy, words_typed, score FROM {TABLE_NAME} ORDER BY score DESC")
    all_rows = MYCURSOR.fetchall()
    if 1==1:
        row = ["Username", "Time Taken", "Accuracy", "Words Typed", "Score"]
        print(tabulate(all_rows, headers=row, tablefmt="grid"))


def search_username_or_add(name):
	MYCURSOR.execute(f"SELECT * FROM {TABLE_NAME} WHERE username = %s", (name,))
	userdata_exists=MYCURSOR.fetchone()
	if userdata_exists:
		pprint(f"Welcome back, {name}", wait=0.1, progressive=0.2)
		pprint("LOADING.....................", wait=0.2, progressive=0.2)
		userdata_list = [userdata_exists]
		row = ["Username", "Time Taken", "Accuracy", "Words Typed", "Score"]

		print(tabulate(userdata_list, headers=row, tablefmt="grid"))
		print("\nPress [Enter] to run the test again or press and enter any key if you want to quit.")

		user_input = input()
		if not user_input:
			pass
		else:
			print("Exiting the program")
			sys.exit()
				
	else:
		add_username(name)

def add_username(username):
	query=(f"insert into {TABLE_NAME}(username) values (%s)")
	nameval=(username,)
	MYCURSOR.execute(query,nameval)
	CONNECT.commit()
	print("Your username has been recorded.")
	
def update_user_score(username, score, time_taken, accuracy, words_typed):
    query = f"SELECT score FROM {TABLE_NAME} WHERE username = %s"
    MYCURSOR.execute(query, (username,))
    old_score = MYCURSOR.fetchone()

    
    if old_score[0] is None:
        old_score = (0,)

    if score > old_score[0]:
        update_query = f"UPDATE {TABLE_NAME} SET score = %s, time = %s, accuracy = %s, words_typed = %s WHERE username = %s"
        update_values = (score, time_taken, accuracy, words_typed, username)
        MYCURSOR.execute(update_query, update_values)
        CONNECT.commit()
        pprint("\nYour data has been updated.", wait=0.1, progressive=0.2)
    else:
        pprint("\nYour new score is not bigger than the old score. Data was not updated.", wait=0.1, progressive=0.2)



# paragraph functions -------
def get_all_paragraphs():
	file = open("paragraphs.txt","r")

	paragraphs = file.read().split(FILE_SEPERATOR)
	paragraphs = [para.strip("\n") for para in paragraphs]

	return paragraphs


#score functions -------
    
def calculate_accuracy(original,user):

	user = user[:len(original)]
	
	score = 0

	for i in range(len(user)):
		
		if user[i] == original[i]:
			if user[i].isspace():
				score += 0.5
			else:
				score += 1

	accuracy = (score/len(original)) * 100


	

	return round(accuracy,2)





#single test loop -------

def dotypingtest():
	paragraphs = get_all_paragraphs()

	print(" "* 30)
	pprint("1. A random paragraph will be shown, and the timer will start immediately.",wait = 0.5,progressive = 0.09)
	pprint("2. Press [Enter] to start the test and press [Enter] again to stop the timer.",wait = 0.5,progressive = 0.08)
	print(" "* 30)

	start = input()


	para = random.choice(paragraphs)
	pprint(para,wait = 0.1,progressive = 0.01)
	print("[Enter to stop]")

	start_time = time.time()

	user_input = input()

	end_time = time.time()

	accuracy = calculate_accuracy(para,user_input)
	time_taken = round(end_time - start_time,2)
	words_typed = len(user_input.split())

	if time_taken == 0:
		time_taken = 0.1
	score = round(accuracy* 1.5  * (1/time_taken)  * words_typed )

	pprint("\nResults")
	pprint("Accuracy :",accuracy)
	pprint("Timetaken :",time_taken)
	pprint("Words typed :",words_typed)
	pprint("Your Score :",score)

	return accuracy,time_taken,words_typed,score

	#update user score


#special functions -------

def setLogin():
	global SQL_HOST,SQL_PASSWORD,SQL_USERNAME,CONNECT,MYCURSOR

	try: 
		file = open('log.txt','r')
		text = file.read().split("\n")
		
		SQL_HOST = text[1]		
		SQL_USERNAME = text[2]
		SQL_PASSWORD = text[3]
		

		CONNECT = mysql.connector.connect(host=SQL_HOST,user=SQL_USERNAME,password=SQL_PASSWORD)
		MYCURSOR=CONNECT.cursor()
		file.close()

		text[0] = str(int(text[0]) + 1)
		file = open("log.txt",'w')	
		file.write("\n".join(text))
		file.close()

	except:

		file = open('log.txt','w')
		file.write("0\n")
		print("We need to configure some sql settings to start.")
		print("If you ever want to change any of them in the future please delete the log file and run the program again.")
		host = input(f"1. If '{SQL_HOST}' is your host [ENTER] else type your host: ")
		if host:
			SQL_HOST = host
		username = input(f"2. If '{SQL_USERNAME}' is your username [ENTER] else type your username: ")
		if username:
			SQL_USERNAME = username
		password = input(f"3. If '{SQL_PASSWORD}' is your password [ENTER] else type your password: ")
		if password:
			SQL_PASSWORD = password
		file.write("\n".join([SQL_HOST,SQL_USERNAME,SQL_PASSWORD]))

		file.close()

		setLogin()
	





def pprint(*text,wait = 0.1,progressive = 0,end = "\n"):

	if not PPRINT_ALLOWED:
		wait = 0
		progressive = 0
		

	text = [str(part) for part in text]
	for i in " ".join(text):
		print(i,end = "")
		time.sleep(wait)

		if progressive:
			wait -= progressive
			wait = abs(wait)
	print(end,end = "")


def tabulatea(rows):
	#failed function
	
	transposed_list = [[row[i] for row in rows] for i in range(len(rows[0]))]
	print(transposed_list)

	maxs = [(str(i)) for i in transposed_list]
	print(maxs)
	return

	

	for row in rows:
		for index,cell in enumerate(row):

			print(cell.zfill(" ",maxs[index]),end = "")


def noprettyprinting():
	global PPRINT_ALLOWED

	ans = input("To stop slow printing press [a]: ")
	
	if ans.lower() == "a":
		PPRINT_ALLOWED = False
		print("Set to False")


# main loop

def mainloop():

	#setup
	setLogin()
	create_database()
	create_table()

	print(LOGONAME)

	#usercreation
	username = input("Enter your username: ")

	search_username_or_add(username) 

	noprettyprinting()	
	

	dotest = True

	pprint("\nStarting... Starting... Starting...",wait = 0.5,progressive = 0.2)

	while dotest:
		accuracy,time_taken,words_typed,score = dotypingtest()

		update_user_score(username,score,time_taken,accuracy,words_typed)

		pprint("\nPrinting scoreboard... Please wait...",wait = 0.5,progressive = 0.2)

		show_table()

		again = input("\nTo do the typing test again, press[a]: ")

		if again.lower() != "a":
			pprint("Thank you for playing!",wait = 0.23,progressive = 0.2)
			break
		else: 
			pass

mainloop()







