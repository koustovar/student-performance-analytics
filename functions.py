"""Reusable validation and analysis functions for student records."""

import numpy as np
import pandas as pd

SUBJECTS = [
    "Math",
    "Physics",
    "Chemistry",
    "Computer_Science",
    "English"
]

REQUIRED_COLUMNS = [
    "Student_ID",
    "Name",
    "Department",
    *SUBJECTS,
    "Attendance"
]

NUMERIC_COLUMNS = ["Student_ID", *SUBJECTS, "Attendance"]


def validate_student_data(data, minimum_records=20):
    """Validate and return a normalized copy of the student dataset."""

    if not isinstance(data, pd.DataFrame):
        raise TypeError("Expected student data as a pandas DataFrame.")

    issues = []
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in data.columns]
    if missing_columns:
        issues.append(f"Missing required columns: {', '.join(missing_columns)}.")

    unexpected_columns = [
        column for column in data.columns
        if isinstance(column, str) and column != column.strip()
    ]
    if unexpected_columns:
        issues.append(
            "Column names contain leading or trailing spaces: "
            f"{unexpected_columns}."
        )

    if len(data) < minimum_records:
        issues.append(
            f"Expected at least {minimum_records} student records; found {len(data)}."
        )

    if missing_columns:
        raise ValueError("\n".join(issues))

    validated_data = data.copy()

    for column in ["Name", "Department"]:
        blank_values = validated_data[column].isna() | (
            validated_data[column].astype("string").str.strip() == ""
        )
        if blank_values.any():
            rows = (np.flatnonzero(blank_values.to_numpy()) + 2).tolist()
            issues.append(f"{column} is missing or blank on CSV rows {rows}.")

    for column in NUMERIC_COLUMNS:
        values = pd.to_numeric(validated_data[column], errors="coerce")
        invalid_numeric = values.isna() | ~np.isfinite(values)
        if invalid_numeric.any():
            rows = (np.flatnonzero(invalid_numeric.to_numpy()) + 2).tolist()
            issues.append(f"{column} must contain numeric values on CSV rows {rows}.")
        validated_data[column] = values

    student_ids = validated_data["Student_ID"]
    valid_ids = student_ids.notna() & np.isfinite(student_ids)
    if (student_ids[valid_ids] % 1 != 0).any():
        issues.append("Student_ID values must be whole numbers.")
    duplicate_ids = student_ids[valid_ids].duplicated(keep=False)
    if duplicate_ids.any():
        duplicate_values = sorted(student_ids[valid_ids][duplicate_ids].unique().tolist())
        issues.append(f"Duplicate Student_ID values: {duplicate_values}.")

    for column in [*SUBJECTS, "Attendance"]:
        values = validated_data[column]
        out_of_range = values.notna() & ~values.between(0, 100)
        if out_of_range.any():
            rows = (np.flatnonzero(out_of_range.to_numpy()) + 2).tolist()
            issues.append(f"{column} must be between 0 and 100 on CSV rows {rows}.")

    if issues:
        raise ValueError("\n".join(issues))

    validated_data["Student_ID"] = validated_data["Student_ID"].astype("int64")
    return validated_data


def _numeric_subjects(data):
    """Return subject columns as numeric values and a mask of valid rows."""

    if not isinstance(data, pd.DataFrame):
        raise TypeError("Expected student data as a pandas DataFrame.")

    missing = [subject for subject in SUBJECTS if subject not in data.columns]
    if missing:
        raise ValueError(f"Missing required subject columns: {missing}.")

    subjects = data[SUBJECTS].apply(pd.to_numeric, errors="coerce")
    valid_values = subjects.notna() & np.isfinite(subjects) & subjects.ge(0) & subjects.le(100)
    valid_rows = valid_values.all(axis=1)
    return subjects, valid_rows


def calculate_total_marks(data):
    """Calculate each student's total; invalid subject rows receive NaN."""

    working_data = data.copy()
    subjects, valid_rows = _numeric_subjects(data)
    totals = subjects.sum(axis=1, min_count=len(SUBJECTS))
    working_data["Total_Marks"] = totals.where(valid_rows)
    return working_data


