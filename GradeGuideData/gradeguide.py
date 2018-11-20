import sqlite3
import csv
import plotly.plotly as py
import plotly.graph_objs as go
grades_csv = "w18_foia_grades.csv"

#CREATE SQL

DBNAME = "grade_guide.db"

def init_db(db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    statement = '''
        DROP TABLE IF EXISTS 'Grades';
    '''
    cur.execute(statement)
    conn.commit()
    s = '''
        CREATE TABLE 'Grades' (
            'Term' TEXT NOT NULL,
            'AcadGroup' TEXT NOT NULL,
            'AcadGroupDecrip' TEXT NOT NULL,
            'Subject' TEXT NOT NULL,
            'CatalogNumber' INTEGER NOT NULL,
            'CourseGrade' TEXT NOT NULL,
            'ClassGradeCount' INTEGER NOT NULL
        );
    '''
    cur.execute(s)
    conn.commit()
    conn.close()
def insert_grades(grades_csv):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    with open(grades_csv) as csvDataFile:
        csvReader = csv.reader(csvDataFile)
        num = 0
        for row in csvReader:
            num = num + 1
            if num == 1:
                continue
            Term = row[0]
            AcadGroup = row[1]
            AcadGroupDecrip = row[2]
            Subject = row[3]
            CatalogNumber= row[4]
            CourseGrade = row[5]
            ClassGradeCount = row[6]
            insert = (Term,AcadGroup,AcadGroupDecrip,Subject,CatalogNumber,CourseGrade,ClassGradeCount)
            statement = 'INSERT INTO Grades '
            statement += 'VALUES (?,?,?,?,?,?,?)'
            cur.execute(statement, insert)
            conn.commit()
        conn.close()

#QUERIES ARE BELOW:
#---------------------------------------------------------------------------------
#Information came from University of Michigan Website: https://lsa.umich.edu/lsa/academics/lsa-requirements/grade-point-average/computing-your-grade-point-average.html
MAPPING = {
    'A+': 4.3,
	'A': 4.0,
	'A-': 3.7,
	'B+': 3.3,
	'B': 3.0,
	'B-': 2.7,
    'C+': 2.3,
    'C': 2.0,
    'C-': 1.7,
    'D+': 1.3,
    "D": 1.0,
    "D-": 0.7,
    "E": 0.0
    }
#BELOW FUNCTIONS: Gets the GPA for a class in a department
#---------------------------------------------------------------------------------
#Parameters: Subject and CatalogNumber
#Returns: a list of possible grades that can be recieved for the class
def all_possible_grades_forclass(Subject, CatalogNumber):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    #classes_in_depart = gets_class_numbers_for_department(Subject)
    possible_grades = []
    statement = '''
        SELECT CourseGrade
        FROM Grades
        WHERE Subject = "{}" AND CatalogNumber = "{}"
        GROUP BY CourseGrade
    '''.format(Subject,CatalogNumber)
    cur.execute(statement)
    for y in cur:
        if y[0] not in ["IA+","IA","IA-","IB+","IB","IB-","IC+","IC","IC-","ID+","ID","ID-","IE+","IE","IE-"]:
            possible_grades.append(y[0])
    conn.close()
    #print(possible_grades)
    return possible_grades
#Parameters: Subject (Department), CatalogNumber (class number)
#Return: the number of students who recieved each type of grade for a specified class
def CountStudents_MappedGrades_PerClass(Subject,CatalogNumber):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    Subject = Subject.upper()
    possible_grades = all_possible_grades_forclass(Subject,CatalogNumber)
    dic = {}
    for grade in possible_grades:
        s = '''
            SELECT SUM(ClassGradeCount)
            FROM Grades
            WHERE Subject = '{}' AND CatalogNumber = "{}" AND CourseGrade ="{}"
        '''.format(Subject,CatalogNumber,grade)
        cur.execute(s)
        for x in cur:
            total_count = x[0]
            dic[grade] = total_count
    conn.close()
    return dic
#print(CountStudents_MappedGrades_PerClass("BIOLOGY",116))
#parameters: Subject (Department),CatalogNumber (class number)
#return: dictionary with letter grade mapped to the total number of
#students who recieved that grade for the class
def GPA_for_class(Subject,CatalogNumber):
    class_dic = CountStudents_MappedGrades_PerClass(Subject,CatalogNumber)
    running_sum = 0
    running_count = 0
    for grade in class_dic:
        running_sum += MAPPING[grade]*class_dic[grade]
        running_count += class_dic[grade]
    return running_sum/running_count

#BELOW FUNCTIONS: Gets the GPA for a department
#---------------------------------------------------------------------------------
#parameters: takes in a Subject (department)
#returns a list of all possible grades recieved across all classes in a specified department
def possible_grades_department(Subject):
    Subject = Subject.upper()
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    possible_grades = []
    statement = '''
        SELECT CourseGrade
        FROM Grades
        WHERE Subject = "{}"
        GROUP BY CourseGrade
    '''.format(Subject)
    cur.execute(statement)
    for x in cur:
        if x[0] not in ["IA+","IA","IA-","IB+","IB","IB-","IC+","IC","IC-","ID+","ID","ID-","IE+","IE","IE-"]:
            possible_grades.append(x[0])
    conn.close()
    return possible_grades
#Parameters: Subject(department), CatalogNumber(class number)
#Returns the number of students who recieved each type of grade
# across all classes in the department
def CountStudents_MappedGrades_Department(Subject):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    Subject = Subject.upper()
    possible_grades = possible_grades_department(Subject)
    dic = {}
    for grade in possible_grades:
        s = '''
            SELECT SUM(ClassGradeCount)
            FROM Grades
            WHERE Subject = '{}' AND CourseGrade ="{}"
        '''.format(Subject,grade)
        cur.execute(s)
        for x in cur:
            total_count = x[0]
            dic[grade] = total_count
    conn.close()
    return dic
def GPA_for_department(Subject):
    class_dic = CountStudents_MappedGrades_Department(Subject)
    running_sum = 0
    running_count = 0
    for grade in class_dic:
        running_sum += MAPPING[grade]*class_dic[grade]
        running_count += class_dic[grade]
    return running_sum/running_count


#BELOW FUNCTION: GETS THE AVERAGE
#---------------------------------------------------------------------------------
def possible_grades_class_one(Subject,CatalogNumber):
    Subject = Subject.upper()
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    possible_grades = []
    statement = '''
        SELECT CourseGrade
        FROM Grades
        WHERE Subject = "{}" AND CatalogNumber = "{}"
        GROUP BY CourseGrade
    '''.format(Subject,CatalogNumber)
    cur.execute(statement)
    for y in cur:
        if y[0] in ["A","B","C","D","E","IA","IB","IC","ID","IE"]:
            possible_grades.append(y[0])
    conn.close()
    return possible_grades
#paramters takes in a subject
#returns an integer that represents the total number of
#students who have taken a class in the department
def getTotalCountStudents_department(Subject):
    Subject = Subject.upper()
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    s = '''
        SELECT SUM(ClassGradeCount)
        FROM Grades
        WHERE Subject = '{}'
    '''.format(Subject)
    cur.execute(s)
    for x in cur:
        total_count = x[0]
    conn.close()
    return total_count
#parameters: takes in a Subject
#returns a list of all possible grades recieved
#in a department not including +'s and -'s
def possible_grades_department(Subject):
    Subject = Subject.upper()
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    possible_grades = []
    statement = '''
        SELECT CourseGrade
        FROM Grades
        WHERE Subject = "{}"
        GROUP BY CourseGrade
    '''.format(Subject)
    cur.execute(statement)
    for x in cur:
        if x[0] in ["A","B","C","D","E","IA","IB","IC","ID","IE"]:
            possible_grades.append(x[0])
    conn.close()
    return possible_grades
#parameter: subject
#finds the total number of students who have taken a class in the department
#Then finds the different course grades recieved in the department
#Creates a list of all the possible grades a student has recieved
# Then counts the number of students who recieved each particular grade
#calculates:number of students who recieved that particualr grade /total number of students that have taken the class
#finds the highest percentage out of all the different grades
#returns a list of highest grade percentage (percent of poeple who recieved that grade) and highest grade
def average_grade_for_department(Subject):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    Subject = Subject.upper()
    total_count = getTotalCountStudents_department(Subject)
    possible_grades = possible_grades_department(Subject)
    avg = {}
    for grade in possible_grades:
        statement = '''
            SELECT SUM(ClassGradeCount)
            FROM GRADES
            WHERE Subject = "{}" AND CourseGrade LIKE "{}%"
        '''.format(Subject,grade)
        cur.execute(statement)
        for x in cur:
            grade_count = x[0]
            avg[grade] = grade_count/total_count
    highest_percentage = -1
    for x in avg:
        if avg[x] > highest_percentage:
            highest_percentage = avg[x]
            highest_percentage_grade = x
    #print(highest_percentage, highest_percentage_grade)
    conn.close()
    department = [highest_percentage, highest_percentage_grade]
    #hardest_classes_compared_to_depart_avg(Subject,department)
    return department
#parameter: a subject (department)
#returns a list of classes in the department (a list of class numbers or CatalogNumbers)
def gets_class_numbers_for_department(Subject):
    Subject = Subject.upper()
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    statement = '''
        SELECT CatalogNumber
        FROM Grades
        WHERE Subject = "{}"
        GROUP BY Subject,CatalogNumber
    '''.format(Subject)
    cur.execute(statement)
    classes_in_depart = []
    for x in cur:
        classes_in_depart.append(x[0])
    conn.close()
    return classes_in_depart
#parameters: Subject (department) and CatalogNumber (class number)
#return: Integer that represents the total number of students who took the class
def getTotalCountStudents_for_class(Subject,CatalogNumber):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    Subject = Subject.upper()
    s = '''
        SELECT SUM(ClassGradeCount)
        FROM Grades
        WHERE Subject = '{}' AND CatalogNumber = "{}"
    '''.format(Subject,CatalogNumber)
    cur.execute(s)
    for x in cur:
        total_count = x[0]
    conn.close()
    return total_count

def get_dic_for_average_grades_for_class(Subject,CatalogNumber):
    Subject = Subject.upper()
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    possible_grades = possible_grades_class_one(Subject,CatalogNumber)
    dic = {}
    for grade in possible_grades:
        statement = '''
            SELECT SUM(ClassGradeCount)
            FROM GRADES
            WHERE Subject = "{}" AND CatalogNumber = "{}" AND CourseGrade LIKE "{}%"
        '''.format(Subject,CatalogNumber,grade)
        cur.execute(statement)
        for x in cur:
            dic[grade] = x[0]/getTotalCountStudents_for_class(Subject,CatalogNumber)
    conn.close()
    return dic

def return_highest_average_grade_for_class(Subject,CatalogNumber):
    Subject = Subject.upper()
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    possible_grades = possible_grades_class_one(Subject,CatalogNumber)
    dic = {}
    for grade in possible_grades:
        statement = '''
            SELECT SUM(ClassGradeCount)
            FROM GRADES
            WHERE Subject = "{}" AND CatalogNumber = "{}" AND CourseGrade LIKE "{}%"
        '''.format(Subject,CatalogNumber,grade)
        cur.execute(statement)
        for x in cur:
            dic[grade] = x[0]/getTotalCountStudents_for_class(Subject,CatalogNumber)
    highest = -1
    grade = None
    for x in dic:
        if dic[x] > highest:
            highest = dic[x]
            grade = x
    conn.close()
    return highest,grade

def hardest_classes_compared_to_depart_avg(Subject,department_average):
    #gets a list of catalognumbers for classes in the department
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    classes_in_depart = gets_class_numbers_for_department(Subject)
    total_class = {}
    #print(classes_in_depart)
    for numb in classes_in_depart:
        total_count = getTotalCountStudents_for_class(Subject,numb)
        class_num = numb
        total_class[class_num] = total_count
    class_numb_avg = {}
    avg= {}
    highest_grade = "None"
    highest_percent_class = -1
    #print(total_class)
    for numb in classes_in_depart:
        dic = get_dic_for_average_grades_for_class(Subject,numb)
        class_numb_avg[numb] = dic
        #possible_grades = possible_grades_class(Subject,numb)
    #print(class_numb_avg)
    depart_grade = department_average[1]
    depart_percent = department_average[0]
    classes = [] #lists with number of class, class grade, and class percent
    for x in class_numb_avg:
        worst = return_highest_average_grade_for_class(Subject,x)
        class_grade = worst[1]
        class_percent = worst[0]
        c = []
        if depart_grade == "A":
            if depart_grade == class_grade:
                 continue
            else:
                c.append([x,class_grade, class_percent])
                classes = classes + c
        elif depart_grade == "B":
            if class_grade == "A":
                continue
            if depart_grade == class_grade:
                 continue
            else:
                c.append([x,class_grade, class_percent])
                classes = classes + c
        elif depart_grade == "C":
            if class_grade == "A":
                continue
            if class_grade == "B":
                continue
            if depart_grade == class_grade:
                 continue
            else:
                c.append([x,class_grade, class_percent])
                classes = classes + c
    if len(classes) == 0:
        return None
    conn.close()
    print("The Average Department grade for {} is {} ,{}, and the classes below this average: ".format(Subject,depart_grade,depart_percent))
    for x in classes:
        print("\t {} {}: \n \t\t Average Grade = {}, {}".format(Subject,x[0],x[1],x[2]))
#goes through every department at michigan and compares each class average to the department average
def check_every_department():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    subjects = []
    statement = '''
        SELECT Subject
        FROM Grades
        GROUP BY Subject
    '''
    cur.execute(statement)
    for x in cur:
        subjects.append(x[0])
    for x in subjects:
        average = average_grade_for_department(x)
        result = hardest_classes_compared_to_depart_avg(x,average)
#BELOW FUNCTIONS: Finds an class average grad
#---------------------------------------------------------------------------------
#Parameters: Subject, CatalogNumber, grade (enter a subject, course number, and grade (i.e., A,B,C) you would like averaged)
#Return: an average grade for the class and also will also show a pie chart
def find_average_grade(Subject,CatalogNumber,grade):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    #find the total number of students who recieved the grade
    statement = '''
        SELECT SUM(ClassGradeCount)
        FROM GRADES
        WHERE Subject = "{}" AND CatalogNumber = "{}" AND CourseGrade LIKE "{}%"
    '''.format(Subject,CatalogNumber,grade.upper())
    cur.execute(statement)
    for x in cur:
        count_grade =x[0]
    #find the toal number of students who took the class
    s = '''
        SELECT SUM(ClassGradeCount)
        FROM Grades
        WHERE Subject = '{}' AND CatalogNumber = '{}'
    '''.format(Subject,CatalogNumber)
    cur.execute(s)
    for x in cur:
        total_count = x[0]

    conn.close()
    average = count_grade/total_count
    Subject = Subject
    CatalogNumber = CatalogNumber
    grade = grade
    average_grade_pie_chart(average,grade,Subject,CatalogNumber)
    return average
def average_grade_pie_chart(average,grade,subject,catalognum):
    other_grade = 1 - average
    title = "Average Number of Students Who Get an {} In {} {}".format(grade.upper(),subject,catalognum)
    percent_grade = "percent of students who got an {}".format(grade.upper())
    fig = {
        'data': [{'labels': [percent_grade, "percent who got a different grade"],
                  'values':  [average, other_grade],
                  'type': 'pie'}],
        'layout': {'title': title}
        }
    py.plot(fig)

if __name__=="__main__":
    #test GPA_for_class Function:
    #Class=CountStudents_MappedGrades_PerClass("EECS",183)
    # print(GPA_for_class("EECS",381))
    #test GPA_for_class Function:
    print(GPA_for_department("EECS"))
    #check_every_department()
    # find_average_grade("URP", "357","A")
