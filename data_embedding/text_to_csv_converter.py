import pandas as pd

import re
def remove_newlines(text):
    """
    
    """
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r' +', ' ', text)
    return text

def text_to_df(data_file):
    """
    
    """
    texts = []

    with open(data_file, 'r', encoding="utf-8") as file:
        text = file.read()
        sections =  text.split('\n\n')

        for section in sections:
            lines = section.split('\n')

            fname = lines[0]   
            content = ' '.join(lines[1:])
            texts.append([fname, content])

    df = pd.DataFrame(texts, columns=['fname', 'text'])
    df['text'] = df['text'].apply(remove_newlines)

    return df

        

df = text_to_df('data.txt')
df.to_csv('scraped.csv', index=False, encoding='utf-8')