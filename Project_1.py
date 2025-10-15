import unittest
import os
import csv
#calculation fuctions

import os
import csv

def csv_to_filtered_list(path, convert_profit=True):
    #includes repeating postal codes --> the function returns a list of dicts, each dict is one row
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
        # find best header names for each wanted key (case-insensitive, partial match)
        mapping = {}
        low_headers = [h.lower() if h is not None else '' for h in headers]
        for want in wanted_keys:
            found = None
            for h in headers:
                if h and want in h.lower():
                    found = h
                    break
            if not found:
                # try exact match ignoring spaces/case
                for h in headers:
                    if h and h.strip().lower() == want:
                        found = h
                        break
            if not found:
                raise ValueError(f"Could not find column for '{want}' in headers: {headers}")
            mapping[want] = found

        for row in reader:
            # skip completely empty rows
            if not any((v or '').strip() for v in row.values()):
                continue
            postal = (row.get(mapping['postal']) or '').strip()
            category = (row.get(mapping['category']) or '').strip()
            profit_raw = (row.get(mapping['profit']) or '').strip()

            # skip rows missing postal/category/profit
            if postal == '' and category == '' and profit_raw == '':
                continue

            # parse profit if requested
            if convert_profit:
                pr = profit_raw.replace('$', '').replace(',', '')
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


def avg_profit_by_postal(consumer):
    rows = csv_to_filtered_list(path, convert_profit=True)
    totals = {}
    counts = {}
    for r in rows:
        p = r['Postal Code']
        profit = r['Profit']
        if profit is None or p == '':
            continue
        totals[p] = totals.get(p, 0.0) + profit
        counts[p] = counts.get(p, 0) + 1
    return {p: round(totals[p]/counts[p], 2) for p in totals}
# result example: {'12345': 123.45, '67890': 50.00}

#def Find_postal_max_furniture(consumer,money):

#def Find_postal_min_furniture(consumer,money):

#def Generate_report(min, max):
    

#four test cases
    class TestSuperstore(unittest.TestCase):
        def setUp(self):
            self.store_dict = load_superstore('Superstore.csv')

        def test_placeholder(self):
            # example assertion to make this a real test
            self.assertIsInstance(self.store_dict, (list, dict))

if __name__ == "__main__":
    unittest.main(verbosity=2)