"""
Simple BMI Checker Chat Bot
Run with: python bmi_bot.py

This script runs an interactive command-line chatbot that:
- calculates BMI and category
- estimates TDEE using Mifflin-St Jeor
- creates a calorie plan for safe weight loss
- provides general health tips

Not medical advice. Consult a healthcare professional for personalized guidance.
"""
from typing import Optional

ACTIVITY_LEVELS = {
    "1": ("sedentary (little or no exercise)", 1.2),
    "2": ("lightly active (light exercise 1-3 days/week)", 1.375),
    "3": ("moderately active (moderate exercise 3-5 days/week)", 1.55),
    "4": ("very active (hard exercise 6-7 days/week)", 1.725),
    "5": ("extra active (very hard exercise / physical job)", 1.9),
}


def safe_float_input(prompt: str) -> float:
    """Simple positive float input with retry. Keeps backward-compatible behavior."""
    while True:
        val = input(prompt).strip()
        try:
            f = float(val)
            if f <= 0:
                raise ValueError()
            return f
        except ValueError:
            print("Please enter a positive number (e.g. 70 or 70.5).")


# New helpers: support weight in kg or lb and height in cm or ft/in

def parse_weight(prompt: str) -> float:
    """Ask for weight and return kilograms. Accepts values like '70', '70 kg', '154 lb'."""
    while True:
        raw = input(prompt + " (e.g. 70 kg or 154 lb): ").strip().lower()
        if not raw:
            print("Please enter your weight.")
            continue
        try:
            # allow formats: '70', '70kg', '70 kg', '154 lb'
            raw = raw.replace('kgs','kg').replace('lbs','lb')
            parts = raw.replace(',', '.').split()
            if len(parts) == 1:
                # maybe '70kg' or just '70'
                token = parts[0]
                # separate digits and letters
                num = ''
                unit = ''
                for ch in token:
                    if (ch.isdigit() or ch == '.'):
                        num += ch
                    else:
                        unit += ch
                val = float(num)
                unit = unit or 'kg'
            else:
                val = float(parts[0])
                unit = parts[1]
            if unit.startswith('k'):
                kg = val
            elif unit.startswith('l'):
                kg = val * 0.45359237
            else:
                print("Unknown unit; use 'kg' or 'lb'.")
                continue
            if kg <= 0:
                print("Weight must be positive.")
                continue
            return round(kg, 2)
        except Exception:
            print("Couldn't parse weight. Examples: '70', '70 kg', '154 lb'.")


def parse_height(prompt: str) -> float:
    """Ask for height and return centimetres. Accepts '170', '170 cm', '5 ft 9 in', '5'9"', '5ft9'."""
    while True:
        raw = input(prompt + " (e.g. 170 cm or 5 ft 9 in): ").strip().lower()
        if not raw:
            print("Please enter your height.")
            continue
        try:
            raw = raw.replace('"', ' in').replace("'", ' ft ').replace('feet', 'ft').replace('meter', 'm')
            raw = raw.replace('cms', 'cm')
            parts = raw.replace(',', '.').split()
            # simple numeric cm: '170' or '170 cm'
            if len(parts) == 1 or (len(parts) == 2 and parts[1].startswith('c')):
                num = float(parts[0])
                if len(parts) == 1 and num < 3:  # maybe meters like 1.7
                    cm = num * 100
                elif len(parts) == 1 and num <= 3:  # e.g. '1.75' meters
                    cm = num * 100
                else:
                    cm = num
                return round(cm, 1)

            # ft/in formats: look for 'ft' and 'in'
            ft = None
            inch = 0.0
            if 'ft' in raw or 'foot' in raw:
                # extract numbers
                tokens = raw.replace('ft', ' ft ').replace('in', ' in ').split()
                for i, t in enumerate(tokens):
                    if t == 'ft' and i > 0:
                        ft = float(tokens[i-1])
                    if t == 'in' and i > 0:
                        inch = float(tokens[i-1])
            else:
                # try patterns like '5 9' or '5'9' converted earlier
                nums = [p for p in parts if all(c.isdigit() or c == '.' for c in p)]
                if len(nums) >= 2:
                    ft = float(nums[0])
                    inch = float(nums[1])
            if ft is not None:
                cm = ft * 30.48 + inch * 2.54
                return round(cm, 1)

            print("Couldn't parse height. Use '170 cm' or '5 ft 9 in' or '1.75 m'.")
        except Exception:
            print("Couldn't parse height. Examples: '170 cm', '5 ft 9 in', '1.75 m'.")


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    height_m = height_cm / 100.0
    bmi = weight_kg / (height_m * height_m)
    return round(bmi, 1)


