"""Command-line entry point for the student performance analytics system."""

from pathlib import Path

import pandas as pd

from functions import (
    analyze_subjects,
    calculate_average_marks,
    calculate_class_statistics,
    calculate_grades,
    calculate_result,
    calculate_total_marks,
    get_top_performers,
    validate_student_data
)

BASE_DIR = Path(__file__).resolve().parent


def main():
    """Load, validate, analyze, and report on the student dataset."""

    print("=" * 65)
    print("       STUDENT PERFORMANCE ANALYTICS SYSTEM")
    print("=" * 65)

    data_path = BASE_DIR / "students.csv"
    try:
        data = pd.read_csv(data_path)
    except FileNotFoundError:
        print(f"Error: students.csv was not found at {data_path}.")
        return
    except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError) as error:
        print(f"Error: students.csv is not a readable CSV file: {error}")
        return
    except OSError as error:
        print(f"Error: could not read students.csv: {error}")
        return

    try:
        data = validate_student_data(data)
    except (TypeError, ValueError) as error:
        print(f"Invalid student data:\n{error}")
        return

    try:
        print("\n1. DATASET INFORMATION")
        print("-" * 65)
        print("Total Records:", len(data))
        print("\nDataset Columns:")
        print(data.columns.tolist())
        print("\nFirst Five Student Records:")
        print(data.head().to_string(index=False))

        data = calculate_total_marks(data)
        data = calculate_average_marks(data)
        data = calculate_grades(data)
        data = calculate_result(data)

        print("\n\n2. STUDENT PERFORMANCE REPORT")
        print("-" * 65)
        report_columns = [
            "Student_ID",
            "Name",
            "Total_Marks",
            "Average_Marks",
            "Grade",
            "Result"
        ]
        print(data[report_columns].to_string(index=False))

        print("\n\n3. CLASS PERFORMANCE STATISTICS")
        print("-" * 65)
        statistics = calculate_class_statistics(data)
        for key, value in statistics.items():
            print(f"{key.replace('_', ' ')}: {value}")

        print("\n\n4. SUBJECT-WISE PERFORMANCE")
        print("-" * 65)
        subject_statistics = analyze_subjects(data)
        print(subject_statistics.to_string())

        print("\n\n5. TOP THREE PERFORMERS")
        print("-" * 65)
        top_students = get_top_performers(data)
        print(
            top_students[
                ["Student_ID", "Name", "Average_Marks", "Grade"]
            ].to_string(index=False)
        )

        print("\n\n6. ATTENDANCE ANALYSIS")
        print("-" * 65)
        average_attendance = data["Attendance"].mean()
        print(f"Average Attendance: {average_attendance:.2f}%")

        low_attendance = data[data["Attendance"] < 75]
        print("Students with Attendance Below 75%:", len(low_attendance))
        if not low_attendance.empty:
            print(
                low_attendance[
                    ["Student_ID", "Name", "Attendance"]
                ].to_string(index=False)
            )

        student_report_path = BASE_DIR / "student_performance_report.csv"
        subject_report_path = BASE_DIR / "subject_performance_report.csv"
        data.to_csv(student_report_path, index=False)
        subject_statistics.to_csv(subject_report_path, index_label="Subject")
    except OSError as error:
        print(f"Error: could not save or access a report file: {error}")
        return
    except Exception as error:
        print(f"Unexpected analysis error ({type(error).__name__}): {error}")
        return

    print("\n\n7. REPORT GENERATION")
    print("-" * 65)
    print(f"Student report saved successfully: {student_report_path.name}")
    print(f"Subject report saved successfully: {subject_report_path.name}")
    print("\nAnalysis completed successfully!")


if __name__ == "__main__":
    main()
