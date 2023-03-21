import re
from IPython.utils import text as text_utils

def remove_colorama_codes(text):
    # Remove colorama escape codes from the string
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

# Run the command and store the output
#output_txt = !python3 main.py -A -odds=betmgm
import subprocess

output_txt = subprocess.run(["python3", "main.py", "-A", "-odds=betmgm"], capture_output=True, text=True)



# Convert SList to a string
output_txt_str = text_utils.SList(output_txt).nlstr

clean_output = remove_colorama_codes(output_txt_str)
#print(clean_output)

# Define patterns to match the start of each section
#xgboost_start_pattern = r"---------------XGBoost Model Predictions---------------"
#nn_start_pattern = r"------------Neural Network Model Predictions-----------"
nn_start_pattern = r"ms/step"
nn_end_pattern = r"nnnend-------------------------------------------------"
xgboost_start_pattern = r"---------------XGBoost Model Predictions---------------"
xgboost_end_pattern = r"xgbend-------------------------------------------------"
odds_start_pattern = r" odds data------------------"
xgb_OUstart_pattern = r"---------------XGBoost Model Predictions---------------"
nn_OUstart_pattern = r"ms/step"

# Find the start of each section
xgboost_start = re.search(xgboost_start_pattern, clean_output).start()
xgboost_end = re.search(xgboost_end_pattern, clean_output).start()
nn_start = re.search(nn_start_pattern, clean_output).start()
nn_end = re.search(nn_end_pattern, clean_output).start()
odds_start = re.search(odds_start_pattern, clean_output).start()
xgb_OUstart = re.search(xgb_OUstart_pattern, clean_output).start()
nn_OUstart = re.search(nn_OUstart_pattern, clean_output).start()

# Extract the text for each section
xgboost_text = clean_output[xgboost_start:xgboost_end].strip()
nn_text = clean_output[nn_start:nn_end].strip()
odds_text = clean_output[odds_start:xgb_OUstart].strip()

# Print each section
#print("xgboost_text:\n", xgboost_text)
#print("nn_text:\n", nn_text)
#print("odds_text:\n", odds_text)

import re
from collections import defaultdict
from datetime import datetime

# Helper function to extract values
def extract_values(text, pattern):
    return {m.group(1): float(m.group(2)) for m in re.finditer(pattern, text)}

def merge_dicts(dict1, dict2):
    result = dict1.copy()
    for key, value in dict2.items():
        if key not in result:
            result[key] = value
    return result

# Extract EVs and betting percentages
xgboost_ev = extract_values(xgboost_text, r"(\w+ \w+) EV: ([-\d.]+)")
nn_ev = extract_values(nn_text, r"(\w+ \w+) EV: ([-\d.]+)")

# Extract OVER and UNDER values from xgboost_text
xgboost_over = extract_values(xgboost_text, r"(\w+ \w+ vs \w+ \w+) \(([\d.]+)%\): OVER \d+\.\d+ \(([\d.]+)%\)")
xgboost_over3 = extract_values(xgboost_text, r"((?:\w+ ){1,2}\w+ \([\d.]+%\) vs (?:\w+ ){1,2}\w+: OVER \d+\.\d) \(([\d.]+)%\)")
xgboost_under = extract_values(xgboost_text, r"(\w+ \w+ \([\d.]+%\) vs \w+ \w+: UNDER \d+\.\d) \(([\d.]+)%\)")
xgboost_under3 = extract_values(xgboost_text, r"((?:\w+ ){1,2}\w+ \([\d.]+%\) vs (?:\w+ ){1,2}\w+: UNDER \d+\.\d) \(([\d.]+)%\)")

xgboost_over = merge_dicts(xgboost_over, xgboost_over3)
xgboost_under = merge_dicts(xgboost_under, xgboost_under3)

# Calculate average EVs
average_ev = {team: (xgboost_ev[team] + nn_ev[team]) / 2 for team in xgboost_ev}

# Filter and sort top 3 teams by EV
top_xgboost_teams = sorted([(team, ev) for team, ev in xgboost_ev.items() if ev > 10], key=lambda x: x[1], reverse=True)[:4]
top_nn_teams = sorted([(team, ev) for team, ev in nn_ev.items() if ev > 10], key=lambda x: x[1], reverse=True)[:4]

# Extract moneyline odds
moneyline_odds = {m.group(1): m.group(2) for m in re.finditer(r"(\w+ \w+) \(([-\d]+)\)", odds_text)}

# Extract games with end-of-line percentage > 62%
xgboost_over_under_62 = [(game, perc) for game, perc in {**xgboost_over, **xgboost_under}.items() if perc > 62]

# Print output
today_date = datetime.now().strftime("%m/%d/%y")
print(today_date)
print()
bet = 25
total_payouts = []

print("MoneyLine Games to Bet:")
for team, ev in sorted(average_ev.items(), key=lambda x: x[1], reverse=True)[:4]:
    if team in moneyline_odds:
        odds = int(moneyline_odds[team])
        payout = bet * abs(odds) / 100 if odds > 0 else bet * 100 / abs(odds)
        total_payouts.append(payout)
        print(f"{team} ({moneyline_odds[team]}) EV: {ev:.4f} Payout: ${payout:.2f}")

total_payout_sum = sum(total_payouts)
print(f"\nBetting Summary: ${bet} each for Total Payout of ${total_payout_sum:.2f}")
print()

print(f"XGBoost Over/Under:")
for game, perc in xgboost_over_under_62:
    print(f"{game} PercentConfidence: {perc:.1f}")
print()

print("XGBoost Model Predictions Summary:")
for team, ev in top_xgboost_teams:
    print(f"{team} EV: {ev:.2f}")
print()
print("NNN Model Predictions Summary:")
for team, ev in top_nn_teams:
    print(f"{team} EV: {ev:.2f}")
