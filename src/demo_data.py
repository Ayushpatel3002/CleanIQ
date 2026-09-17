import numpy as np
import pandas as pd

def get_demo_dataset() -> pd.DataFrame:
    """Generates a realistic enterprise staff dataset with intentional real-world data quality anomalies."""
    np.random.seed(42)
    n = 250
    
    names = ["Alice Smith", "bob jones", "BOB JONES", "Charlie Brown", "Diana Prince", "Evan Wright", None]
    genders = ["Male", "male", "MALE", "Female", "female", "FEMALE", None]
    departments = ["Engineering", "engineering", "HR", "hr", "Marketing", "Sales", "Finance", None]
    emails = ["alice@company.com", "invalid_email@", "charlie#domain.com", "diana@corp.org", None, "evan@tech.io"]
    phones = ["+91-98765-43210", "1234567890", "(555) 234-5678", "invalid_phone", "9876543210", None]
    
    demo_df = pd.DataFrame({
        "Employee_ID": [1000 + i for i in range(n)],
        "Full_Name": np.random.choice(names, size=n),
        "Age": np.random.choice([22, 28, 35, 42, 55, -5, -12, 135, None], size=n),
        "Salary": np.random.choice([45000, 62000, 78000, 95000, -2000, 99999999, None], size=n),
        "Email": np.random.choice(emails, size=n),
        "Phone": np.random.choice(phones, size=n),
        "Gender": np.random.choice(genders, size=n),
        "Department": np.random.choice(departments, size=n),
        "Performance_Score": np.random.choice([75.5, 88.0, 92.5, 64.0, 105.0, -10.0, None], size=n),
        "Joining_Date": np.random.choice(["2021-03-15", "2020-07-20", "2022-11-01", "not-a-date", None], size=n),
        "System_Flag": ["Active"] * n
    })
    return demo_df
