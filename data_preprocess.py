import pandas as pd
import numpy as np

def excel2df(sem1_path:str,sem2_path:str)->pd.DataFrame:
    with open(sem1_path,'r') as o:
        sem1 = pd.read_csv(o)
    with open(sem2_path,'r') as o:
        sem2 = pd.read_csv(o)
    sem1['sem'] = 1
    sem2['sem'] = 2
    df = pd.concat([sem1,sem2]).reset_index()

    df.drop_duplicates(inplace=True)
    df.drop(df[df['Subject Code']== 'Subject Code'].index,inplace = True)
    df.drop(df[pd.isna(df['Day of Week'])].index,inplace = True)
    return df


def get_perfect_plan(data:pd.DataFrame,course:list,forbid:dict,sem = 1):
    data = data[data['sem']==sem]
    # gen all class's permutation
    course_info = {}
    course_permutation = {}
    for course_code in course:
        info = data[data['Subject Code']==course_code]
        info = info[['index','Subject Code','Component Code','Day of Week','Start Time','End Time']]
        component_type = []
        for row in info.itertuples(index=False):
            index,code,component,day,start,end = row
            if component[:3] not in component_type:
                component_type.append(component[:3])
            course_info[code] = [index,component,day,start,end]
        # gen permutation
        

if __name__ == "__main__":
    df = excel2df(".\\sem1.csv",".\\sem2.csv")
    get_perfect_plan(df,['COMP3511','COMP3021','COMP4434'],{},sem=2)