#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
from utils import resource_path

class SimpleDataFrame:
    def __init__(self, data, columns):
        self.data = data
        self.columns = columns
        self._column_index = {col: i for i, col in enumerate(columns)}
    
    def __len__(self):
        return len(self.data)
    
    def __iter__(self):
        for row in self.data:
            yield dict(zip(self.columns, row))
    
    def loc(self, condition_func):
        result_data = []
        for row in self.data:
            row_dict = dict(zip(self.columns, row))
            if condition_func(row_dict):
                result_data.append(row)
        return SimpleDataFrame(result_data, self.columns)
    
    def get(self, key, default=None):
        if key in self._column_index:
            col_idx = self._column_index[key]
            return [row[col_idx] for row in self.data]
        return default
    
    def iterrows(self):
        for i, row in enumerate(self.data):
            row_dict = dict(zip(self.columns, row))
            yield i, row_dict

def notna(value):
    return value is not None and value != '' and str(value).strip() != ''

def load_csv_data(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        columns = next(reader)
        columns = [col.strip('\ufeff') for col in columns]
        for row in reader:
            data.append(row)
    return SimpleDataFrame(data, columns)
