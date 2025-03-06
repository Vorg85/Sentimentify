import csv

input_file = 'sample.csv'
output_file = 'sample1.csv'

with open(input_file, mode='r', newline='', encoding='utf-8') as infile, \
    open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
    
    reader = csv.DictReader(infile)
    fieldnames = ['text', 'sentiment']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    
    writer.writeheader()
    for row in reader:
       writer.writerow({field: row[field] for field in fieldnames})