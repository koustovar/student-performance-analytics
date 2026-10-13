"""Unit tests for student data validation, calculations, and report generation."""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

import main
from functions import (
    SUBJECTS,
    analyze_subjects,
    assign_grade,
    calculate_average_marks,
    calculate_class_statistics,
    calculate_grades,
    calculate_result,
    calculate_total_marks,
    get_top_performers,
    validate_student_data
)


PROJECT_DIR = Path(__file__).resolve().parent


class StudentAnalyticsTests(unittest.TestCase):
    def setUp(self):
        self.data = pd.read_csv(PROJECT_DIR / "students.csv")
        self.validated_data = validate_student_data(self.data)

    def test_total_and_average_marks_and_original_is_unchanged(self):
        original = self.data.copy(deep=True)

        totals = calculate_total_marks(self.data)
        averages = calculate_average_marks(self.data)

        self.assertEqual(totals.loc[0, "Total_Marks"], 450)
        self.assertEqual(averages.loc[0, "Average_Marks"], 90.0)
        pd.testing.assert_frame_equal(self.data, original)

    def test_invalid_marks_do_not_produce_partial_totals_or_averages(self):
        for invalid_value in [None, "not a mark", -1, 101]:
            with self.subTest(invalid_value=invalid_value):
                student = self.data.iloc[[0]].copy()
                student["Math"] = student["Math"].astype(object)
                student.loc[student.index[0], "Math"] = invalid_value
                self.assertTrue(
                    pd.isna(calculate_total_marks(student)["Total_Marks"].iloc[0])
                )
                self.assertTrue(
                    pd.isna(calculate_average_marks(student)["Average_Marks"].iloc[0])
                )
                self.assertEqual(calculate_result(student)["Result"].iloc[0], "Fail")

    def test_every_grade_boundary(self):
        grade_cases = [
            (90, "A+"), (89.99, "A"),
            (80, "A"), (79.99, "B"),
            (70, "B"), (69.99, "C"),
            (60, "C"), (59.99, "D"),
            (50, "D"), (49.99, "F"),
            (0, "F"), (100, "A+")
        ]
        for average, expected_grade in grade_cases:
            with self.subTest(average=average):
                self.assertEqual(assign_grade(average), expected_grade)

    def test_grade_calculation_returns_a_copy(self):
        data = pd.DataFrame({"Average_Marks": [90, 75]})
        graded = calculate_grades(data)

        self.assertEqual(graded["Grade"].tolist(), ["A+", "B"])
        self.assertNotIn("Grade", data.columns)

    def test_pass_requires_at_least_40_in_each_subject(self):
        passing_student = self.data.iloc[[0]].copy()
        passing_student.loc[passing_student.index[0], "Math"] = 40
        self.assertEqual(calculate_result(passing_student)["Result"].iloc[0], "Pass")

        for subject in SUBJECTS:
            with self.subTest(subject=subject):
                failing_student = passing_student.copy()
                failing_student.loc[failing_student.index[0], subject] = 39
                self.assertEqual(
                    calculate_result(failing_student)["Result"].iloc[0], "Fail"
                )

    def test_class_statistics(self):
        results = calculate_result(
            calculate_grades(calculate_average_marks(self.validated_data))
        )
        statistics = calculate_class_statistics(results)

        self.assertEqual(statistics["Total_Students"], 20)
        self.assertEqual(statistics["Class_Average"], 80.46)
        self.assertEqual(statistics["Highest_Average"], 97.0)
        self.assertEqual(statistics["Lowest_Average"], 42.0)
        self.assertEqual(statistics["Students_Passed"], 19)
        self.assertEqual(statistics["Students_Failed"], 1)

    def test_subject_statistics(self):
        statistics = analyze_subjects(self.validated_data)

        self.assertEqual(statistics.loc["Math", "Average"], 78.3)
        self.assertEqual(statistics.loc["Math", "Highest"], 98)
        self.assertEqual(statistics.loc["Math", "Lowest"], 35)
        self.assertEqual(set(statistics.columns), {"Average", "Highest", "Lowest"})

    def test_top_three_and_tie_order(self):
        analyzed = calculate_grades(calculate_average_marks(self.validated_data))
        top_three = get_top_performers(analyzed)
        self.assertEqual(top_three["Student_ID"].tolist(), [112, 104, 120])

        tied = pd.DataFrame({
            "Student_ID": [12, 10, 11, 13],
            "Average_Marks": [95, 95, 95, 94]
        })
        self.assertEqual(
            get_top_performers(tied)["Student_ID"].tolist(), [12, 10, 11]
        )

    def test_csv_validation_detects_header_records_missing_duplicate_and_ranges(self):
        invalid_data = self.data.copy()
        invalid_data["Math"] = invalid_data["Math"].astype(object)
        invalid_data.loc[0, "Attendance"] = 101
        invalid_data.loc[1, "Math"] = "invalid"
        invalid_data.loc[2, "Student_ID"] = invalid_data.loc[0, "Student_ID"]

        with self.assertRaisesRegex(ValueError, "Duplicate Student_ID"):
            validate_student_data(invalid_data)

        invalid_header = self.data.rename(columns={"Attendance": " Attendance"})
        with self.assertRaisesRegex(ValueError, "Attendance"):
            validate_student_data(invalid_header)

        with self.assertRaisesRegex(ValueError, "at least 20"):
            validate_student_data(self.data.iloc[:19])

        invalid_data = self.data.copy()
        invalid_data.loc[0, "Attendance"] = 101
        with self.assertRaisesRegex(ValueError, "between 0 and 100"):
            validate_student_data(invalid_data)

        invalid_data = self.data.copy()
        invalid_data.loc[0, "Math"] = None
        with self.assertRaisesRegex(ValueError, "Math must contain numeric"):
            validate_student_data(invalid_data)

        invalid_data = self.data.copy()
        invalid_data.loc[0, "Name"] = " "
        with self.assertRaisesRegex(ValueError, "Name is missing or blank"):
            validate_student_data(invalid_data)

    def test_report_generation_and_invalid_csv_handling(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_path = Path(temporary_directory)
            self.data.to_csv(temporary_path / "students.csv", index=False)

            with patch.object(main, "BASE_DIR", temporary_path):
                with contextlib.redirect_stdout(io.StringIO()) as output:
                    main.main()
                self.assertIn("Analysis completed successfully!", output.getvalue())

                student_report = pd.read_csv(
                    temporary_path / "student_performance_report.csv"
                )
                subject_report = pd.read_csv(
                    temporary_path / "subject_performance_report.csv"
                )
                self.assertEqual(len(student_report), 20)
                self.assertIn("Average_Marks", student_report.columns)
                self.assertEqual(subject_report.loc[0, "Subject"], "Math")

                with contextlib.redirect_stdout(io.StringIO()):
                    main.main()
                repeated_report = pd.read_csv(
                    temporary_path / "student_performance_report.csv"
                )
                pd.testing.assert_frame_equal(student_report, repeated_report)

                invalid_data = self.data.copy()
                invalid_data.loc[0, "Math"] = 101
                invalid_data.to_csv(temporary_path / "students.csv", index=False)
                (temporary_path / "student_performance_report.csv").unlink()
                with contextlib.redirect_stdout(io.StringIO()) as output:
                    main.main()
                self.assertIn("Invalid student data", output.getvalue())
                self.assertFalse(
                    (temporary_path / "student_performance_report.csv").exists()
                )


if __name__ == "__main__":
    unittest.main()
