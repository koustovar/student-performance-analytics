Student Performance Analytics System

1. Project Title

Student Performance Analytics System

A Python-based data analysis application that processes student academic
records and produces individual and class-level performance reports
using NumPy and Pandas.

2. Objective

The objective of this project is to analyze student marks and attendance
from a CSV dataset and present useful academic performance information.
The system is designed to:

Load and validate student records.

Calculate each student's total and average marks across five
subjects.

Assign grades using predefined average-mark boundaries.

Determine pass or fail status based on marks in every subject.

Calculate class-level statistics.

Analyze subject-wise averages, highest marks, and lowest marks.

Identify the three students with the highest average marks.

Summarize attendance and identify students with attendance below
75%.

Export student and subject analysis to CSV reports.

3. Technologies Used

Python 3.12: application logic, functions, conditionals, loops,
and error handling.

Pandas: CSV input/output, DataFrame processing, filtering, and
statistical summaries.

NumPy: numerical validation, finite-value checks, rounding, and
calculations.

CSV: storage format for the input dataset and generated reports.

Git and GitHub: intended source-control and project-hosting
tools.

The listed runtime dependencies are numpy and pandas, as specified
in requirements.txt.

4. Dataset Description

The input file is students.csv. It contains 20 sample student records
and these required columns:

Column               Description

Student_ID         Unique whole-number identifier for each student
Name               Student's name
Department         Student's department
Math               Mathematics marks out of 100
Physics            Physics marks out of 100
Chemistry          Chemistry marks out of 100
Computer_Science   Computer Science marks out of 100
English            English marks out of 100
Attendance         Attendance percentage

The five subject marks and attendance values are expected to be numeric
and within the range 0--100. The validation function checks required
columns, minimum record count, blank names or departments, numeric
values, non-finite values, duplicate IDs, whole-number student IDs, and
out-of-range subject or attendance values. The default minimum dataset
size is 20 records.

The dataset is sample data for demonstrating the analysis workflow.

5. Implementation

The project is organized around main.py and functions.py.

main.py

The command-line entry point:

Locates students.csv relative to the project directory.

Loads the CSV file with Pandas.

Handles common file-reading errors.

Validates the dataset before analysis.

Calls the reusable analysis functions.

Prints dataset details and reports in the terminal.

Saves the student and subject reports as CSV files.

functions.py

This module contains reusable validation and analysis functions:

validate_student_data(data, minimum_records=20): checks the
dataset structure and values and returns a normalized copy.

calculate_total_marks(data): calculates each student's total
across the five subjects. Rows with invalid subject values receive a
missing total.

calculate_average_marks(data): calculates each student's average
to two decimal places. Rows with invalid subject values receive a
missing average.

assign_grade(average): assigns a grade from the configured grade
boundaries.

calculate_grades(data): adds a grade for each average.

calculate_result(data): returns Pass only when all five subject
marks are valid and at least 40; otherwise it returns Fail.

calculate_class_statistics(data): calculates class size, class
average, highest and lowest student averages, and pass/fail counts.

analyze_subjects(data): calculates each subject's average, highest
mark, and lowest mark.

get_top_performers(data, count=3): returns up to the requested
number of students, ordered by average marks. Stable sorting
preserves input order for tied averages.

Grade criteria

 Average marks Grade

  90 and above A+
80 to below 90 A
70 to below 80 B
60 to below 70 C
50 to below 60 D
      Below 50 F

A student's grade is based on the average mark. Pass/fail status is
determined separately: a student must score at least 40 in every subject
to pass.

Report generation

The program generates these files in the project directory:

student_performance_report.csv: original validated student fields
plus calculated totals, averages, grades, and results.

subject_performance_report.csv: subject-wise average, highest, and
lowest marks, with the subject name as the index label.

The program also prints average attendance and lists students whose
attendance is below 75%.

6. Key Features

CSV dataset loading using Pandas.

Dataset validation for required columns, record count, missing
or blank text fields, invalid numeric data, duplicate student IDs,
and out-of-range values.

Total and average calculations across five subjects.

Grade assignment using fixed average-mark thresholds.

Pass/fail analysis requiring at least 40 marks in every subject
to pass.

Class statistics including student count, class average, highest
and lowest averages, and pass/fail counts.

Subject-wise analysis showing average, highest, and lowest
marks.

Top-three ranking based on average marks.

Attendance analysis showing the class average attendance and
students below 75%.

CSV report export for further review or reuse.

Error handling for missing, unreadable, or invalid input data.

Unit tests intended to check calculation logic, validation
rules, ranking, and report generation.

7. Output and Screenshots

When run with the provided 20-record dataset, the program displays
dataset information, a student performance report, class statistics,
subject-wise analysis, the top three performers, attendance analysis,
and report-generation messages.

The recorded run shown during development reported:

Total records: 20

Class average: 80.46

Highest student average: 97.0

Lowest student average: 42.0

Students passed: 19

Students failed: 1

Average attendance: 89.05%

Students with attendance below 75%: 2

The top three students in that run were Diya Mukherjee (97.0), Priya Roy
(95.0), and Tanisha Roy (94.8).

Insert genuine screenshots before submission:

Screenshot 1: Terminal output --- capture the program running
with python main.py.

Screenshot 2: Student report --- show
student_performance_report.csv opened in an editor or spreadsheet
application.

Screenshot 3: Subject report --- show
subject_performance_report.csv.

Screenshot 4: Tests --- capture the actual output after running
the unit tests.

Do not use placeholder images as evidence of execution. The figures
above describe the previously supplied terminal output; rerun the
current code before submission to confirm they remain the same.

8. Final Outcome

The project brings together CSV handling, data validation, reusable
Python functions, NumPy numerical operations, and Pandas DataFrame
analysis in a single command-line application. It produces both
individual student results and class/subject summaries, and exports the
analysis to CSV files.

The application was shown running successfully on the provided dataset
during development. The unit-test file includes checks for grade
boundaries, invalid marks, pass/fail rules, class statistics, subject
statistics, top-performer ordering, validation failures, and report
generation. The test suite should be run and its actual result recorded
before submission; the presence of tests alone does not establish that
they pass.

9. Challenges and Learning

Challenges addressed

Input validation: checking that required columns and valid
numeric values are present before analysis.

Invalid values: preventing incomplete or out-of-range subject
marks from producing misleading totals or averages.

Pass/fail rules: separating grade assignment based on average
marks from the requirement to score at least 40 in every subject.

Reusable design: placing validation and calculations in
functions rather than keeping all logic in the command-line entry
point.

Report generation: saving analysis results to CSV files so they
can be opened and reviewed separately.

Error handling: displaying readable messages when the input file
cannot be read or fails validation.

Learning outcomes

Through this project, the implementation demonstrates:

Python functions, loops, conditional statements, and exceptions.

Reading and writing CSV files.

Creating and manipulating Pandas DataFrames.

Using NumPy for numeric validation and rounding.

Filtering and summarizing tabular data.

Designing and running unit tests.

Organizing a small Python project for source control.

10. GitHub Repository

Repository URL: https://github.com/koustovar/student-performance-analytics.git

Replace the placeholder above with the actual public or
submission-accessible GitHub repository URL before submitting.

The repository should include the source code, input dataset,
requirements.txt, README, project documentation, tests, .gitignore,
and any required screenshots. Do not commit the .venv/ virtual
environment or generated Python cache files.

Running the project

From the project directory, create and activate a virtual environment,
install dependencies, and run the application.

Windows PowerShell:

python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py

Run the unit tests with:

python -m unittest test_project.py -v