def calculate_average_marks(data):
    """Calculate each student's average to two decimals; invalid rows receive NaN."""

    working_data = data.copy()
    subjects, valid_rows = _numeric_subjects(data)
    averages = np.round(subjects.mean(axis=1), 2)
    working_data["Average_Marks"] = averages.where(valid_rows)
    return working_data


def assign_grade(average):
    """Assign a grade using the project's fixed average-mark boundaries."""

    try:
        numeric_average = float(average)
    except (TypeError, ValueError) as error:
        raise ValueError("Average marks must be a finite number from 0 to 100.") from error

    if not np.isfinite(numeric_average) or not 0 <= numeric_average <= 100:
        raise ValueError("Average marks must be a finite number from 0 to 100.")
    if numeric_average >= 90:
        return "A+"
    elif numeric_average >= 80:
        return "A"
    elif numeric_average >= 70:
        return "B"
    elif numeric_average >= 60:
        return "C"
    elif numeric_average >= 50:
        return "D"
    return "F"


def calculate_grades(data):
    """Assign a grade to each row using its Average_Marks value."""

    if "Average_Marks" not in data.columns:
        raise ValueError("Average_Marks column is required before calculating grades.")

    working_data = data.copy()
    working_data["Grade"] = [
        assign_grade(average) for average in working_data["Average_Marks"]
    ]
    return working_data


def calculate_result(data):
    """Mark students as passing only if all five valid subject marks are at least 40."""

    working_data = data.copy()
    subjects, valid_rows = _numeric_subjects(data)
    passed = valid_rows & subjects.ge(40).all(axis=1)
    working_data["Result"] = np.where(passed, "Pass", "Fail")
    return working_data


def calculate_class_statistics(data):
    """Calculate class size, average, highest/lowest averages, and pass/fail counts."""

    required = ["Average_Marks", "Result"]
    missing = [column for column in required if column not in data.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}.")
    if data.empty:
        raise ValueError("Cannot calculate class statistics for an empty dataset.")

    averages = pd.to_numeric(data["Average_Marks"], errors="coerce")
    if averages.isna().any() or not np.isfinite(averages).all():
        raise ValueError("Average_Marks must contain only finite numeric values.")
    if not data["Result"].isin(["Pass", "Fail"]).all():
        raise ValueError("Result must contain only 'Pass' or 'Fail'.")

    return {
        "Total_Students": len(data),
        "Class_Average": round(float(averages.mean()), 2),
        "Highest_Average": round(float(averages.max()), 2),
        "Lowest_Average": round(float(averages.min()), 2),
        "Students_Passed": int((data["Result"] == "Pass").sum()),
        "Students_Failed": int((data["Result"] == "Fail").sum())
    }


def analyze_subjects(data):
    """Calculate the average, highest, and lowest mark for every subject."""

    subjects, valid_rows = _numeric_subjects(data)
    if not valid_rows.all():
        raise ValueError("Cannot analyze subjects while marks are missing or invalid.")

    return pd.DataFrame({
        "Average": np.round(subjects.mean(), 2),
        "Highest": subjects.max(),
        "Lowest": subjects.min()
    })


def get_top_performers(data, count=3):
    """Return up to count students with the highest averages, preserving tie order."""

    if "Average_Marks" not in data.columns:
        raise ValueError("Average_Marks column is required to rank performers.")
    if not isinstance(count, int) or isinstance(count, bool):
        raise TypeError("count must be a non-negative integer.")
    if count < 0:
        raise ValueError("count must be a non-negative integer.")

    working_data = data.copy()
    working_data["Average_Marks"] = pd.to_numeric(
        working_data["Average_Marks"], errors="coerce"
    )
    working_data = working_data[
        np.isfinite(working_data["Average_Marks"])
        & working_data["Average_Marks"].between(0, 100)
    ]
    return working_data.sort_values(
        "Average_Marks", ascending=False, kind="stable"
    ).head(count)
