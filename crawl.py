import sys, os
import shutil, errno
import datetime

os.chdir("D:\\Luko\\emacs\\programavimas\\Projektas\\CTVparsingas")
import CMDparsing
from CMDparsing import AlgError, MatchError, ParseError, EOSError

working_dir='x:/conv_db'
my_dir='d:/luko/emacs/programavimas/Projektas/ChangeCompare/data/'
my_errors_dir=my_dir+'errors/'
my_stats_dir=my_dir+'stats/'



def get_publishers():
    '''Surenkami publisheriai esantys conv_db.'''
    leidyklos=[]
    leidyklos=[os.path.join(working_dir,leidykla)\
               for leidykla in os.listdir(working_dir)\
               if os.path.isdir(os.path.join(working_dir,leidykla))]
    return leidyklos



def get_list_of_projects():
    '''Grazina sarasa su leidyklom ir ju projektais.
    kiekvienas elementas yra sarasas projektu su tuo paciu
    leideju.'''
    leidyklos=get_publishers()
    projektai=[]
    for leidykla in leidyklos:
        projektai.append([os.path.join(leidykla,projektas)\
                          for projektas in os.listdir(leidykla)\
                          if os.path.isdir(os.path.join(leidykla,projektas))])
    return projektai

def get_elsa_projects():
    '''Grazina sarasa su leidyklom ir ju projektais.
    kiekvienas elementas yra sarasas projektu su tuo paciu
    leideju.'''
    leidyklos=['x:/conv_db\\esch',
                  'x:/conv_db\\esme',
                  'x:/conv_db\\esnl',
                  'x:/conv_db\\essd']
    projektai=[]
    for leidykla in leidyklos:
        projektai.append([os.path.join(leidykla,projektas)\
                          for projektas in os.listdir(leidykla)\
                          if os.path.isdir(os.path.join(leidykla,projektas))])
    return projektai

def get_issues(Projektas):
    '''Grazina lista su nuorodomis i conv_dv 
    esancias sio projekto straipsniu direktorijas.

    Return: [(dir, name),...].'''
    projektai=get_list_of_projects()
    lenghtas=len(Projektas)
    Straipsniai=[]
    for leidykla in projektai:
        for projektas in leidykla:
            if projektas[-lenghtas:]==Projektas:
                for straipsnis in  os.listdir(projektas):
                    Straipsniai.append((os.path.join(projektas,straipsnis),straipsnis))
    return Straipsniai

def get_elsa_issues():
    '''Grazina lista su nuorodomis i conv_dv 
    esancias sio projekto straipsniu direktorijas.

    Return: [(dir, name),...].'''
    projektai=get_elsa_projects()
    Straipsniai=[]
    for leidykla in projektai:
        for projektas in leidykla:
            for straipsnis in  os.listdir(projektas):
                Straipsniai.append((os.path.join(projektas,straipsnis),straipsnis))
    return Straipsniai

def get_everything():
    '''Pavojinga!!!'''
    listas=get_list_of_projects()
    visi=[]
    for nr,i in enumerate(listas):
        for k in i:
            visi=visi+get_issues(k)
        if nr==3:break
    return visi
            


def ensure_dir(f):
    '''Uztikrina direktorijos buvima.'''
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

def surink_komandas(String,Straipsnis='Unnamed',komanda='\\newcommand'):
    '''Perdavus texinio failo turini, ir straipsnio pavadinima,
    surenkama nurodyta komanda.'''
    for i,char in enumerate(String):
        if char=='\\' and CMDparsing.metachar(i,String):
            cmd=CMDparsing.collect_full_command(i,String)
            if cmd[1]==komanda:
                direktorija=os.path.join(my_stats_dir,komanda[1:]+'/')
                ensure_dir(direktorija)
                with open(direktorija+komanda[1:]+".txt",'at') as output:
                    output.write('\n'+'='*50+'\n')
                    output.write(Straipsnis+'\n'+'Parsed:\n')
                    output.write(cmd[1])
                    for arg in cmd[2]:
                        if arg: output.write(arg)
                    output.write('\n'+'-'*50+'\n'+'Orig:\n')
                    output.write(cmd[3])



