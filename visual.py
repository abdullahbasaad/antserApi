# import seaborn as sns
# import matplotlib.pyplot as plt
# carrier_count = cat_df_flights['carrier'].value_counts()
# sns.set(style="darkgrid")
# sns.barplot(carrier_count.index, carrier_count.values, alpha=0.9)
# plt.title('Frequency Distribution of Carriers')
# plt.ylabel('Number of Occurrences', fontsize=12)
# plt.xlabel('Carrier', fontsize=12)
# plt.show()


# labels = cat_df_flights['carrier'].astype('category').cat.categories.tolist()
# counts = cat_df_flights['carrier'].value_counts()
# sizes = [counts[var_cat] for var_cat in labels]
# fig1, ax1 = plt.subplots()
# ax1.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True) #autopct is show the % on plot
# ax1.axis('equal')
# plt.show()

import pandas as pd
df= pd.read_csv('Titanic.csv')

#print(df.select_dtypes(include=['category','int','float']).dtypes)

#print(df.head)
#print((df['Age'].size - len(df['Age'].unique())) / df['Age'].size * 100) 
      
print(len(df['Embarked'].dropna().unique()))

#print(df['Survived'].values.ravel())

#print(df['Survived'].unique().sum())