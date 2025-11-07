
from openpyxl import load_workbook
import os

def generate_output_excel(answers, scores, category):
    wb = load_workbook("data/Platform-Qualification-Checklst.xlsx")
    sheet = wb["Qualification-Checklist"]

    for row in sheet.iter_rows(min_row=13, max_row=31):
        criterion = row[0].value
        if criterion in answers:
            row[2].value = scores[criterion]
            try:
                weight = float(row[3].value)
            except:
                weight = 0
            row[4].value = weight * scores[criterion]
            row[5].value = answers[criterion]

    weighted_scores = []
    for row in sheet.iter_rows(min_row=13, max_row=31):
        try:
            weighted_scores.append(float(row[4].value))
        except:
            continue

    total_score = sum(weighted_scores)
    sheet["F33"] = total_score

    if total_score > 850:
        category_text = "Enterprise-grade Platform"
    elif total_score > 600:
        category_text = "Emerging Platform"
    elif total_score > 300:
        category_text = "Application / Modular Product"
    else:
        category_text = "Application Development"

    sheet["F36"] = f"Project classified as: {category_text}"

    output_path = "data/Platform_Qualification_Result.xlsx"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    wb.save(output_path)