def surink_komandos_statistika(String,Straipsnis='Unnamed',komanda='\\usepackage'):
    '''Perdavus texinio failo turini, ir straipsnio pavadinima,
    surenkama nurodyta komanda.'''
    def check_this(cmd):
        nonlocal komanda
        if cmd[1]==komanda:
            return komanda
        else:
            return None    
        
    direktorija=os.path.join(my_stats_dir,komanda[1:]+'_stat/')
    ensure_dir(direktorija)          
    global stat
        
    with open(direktorija+komanda[1:]+".txt",'wt') as output:
        output.write('*'*60)
        output.write("Komandos {} statistika conv_dv direktorijoje".format(komanda))
        output.write('*'*60) 

    for i,char in enumerate(String):
        if char=='\\' and CMDparsing.metachar(i,String):
            cmd=CMDparsing.collect_full_command(i,String)
            if check_this(cmd):
                tmp=komanda
                tmp=tmp+''.join([k for k in cmd[2] if k])
                if stat.get(tmp,None): 
                    stat[tmp][0]+=1
                    stat[tmp][1].append(Straipsnis)
                else:stat[tmp]=[1,[Straipsnis]]
    return 
        
        
def do_job(projektas,funk,Straipsnis=None):
    '''Perdavus projekta ir darbine funkcija, 
    dirbama su failu, loginant visus errorus.'''
    for kelias,straipsnis in projektas:
        if Straipsnis:
            if not Straipsnis==straipsnis:
                continue
        try:
            with open(os.path.join(kelias,straipsnis+'.txt'),'rt',
                      encoding="ascii", 
                      errors="surrogateescape") as failas:
                String=failas.read()
                funk(String,straipsnis)
                del String
        except UnicodeError as msg:
            direktorija=os.path.join(my_errors_dir,'UnicodeError/')
            ensure_dir(direktorija)
            shutil.copy(os.path.join(kelias,straipsnis+'.txt'),
                        os.path.join(direktorija,straipsnis+'.tex'))
            continue
        except FileNotFoundError as msg:
            continue
        except AlgError as msg:
            direktorija=os.path.join(my_errors_dir,'AlgError/')
            ensure_dir(direktorija)
            shutil.copy(os.path.join(kelias,straipsnis+'.txt'),
                        os.path.join(direktorija,straipsnis+'.tex'))
            with open(os.path.join(direktorija,
                                   straipsnis+'_log.txt'),
                                   'wt') as logas:
                logas.write(repr(msg))
            continue
        except IndexError as msg:
            direktorija=os.path.join(my_errors_dir,'IndexError/')
            ensure_dir(direktorija)
            shutil.copy(os.path.join(kelias,straipsnis+'.txt'),
            os.path.join(direktorija,straipsnis+'.tex'))
            with open(os.path.join(direktorija,
                                   straipsnis+'_log.txt'),
                                   'wt') as logas:
                logas.write(repr(msg))    
            continue
        except MatchError as msg:
            direktorija=os.path.join(my_errors_dir,'MatchError/')
            ensure_dir(direktorija)
            shutil.copy(os.path.join(kelias,straipsnis+'.txt'),
                        os.path.join(direktorija,straipsnis+'.tex'))
            with open(os.path.join(direktorija,straipsnis+'_log.txt'),
                      'wt') as logas:
                logas.write(repr(msg))    
            continue
        except EOSError as msg:
            direktorija=os.path.join(my_errors_dir,'EOSError/')
            ensure_dir(direktorija)
            shutil.copy(os.path.join(kelias,straipsnis+'.txt'),
                        os.path.join(direktorija,straipsnis+'.tex'))
            with open(os.path.join(direktorija,straipsnis+'_log.txt'),
                      'wt') as logas:
                logas.write(repr(msg))    
            continue
        except ParseError as msg:
            direktorija=os.path.join(my_errors_dir,'ParseError/')
            ensure_dir(direktorija)
            shutil.copy(os.path.join(kelias,straipsnis+'.txt'),
                        os.path.join(direktorija,straipsnis+'.tex'))
            with open(os.path.join(direktorija,straipsnis+'_log.txt'),
                      'wt') as logas:
                logas.write(repr(msg))    
            continue
            



issues=get_elsa_issues()
stat={}
returnas=do_job(issues,surink_komandos_statistika)
print(stat.keys())




   
        
        

