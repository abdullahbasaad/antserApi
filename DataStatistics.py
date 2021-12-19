import statistics
import pandas as pd


class DataStat:

    def get_data_stat(df, file_name):
        try:
            skew = df.skew(axis=0, skipna=True, numeric_only=True).to_string().strip()
            DATDICREF = {'Number of Rows:': df.shape[0], 
                        'Number of Columns:': df.shape[1], 
                        'Data set Shape:': df.shape,
                        'File Source:': file_name[:file_name.index('.')], 
                        'File Type:': file_name[file_name.index('.') + 1:file_name.index('.') + 1 + len(file_name) - file_name.index('.') - 1],
                        'Data Skewness:': skew}
        except ValueError:
            print('Dataset parsing error..')
        return DATDICREF
    
    def get_cat_stat(df, k):
        CATDICREF = {k: ['Total Rows: ' + str(df.shape[0]),
                         'Unique: ' + str(len(df[k].dropna().unique())),
                         'Groups: ' + str(df[k].dropna().unique())]}
        return CATDICREF

    def get_obj_stat(df, k):
        try:
            mostfreq = df[k].value_counts().idxmax()
            freq = len([x for x in df[k] if x == mostfreq])
            OBJDICREF = {k: ['Total Rows: ' + str(df.shape[0]),
                            'Missing Values: ' + str(sum(pd.isnull(df[k]))),
                            '% Missing: ' + str(round(sum(pd.isnull(df[k])) / len(df[k]) * 100, 2)),
                            'Most Frequent: ' + str(df[k].value_counts().idxmax()),
                            'Frequency: ' + str(freq)]}
        except ValueError:
            print('Object data parsing error..')
        return OBJDICREF

    # Method to collect different numeric statistics
    def get_num_stat(df, k):
        try:
            outliers = df[df[k] > df[k].mean() + 3 * df[k].std()]
            mostfreq = df[k].value_counts().idxmax()
            freq = len([x for x in df[k] if x == mostfreq])
            NUMDICREF = {k: ['Total Rows: ' + str(df.shape[0]),
                            'Missing Values: ' + str(sum(pd.isnull(df[k]))),
                            '% Missing :' + str(round(sum(pd.isnull(df[k])) / len(df[k]) * 100, 4)),
                            'Most Frequent ' + str(df[k].value_counts().idxmax()),
                            'Frequency: ' + str(freq),
                            'Min: ' + str(df[k].min()),
                            'Max: ' + str(df[k].max()),
                            'Mean: ' + str(round(df[k].mean(), 4)),
                            'Median: ' + str(df[k].median()),
                            'Mode: ' + str(statistics.mode(df[k])),  # str(df[k].mode()),
                            'Sum: ' + str(df[k].sum()),
                            'Std: ' + str(round(df[k].std(), 4)),
                            'Var: ' + str(round(df[k].var(), 4)),
                            '25%: ' + str(df[k].quantile(0.25)),
                            '50%: ' + str(df[k].quantile(0.5)),
                            '75%: ' + str(df[k].quantile(0.75)),
                            'Outliers: ' + str(len(outliers))]}
        except ValueError:
            print('Numaric data parsing error..')
        return NUMDICREF