def bmi_category(bmi: float) -> str:
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 25:
        return "Normal (healthy weight)"
    elif 25 <= bmi < 30:
        return "Overweight"
    else:
        return "Obesity"


def bmr_mifflin_sex(weight: float, height_cm: float, age: int, sex: str) -> float:
    # sex: 'male' or 'female' (case-insensitive); 'other' will use average of male/female
    s = sex.lower()
    if s.startswith('m'):
        bmr = 10 * weight + 6.25 * height_cm - 5 * age + 5
    elif s.startswith('f'):
        bmr = 10 * weight + 6.25 * height_cm - 5 * age - 161
    else:
        # average of male and female formulas
        bmr_m = 10 * weight + 6.25 * height_cm - 5 * age + 5
        bmr_f = 10 * weight + 6.25 * height_cm - 5 * age - 161
        bmr = (bmr_m + bmr_f) / 2
    return bmr


def estimate_tdee(weight: float, height_cm: float, age: int, sex: str, activity_key: str) -> float:
    bmr = bmr_mifflin_sex(weight, height_cm, age, sex)
    multiplier = ACTIVITY_LEVELS.get(activity_key, (None, 1.2))[1]
    tdee = bmr * multiplier
    return round(tdee)


# New: recommend macronutrients based on activity and goal

def recommend_macros(suggested_calories: int, weight_kg: float, activity_key: str) -> dict:
    # protein: 1.6 g/kg for sedentary up to 2.2 g/kg for very active
    activity_to_protein = {
        "1": 1.6,
        "2": 1.6,
        "3": 1.8,
        "4": 2.0,
        "5": 2.2,
    }
    protein_g_per_kg = activity_to_protein.get(activity_key, 1.6)
    protein_g = round(protein_g_per_kg * weight_kg)
    protein_kcal = protein_g * 4

    # fat: 25-30% of calories (use 28%)
    fat_pct = 0.28
    fat_kcal = suggested_calories * fat_pct
    fat_g = round(fat_kcal / 9)

    # carbs: remaining calories
    remaining_kcal = suggested_calories - (protein_kcal + fat_kcal)
    carb_g = max(round(remaining_kcal / 4), 0)

    return {
        'protein_g': protein_g,
        'fat_g': fat_g,
        'carb_g': carb_g,
        'protein_kcal': int(protein_kcal),
        'fat_kcal': int(fat_kcal),
        'carb_kcal': int(remaining_kcal if remaining_kcal>0 else 0),
    }


