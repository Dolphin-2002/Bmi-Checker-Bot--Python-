Created by copyright @ Danussuthan 2025
```markdown
BMI Checker Bot

Simple command-line helper that:
...


 BMI Checker Bot

Simple command-line helper that:
- Calculates your BMI and tells you the category (underweight, normal, overweight, obesity).
- Estimates daily calories to maintain your weight (TDEE).
- Suggests a safe calorie plan and simple macronutrient targets (protein/fat/carbs) for weight loss.
- Gives general health tips.

Important: This is educational only — not medical advice. People who are pregnant, breastfeeding, under 18, have a history of eating disorders, or have serious medical conditions should consult a healthcare professional before changing diet or exercise.

How to use (non-technical)
1. Open a terminal or Command Prompt.
2. Run the program:
   - On Windows: `python bmi_bot.py`
   - On Debian / Linux: `python3 bmi_bot.py`
3. Follow the prompts. The program will ask for:
   - Weight (you can type examples like `70`, `70 kg`, or `154 lb`)
   - Height (you can type `170`, `170 cm`, `5 ft 9 in`, or `1.75 m`)
   - Age and sex
   - Activity level (pick the option that best matches how active you are)
4. At start you’ll see a short disclaimer. Type `I AGREE` to enable the calorie planner; otherwise you can still use BMI and general tips.
5. Choose:
   - “Check BMI” to see your BMI and simple advice.
   - “Create weight-loss calorie plan” to get a TDEE estimate, suggested daily calories for a safe deficit, and basic macro targets.
   - “Health tips” for general, practical suggestions.

Example interactions (what to expect)
- BMI check: enter weight and height → you’ll get BMI number + simple advice (e.g., “Maintain balanced nutrition”).
- Calorie plan: enter current and target weight, weeks to reach goal → you’ll see the calories you’d need to eat each day (the script uses conservative safety caps and warns if a plan looks unsafe).

Friendly notes
- The tool uses common formulas and estimates — results are approximate.
- If the calculated calorie intake looks very low or the deficit is very large, the program will warn you or suggest a longer timeline.
- Use common sense: combine healthy eating, strength/cardio exercise, good sleep and hydration.

