import pandas as pd
import numpy as np

def excel2df(sem1_path=".\\sem1.csv",sem2_path=".\\sem2.csv")->pd.DataFrame:
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

def df_filter(sem,department)->dict:
    sem = 1 if str(sem)=='1' else 2
    department = [i.upper() for i in department]
    df = excel2df(".\\sem1.csv",".\\sem2.csv")
    df = df[df['sem']==sem]
    df = df[['Subject Code','Subject Title']]
    ret = {}
    for i in department:
        tmp = df[df['Subject Code'].str.contains(i)]
        ret[i] = tmp['Subject Code'].str.cat(tmp['Subject Title'],sep=" - ").drop_duplicates().to_list()
    return ret

def class_filter(sem,subject)->dict:
    sem = 1 if str(sem)=='1' else 2
    subject = subject.upper()
    df = excel2df(".\\sem1.csv",".\\sem2.csv")
    df = df[df['sem']==sem]
    df = df[['Subject Code','Component Code']]
    df = df[df['Subject Code'] == subject]
    tmp = df['Component Code'].drop_duplicates().to_list()
    tmp.sort()
    return {"code":subject,"component":tmp}


def check_day_conflict(time:list,start:int,end:int)->bool:
    if end<start:
        return False
    if len(time)==0:
        return True
    time = time.copy()
    time.append((start,0))
    time.append((end,1))
    time.sort(key = lambda t: t[1], reverse=True)
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
    time_table = {i:[] for i in ['Mon','Tue','Thu','Wed','Sat','Sun','Fri']} if forbid == None else forbid
    gen_permutation([],course_permutation,course_info,time_table,ans)
    return ans

def get_perfect_plan1(data:pd.DataFrame,limit:dict):
    course = list(limit.keys())
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
    has_limit = False
    for key in limit.keys():
        forbid = limit[key]['forbid']
        fixed = limit[key]['fixed']
        # del forbid item
        for i in forbid:
            has_limit = True
            component = i[:3]
            if course_info[(key,component)] == None:
                return False,"unmatched data"
            for j in range(len(course_info[(key,component)])):
                if course_info[(key,component)][j][2] == i:
                    del course_info[(key,component)][j]
                    break
            # if no class in the section, err
            if len(course_info[(key,component)]) == 0:
                return False,"You can't forbid all class in {} {}".format(key,component)
        # if fixed!=0, del not in fixed
        if len(fixed)!=0:
            has_limit = True
            for i in fixed:
                component = i[:3]
                if course_info[(key,component)] == None:
                    return False,"unmatched data"
                tmp = []
                for j in range(len(course_info[(key,component)])):
                    if course_info[(key,component)][j][2] == i:
                        tmp.append(course_info[(key,component)][j])
                course_info[(key,component)] = tmp
    ans = []
    time_table = {i:[] for i in ['Mon','Tue','Thu','Wed','Sat','Sun','Fri']} 
    gen_permutation([],course_permutation,course_info,time_table,ans)
    if len(ans) == 0 and has_limit:
        return False,"There is no non-conflicting solution, please try to reduce the conditions."
    if len(ans) == 0:
        return False,"There is no non-conflicting plan, please try to replace other course combinations."
    return True,ans


def detailed(df:pd.DataFrame,idx:list,sem:int):
    
    print(df)
    return df[df['index'].isin(idx)]

# def limit_solve_test():
#     df = excel2df(".\\sem1.csv",".\\sem2.csv")
#     df = df[['index','Subject Code','Subject Title','Component Code','Day of Week','Start Time','End Time','sem']]
#     ['COMP4434','COMP3421','COMP3334','COMP3511','AMA2112','COMP3021','AMA364']
#     limit = {
#         'COMP4434':{'forbid':[],'fixed':[]},
#         'COMP3421':{'forbid':[],'fixed':[]},
#         'COMP3334':{'forbid':[],'fixed':[]},
#         'COMP3511':{'forbid':[],'fixed':[]},
#         'AMA2112':{'forbid':[],'fixed':[]},
#         'COMP3021':{'forbid':[],'fixed':[]},
#         'AMA364':{'forbid':[],'fixed':[]},

#     }
#     stat,ans= get_perfect_plan1(df,limit,sem=2)
#     ans = detailed(df,ans[0],2)
#     return ans.T.to_dict()

def limit_solve(sem,limit):
    df = excel2df(".\\sem1.csv",".\\sem2.csv")
    sem = 1 if str(sem)=='1' else 2
    df = df[['index','Subject Code','Subject Title','Component Code','Day of Week','Start Time','End Time','sem']]
    df = df[df['sem']==sem]
    stat,ans= get_perfect_plan1(df,limit)
    if stat:
        ans = df[df['index'].isin(ans[0])].T.to_dict()
    return {'solve':stat,'result':ans}


def test():
    df = excel2df(".\\sem1.csv",".\\sem2.csv")
    df = df[['index','Subject Code','Subject Title','Component Code','Day of Week','Start Time','End Time','sem']]
    forbid = {i:[(0,0),(830,1)] for i in ['Mon','Tue','Thu','Wed','Sat','Sun','Fri']}
    ans= get_perfect_plan(df,['COMP4434','COMP3421','COMP3334','COMP3511','AMA2112','COMP3021','AMA364'],forbid,sem=2)
    ans = detailed(df,ans[0],2)
    return ans


if __name__ == "__main__":
    limit_solve_test()