def recommend_calories_for_weight_loss(current_weight: float, target_weight: float, tdee: float, days: int, sex: str) -> dict:
    # 1 kg fat ~= 7700 kcal
    kg_to_lose = current_weight - target_weight
    if kg_to_lose <= 0:
        return {"message": "Target weight is not less than current weight. No calorie deficit needed."}

    total_kcal_needed = kg_to_lose * 7700
    daily_deficit = total_kcal_needed / max(days, 1)

    # Safety caps
    max_safe_deficit = 1000  # kcal/day
    weekly_loss_kg = (daily_deficit * 7) / 7700
    if daily_deficit > max_safe_deficit:
        # if unrealistic, recommend using the max safe deficit and compute new timeframe
        warning = "Required deficit exceeds common safety recommendations; using max safe deficit of 1000 kcal/day. Consider a longer timeframe or consult a professional."
        daily_deficit = max_safe_deficit
        suggested_daily = tdee - daily_deficit
        est_weeks_needed = (kg_to_lose * 7700) / (daily_deficit * 7)
    else:
        warning = None
        suggested_daily = tdee - daily_deficit
        est_weeks_needed = days / 7

    # Minimum recommended daily calories (very general); always consult a pro
    min_cal = 1200
    if suggested_daily < min_cal:
        suggested_daily = min_cal
        warning_min = f"Calculated intake would fall below minimum recommended calories ({min_cal} kcal/day). Use caution and consult a professional."
    else:
        warning_min = None

    return {
        "kg_to_lose": round(kg_to_lose, 2),
        "total_kcal_needed": int(total_kcal_needed),
        "daily_deficit": int(daily_deficit),
        "suggested_daily_calories": int(suggested_daily),
        "warnings": [w for w in (warning, warning_min) if w],
        "weekly_loss_kg": round(weekly_loss_kg, 3),
        "estimated_weeks_needed": round(est_weeks_needed, 1),
    }


def print_health_tips():
    tips = [
        "Aim for 0.5–1 kg (1–2 lb) weight loss per week — it's safer and more sustainable.",
        "Prioritize protein and vegetables to stay full on fewer calories.",
        "Do a mix of resistance training and cardio — muscle helps raise metabolic rate.",
        "Get 7–9 hours of sleep per night; poor sleep increases hunger hormones.",
        "Stay hydrated and limit sugary drinks.",
        "Avoid extreme calorie restriction; consult a dietitian for personalized plans.",
    ]
    print("\nGeneral health tips:")
    for t in tips:
        print("-", t)
    print()


def menu():
    print("\nBMI Checker Bot")
    print("Options:\n 1) Check BMI\n 2) Create weight-loss calorie plan\n 3) Health tips\n 4) Exit")


def action_check_bmi():
    print("\n-- BMI Calculator --")
    weight = parse_weight("Enter weight")
    height = parse_height("Enter height")
    bmi = calculate_bmi(weight, height)
    category = bmi_category(bmi)
    print(f"\nYour BMI is {bmi} — {category}")

    # extra context
    if category == 'Underweight':
        print("Advice: If underweight, focus on nutritious calorie-dense foods and consider a medical check-up.")
    elif category == 'Normal (healthy weight)':
        print("Advice: Maintain balanced nutrition and regular activity to keep your healthy weight.")
    elif category == 'Overweight':
        print("Advice: A modest calorie deficit and increased activity can help. Aim for 0.5–1 kg per week.")
    else:
        print("Advice: For BMI in the obesity range, consult a healthcare professional for a personalized plan.")


def show_disclaimer_and_get_consent() -> bool:
    """Present a clear medical disclaimer and require explicit acknowledgement to run personalized plans.

    Returns True if the user types 'I AGREE' (case-insensitive)."""
    print("\nIMPORTANT — Read before using the calorie planner:")
    print("This tool provides general educational information only. It is NOT a medical diagnosis or a replacement for professional medical, nutritional, or psychiatric advice.")
    print("People who are pregnant or breastfeeding, under 18 years old, have a history of an eating disorder, or have serious medical conditions (heart disease, diabetes, etc.) should consult a healthcare professional before changing diet or exercise.")
    print("If you do not wish to accept these limits, you may still use the BMI calculator and general tips, but personalized calorie plans will be disabled.")
    resp = input("\nType 'I AGREE' to acknowledge and continue, or press Enter to continue without personalized plans: ").strip()
    return resp.upper() == 'I AGREE'


