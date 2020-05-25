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
    df['Start Time'] = df['Start Time'].map(lambda x:int(str(x).replace(":","")))
    df['End Time'] = df['End Time'].map(lambda x:int(str(x).replace(":","")))

    return df

def check_day_conflict(time:list,start:int,end:int)->bool:
    if end<start:
        return False
    if len(time)==0:
        return True
    time = time.copy()
    time.append((start,0))
    time.append((end,1))
    time.sort(key = lambda t: t[1])
    time.sort(key = lambda t: t[0])
    cur = 0
    for time,op in time:
        if op == 0:
            # start
            cur+=1
        else:
            #op == 1 end
            cur-=1
        if not (cur==0 or cur == 1):
            return False
    return cur==0

def gen_permutation(cur_sol:list,course_list:list,course_info:dict,time_record: dict,ans:list)->None:
    cur_idx = len(cur_sol)
    if cur_idx >= len(course_list):
        ans.append(cur_sol.copy())
        return
    cur = course_list[cur_idx]
    for info in course_info[cur]:
        idx,_,_,day,start,end = info
        if check_day_conflict(time_record[day],start,end):
            time_record[day].append((start,0))
            time_record[day].append((end,1))
            cur_sol.append(idx)
            gen_permutation(cur_sol,course_list,course_info,time_record,ans)
            cur_sol.remove(idx)
            time_record[day].remove((start,0))
            time_record[day].remove((end,1))
    return
        

def get_perfect_plan(data:pd.DataFrame,course:list,forbid:dict,sem = 1):
    data = data[data['sem']==sem]
    course_info = {}
    course_permutation = []
    for course_code in course:
        info = data[data['Subject Code']==course_code]
        info = info[['index','Subject Code','Component Code','Day of Week','Start Time','End Time']]
        for row in info.itertuples(index=False):
            index,code,component,day,start,end = row
            if (course_code,component[:3]) not in course_permutation:
                course_permutation.append((course_code,component[:3]))
                course_info[(course_code,component[:3])] = [tuple(row)]
            else:
                course_info[(course_code,component[:3])].append(tuple(row))
    ans = []
    time_table = {i:[] for i in ['Mon','Tue','Thu','Wed','Sat','Sun','Fri']}
    gen_permutation([],course_permutation,course_info,time_table,ans)
    # debug 
    # print("course")
    # for i in course_info:
        # print(i)
    # print("Sol")
    # t  = [" ".join(i) for i in course_permutation]
    # print("\t".join(t))
    # for i in ans:
        # t = [str(j) for j in i]
        # print("\t\t".join(t))
    return ans
        

if __name__ == "__main__":
    df = excel2df(".\\sem1.csv",".\\sem2.csv")
    get_perfect_plan(df,['COMP3511','COMP3021','COMP4434'],{},sem=2)