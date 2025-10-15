import unittest
import os
import csv
import tempfile
#calculation fuctions

def csv_to_filtered_list(path, convert_profit=True):
    """
    Return a list of dicts with exactly the keys:
      'Postal Code', 'Category', 'Profit'
    Values are stripped strings; if convert_profit=True, Profit is a float.
    Raises ValueError if required columns are not found.
    """
    wanted_keys = {'postal': 'Postal Code', 'category': 'Category', 'profit': 'Profit'}

    base = os.path.abspath(os.path.dirname(__file__))
    full = os.path.join(base, path)

    out = []
    with open(full, newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        headers = reader.fieldnames or []

        # Map headers dynamically
        mapping = {}
        for want in wanted_keys:
            found = None
            for h in headers:
                if h and want in h.lower():
                    found = h
                    break
            if not found:
                for h in headers:
                    if h and h.strip().lower() == want:
                        found = h
                        break
            if not found:
                raise ValueError(f"Could not find column for '{want}' in headers: {headers}")
            mapping[want] = found

        for row in reader:
            # skip empty rows
            if not any((v or '').strip() for v in row.values()):
                continue

            postal = (row.get(mapping['postal']) or '').strip()
            category = (row.get(mapping['category']) or '').strip()
            profit_raw = (row.get(mapping['profit']) or '').strip()

            # skip missing data
            if postal == '' and category == '' and profit_raw == '':
                continue

            # parse profit safely
            if convert_profit:
                pr = profit_raw.replace('$', '').replace(',', '').strip()
                try:
                    profit_val = float(pr) if pr != '' else None
                except ValueError:
                    profit_val = None
            else:
                profit_val = profit_raw

            entry = {
                'Postal Code': postal,
                'Category': category,
                'Profit': profit_val if convert_profit else profit_raw
            }
            out.append(entry)
    return out


def avg_profit_by_postal(path):
    rows = csv_to_filtered_list(path, convert_profit=True)
    totals = {}
    counts = {}
    
    for r in rows:
        if r['Category'] != 'Furniture':  #ignores non furniture 
            continue
        p = r['Postal Code']
        profit = r['Profit']
        if profit is None or p == '': #if the profit is missing or if the postal code is missing --> skips
            continue
        totals[p] = totals.get(p, 0.0) + profit #adds the profit together for total profit
        counts[p] = counts.get(p, 0) + 1 #counts the number of times a postal code appears

    avg_dict = {p: round(totals[p] / counts[p], 2) for p in totals} #returns a seperate dictionary for each postal code and their average profit
    return avg_dict
    


# result example: {'12345': 123.45, '67890': 50.00}

def best_postal_by_avg(path):
    avg = avg_profit_by_postal(path)   # uses previous function
    if not avg: #if the dictionary is empty
        return None, None
    best = max(avg, key=avg.get)
    # return postal code and numeric average
    return best, avg[best]

def worst_postal_by_avg(path):
    avg = avg_profit_by_postal(path)
    if not avg:
        return None, None
    worst = min(avg, key=avg.get)
    return worst, avg[worst]

def worst_postals_by_avg(path):
    """Return list of (postal, avg) tied for the worst average."""
    avg = avg_profit_by_postal(path)
    if not avg:
        return []
    min_val = min(avg.values())
    return [(p, v) for p, v in avg.items() if v == min_val]

import os
import csv

def write_best_worst_to_csv(input_csv, out_csv):
    """
    Write best and worst average profit postal codes to out_csv (single winner each).
    - input_csv: path to the source Superstore CSV
    - out_csv: destination CSV path (overwritten)
    Output CSV columns: Type,Postal Code,Average Profit
    """
    avg = avg_profit_by_postal(input_csv)
    # ensure folder exists
    os.makedirs(os.path.dirname(out_csv) or ".", exist_ok=True)

    # if empty case, write header only
    if not avg:
        with open(out_csv, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["Type", "Postal Code", "Average Profit"])
        return

    # find best/worst
    values = list(avg.values())
    max_val = max(values)
    min_val = min(values)

    best_postal = max(avg, key=avg.get)
    worst_postal = min(avg, key=avg.get)
    best_items = [(best_postal, avg[best_postal])]
    worst_items = [(worst_postal, avg[worst_postal])]

    # write CSV
    with open(out_csv, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["Type", "Postal Code", "Average Profit"])
        for p, v in best_items:
            writer.writerow(["Best", p, f"{v:.2f}"])
        for p, v in worst_items:
            writer.writerow(["Worst", p, f"{v:.2f}"])

#four test cases
#test case for filtered list function 
class TestFilteredCSV(unittest.TestCase):
    def test_filtered(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='', encoding='utf-8') as t:
            t.write("Postal Code,Category,Profit,Other\n")
            t.write("11111,Furniture,$100.00,x\n")
            t.write("11111,Furniture,$200.00,y\n")
            t_path = t.name
        try:
            rows = csv_to_filtered_list(t_path)
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]['Postal Code'], '11111')
            self.assertEqual(rows[0]['Category'], 'Furniture')
            self.assertAlmostEqual(rows[0]['Profit'], 100.00)
        finally:
            os.unlink(t_path)

#test case for average profit function
class TestAvgProfitByPostal(unittest.TestCase):
    def test_avg_profit(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='', encoding='utf-8') as t:
            t.write("Postal Code,Category,Profit,Other\n")
            t.write("11111,Furniture,$100.00,x\n")
            t.write("11111,Furniture,$200.00,y\n")
            t.write("22222,Office Supplies,$50.00,z\n")
            t.write("33333,Technology,,a\n")  # missing profit
            t.write("44444,Furniture,$-20.00,b\n")  # negative profit
            t_path = t.name
        try:
            result = avg_profit_by_postal(t_path)
            self.assertEqual(result['11111'], 150.00)
            self.assertEqual(result['22222'], 50.00)
            self.assertEqual(result['44444'], -20.00)
            self.assertNotIn('33333', result)  # missing profit should be skipped
        finally:
            os.unlink(t_path)

#test case for best postal by average profit function:
class TestMaxProfitByPostal(unittest.TestCase):
    def test_single_best_postal(self):
        # postal 22222 has average 500.00 (single best)
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='', encoding='utf-8') as t:
            t.write("Postal Code,Category,Profit,Other\n")
            t.write("11111,Furniture,$100.00,x\n")
            t.write("11111,Furniture,$200.00,x\n")
            t.write("22222,Furniture,$500.00,x\n")
            t.write("33333,Office,$1000.00,x\n")   # non-Furniture should be ignored by avg routine
            path = t.name
        try:
            postal, avg = best_postal_by_avg(path)
            self.assertEqual(postal, '22222')
            self.assertEqual(avg, 500.00)
        finally:
            os.unlink(path)

#test case for worst postal by average profit function:
class TestWorstPostalByAvg(unittest.TestCase):
    def test_single_worst_postal(self):
        # 11111 avg=150, 22222 avg=50 (worst), 33333 ignored or higher
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='', encoding='utf-8') as t:
            t.write("Postal Code,Category,Profit\n")
            t.write("11111,Furniture,$100.00\n")
            t.write("11111,Furniture,$200.00\n")
            t.write("22222,Furniture,$50.00\n")
            t.write("22222,Furniture,$50.00\n")
            t.write("33333,Office,$1000.00\n")  # non-Furniture may be ignored depending on your loader
            path = t.name
        try:
            postal, avg = worst_postal_by_avg(path)
            self.assertEqual(postal, '22222')
            self.assertEqual(avg, 50.00)
        finally:
            os.unlink(path)

if __name__ == '__main__':
    unittest.main(verbosity=2)