def action_plan(consent: bool = False):
    # If the user did not consent to the medical disclaimer, block personalized plans
    if not consent:
        print("\nPersonalized calorie plans are disabled because you did not acknowledge the disclaimer.")
        print("You can still use BMI calculation and general health tips. To enable plans, restart the program and type 'I AGREE' when prompted.")
        return

    print("\n-- Weight-loss calorie planner --")
    weight = parse_weight("Current weight")
    target = parse_weight("Target weight")
    age = int(safe_float_input("Age (years): "))

    # safety checks
    if age < 18:
        print("\nWarning: You are under 18. This tool is not suitable for children or adolescents. Please consult a pediatrician or registered dietitian.")
        return
    if age > 80:
        print("\nNote: For older adults (80+), metabolic estimates may be less accurate. Consult your doctor for personalized guidance.")

    sex = input("Sex (male/female/other): ").strip() or "other"

    # pregnancy/breastfeeding check — only ask where relevant
    if sex.lower().startswith('f'):
        preg = input("Are you pregnant or breastfeeding? (y/n): ").strip().lower()
        if preg.startswith('y'):
            print("\nBecause you are pregnant/breastfeeding, please consult an obstetrician or registered dietitian before making changes to calories or weight goals.")
            return

    med = input("Do you have any diagnosed medical condition that affects diet/exercise (e.g., diabetes, heart disease)? (y/n): ").strip().lower()
    if med.startswith('y'):
        print("\nBecause of your medical condition, personalized guidance from a clinician or registered dietitian is recommended. This tool cannot safely provide that level of personalization.")
        return

    height = parse_height("Height")

    print("Select activity level:")
    for k, v in ACTIVITY_LEVELS.items():
        print(f" {k}) {v[0]}")
    activity = input("Choose 1-5 (default 1): ").strip() or "1"

    tdee = estimate_tdee(weight, height, age, sex, activity)
    print(f"\nEstimated TDEE (calories/day to maintain current weight): {tdee} kcal")

    weeks = safe_float_input("Over how many weeks do you want to reach the target? ")
    days = int(max(1, round(weeks * 7)))
    plan = recommend_calories_for_weight_loss(weight, target, tdee, days, sex)

    if "message" in plan:
        print(plan["message"])
        return

    print(f"\nTo lose {plan['kg_to_lose']} kg (approx) in {plan['estimated_weeks_needed']} weeks:")
    print(f" - Total calories to lose: {plan['total_kcal_needed']} kcal")
    print(f" - Daily calorie deficit needed: {plan['daily_deficit']} kcal/day")
    print(f" - Suggested daily calorie intake: {plan['suggested_daily_calories']} kcal/day")
    print(f" - Estimated weekly loss (if followed): {plan['weekly_loss_kg']} kg/week")

    if plan['warnings']:
        print("\nWarnings:")
        for w in plan['warnings']:
            print("-", w)

    # macros
    macros = recommend_macros(plan['suggested_daily_calories'], weight, activity)
    print("\nSuggested daily macronutrients (approx):")
    print(f" - Protein: {macros['protein_g']} g ({macros['protein_kcal']} kcal)")
    print(f" - Fat: {macros['fat_g']} g ({macros['fat_kcal']} kcal)")
    print(f" - Carbs: {macros['carb_g']} g ({macros['carb_kcal']} kcal)")
    print()


def main():
    print("Welcome — this bot gives general guidance about BMI and calories. Not medical advice.")
    consent = show_disclaimer_and_get_consent()
    while True:
        menu()
        choice = input("Enter choice (1-4): ").strip()
        if choice == "1":
            action_check_bmi()
        elif choice == "2":
            action_plan(consent)
        elif choice == "3":
            print_health_tips()
        elif choice == "4" or choice.lower() in ("exit", "quit"):
            print("Goodbye — consult a healthcare professional for medical advice.")
            break
        else:
            print("Invalid choice — try again.")

if __name__ == "__main__":
    main()
