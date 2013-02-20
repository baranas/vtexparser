'''Modulis, kuriame aprasytas metodas surenkantis komanda ir jos argumentus, priklausomai,
nuo pateikto patterno COMMANDS zodyne.

Naudojimas: collect_full_command(pozicija,stringas)
pozicija -- komandos pradzia reiskianti metacharas "\\"

Return: '''
import string, sys, os

try:
    if __IPYTHON__:
        if sys.platform=='win32':
            os.chdir('d:/Luko/vtexparser/')       
        else:
            sys.path.append('/home/lukas/vtexparser/')
except:
    pass

METACHARACTERS={'#','$','%','^','{','}','_','~','\\'}
# whitespace'ai kurie yra ne newline 
WHITESPACE={' ','\t'}
# komanda sudarantys simboliai, * priskirima prie komandos pav 
COMMAND_CHARS=list(string.ascii_letters)
COMMAND_CHARS.append('*')
ARGUMENT=list(string.ascii_letters+string.digits)

# SARASAS NURODANTIS KIEK PAGRINDINIU IR OPCIONALIU ARGUMENTU TURI KOMANDA
# NURODOMAS PATTERNAS 1--pagr argumentas 0--opcionalus 
COMMANDS={'\\begin':(1,0),
          '\\end':(1,),
          '\\frac':(1,1),
          '\\usepackage':(0,1),
          '\\rule':(0,1,1),
          '\\footnote':(0,1),
          '\\newcommand':(1,0,0,1),
          '\\renewcommand':(1,0,0,1),
          '\\label':(1,),
          '\\part':(0,1),
          '\\chapter':(0,1),
          '\\section':(0,1),
          '\\subsection':(0,1),
          '\\subsubsection':(0,1),
          '\\paragraph':(0,1),
          '\\subparagraph':(0,1),
          '\\subsubparagraph':(0,1),
          '\\subsubsubparagraph':(0,1)}

# ENVIROMENTAI SU OPCIONALIAIS ARGUMENTAIS
# SKAICIUS ISREISKIA OPCIONALIU ARGUMENTU SKAICIU 
ENVIROMENTS={'equation':1,
             'verbatim':0,
             'comment':0}

# PAGRINDINIAI KOMANDU TIPAI 
#     * iverb -- inline verbatimas (skirtukai--bet kokie nonalpha symboliai)
#     * nocomment -- komandos kuriu argumentuose % nereiskia komentaro pradzios
#     * package -- \usepackage
#     * env -- enviromentu tagai \begin \end
#     * switch -- jungiklis
#     * math -- matematines komandos
#     * covered -- komandos kuriu argumentai apgaubia komanda is abieju pusiu
R_TYPE={'iverb':['\\verb'],
       'nocomment':['\\index',],
       'package':['\\usepackage'],
       'syntax':['\\newcommand','\\def']
       'env':['\\begin','\\end'],
       'switch':['\\it','\\bf','\\em'],    # switchai neturi nei vieno argumento
       'math':['\\frac','\\sin','\\leq']
       'msymbol':['\\alpha','\\beta'],
       'tsymbol':['\textmu','\textbackslash']}

##### R_TYPE APVERTIMAS #####
# kad galetume gauti komandos tipa
TYPE={}
LIST=[]
for i in R_TYPE.keys():
    LIST.append([i,R_TYPE[i]])
for i,j in LIST:
    for k in j: TYPE[k]=i 

del LIST
del R_TYPE
##############################

### Papildom COMMANDS is R_TYPE #####
for i in R_TYPE['switch']:
    COMMANDS[i]=None
######################################
    
BAISUS_PAKETAI={'fancyvrb','listings'}
BAISIOS_KOMANDOS={'\\DefineShortVerb',     #\DefineShortVerb{ \|} -> |%labas%|
                  '\\UndefineShortVerb'}

### Verbatimo enviromentai
VERB_ENV={'Verbatim'}          # \begin{Verbatim}[commentchar=!]
                     
class ParseError(Exception):
    '''Motininis parsinimo Erroras'''
    def __init__(self,Msg,Poz):
        self.msg=Msg
        self.poz=Poz
    def __str__(self):
        return self.msg

class MatchError(ParseError):
    '''Erroras atsirandanti, kai 
    ieskoma nesuporuoto skirtuko.'''
    def __init__(self,Msg,Poz):
        super().__init__(Msg,Poz)

class EOSError(ParseError):
    '''Erroras atsirandanti, kai 
    ieskoma ten kur baigesi stringas.'''
    def __init__(self,Msg,Poz):
        super().__init__(Msg,Poz)

        
class AlgError(ParseError):
    '''Erroras atsirandantis 
    del blogai parasyto algoritmo.'''
    def __init__(self,Msg,Poz):
        super().__init__(Msg,Poz)

        
def metachar(poz,String):
    '''Jei charas yra metacharu sarase, 
    tai patikrinam ar pries ji buves simbolis 
    nera \\'''
    if poz==0:
          return True 
    if String[poz] in METACHARACTERS:
        return String[poz-1]!='\\'
    else: return True

def metachar_greedy(poz,String):
    '''Jei esamas charas nera metacharas
    ismeta parsingo errora'''
    if metachar(poz,String): return True
    else: 
        raise AlgError(
            'This is not a metachar'\
            '\n{}'.format(context(poz,String)),poz)

def EOS(poz,String):
    '''Tikrinama ar esamas charas
    nera eilutes pabaiga. 
    !!! SUGALVOTI, KAIP OPTIMIZUOTI'''
    return poz>=len(String)-1
        
def context(poz,String):
    '''Grazina eilutes konteksta apie esama
    chara, iskirdama chara.'''
    if poz<20: before=poz
    else: before=50
    if len(String)-poz<50: after=len(String)-poz
    else: after=50
    if poz==0:
        return repr('[['+String[poz]+']]'+String[poz+1:poz+after])
    else:
        return repr(String[poz-before:poz]+'[['+String[poz]+']]'+String[poz+1:poz+after])
    
def skip_whitespace(poz,String):
    '''Praleidziam visus whitespace,
    grazinam ju ilgi'''
    i=poz
    if not (String[poz] in WHITESPACE):
        raise AlgError('This is not a whitespace:\n{}'.format(context(poz,String)),poz)
    while String[i] in WHITESPACE:
        if EOS(i,String): 
            # paliekam viena whitespace
            # kitoms funkcijoms
            return i-poz
        i+=1
    return i-poz

def skip_comment(poz,String):
    '''Nuskaitomas komentaras ir grazinamas jo ilgis.'''
    if not metachar(poz,String):
        raise AlgError('This is not a comment:\n{}'.format(context(poz,String)),poz)
    MULTILINE=True
    i=poz
    while MULTILINE:
        while String[i]!='\n':
            # jei komentaras uzbaigtu faila
            if EOS(i,String):
                raise EOSError(
                    "Comment ends string.\n"\
                    "Maybe string ends with command,"\
                    "that must have argument?\n{}".format(context(i,String)),i)
            i+=1
        i+=1
        if String[i]=='%': continue
        elif String[i] in WHITESPACE:
                i+=skip_whitespace(i,String)
                # jei paskutinis white charas buvo string pabaiga
                if EOS(i,String): return i-poz
                if String[i]=='%': continue
                else: return i-poz
        else: return i-poz
          
def check_self(String):
    '''Pries parsinant stringa,
    patikrinama ar jame nera kai kuriu 
    blogybiu:
    * Failas uzsibaigia komanda:
      ideti papildoma whitespace'''
    pass

def skip_command(poz,String):
    '''Padavus esama \\ pozicija
    ir tikrinama stringa komanda ir jos ilgi.'''
    # jei netycia stringas uzsibaigtu '\'
    if String[poz]!='\\':
        raise AlgError('This is not a start of command:\n{}'.format(context(poz,String)),poz)
    if metachar_greedy(poz,String): pass
    if EOS(poz,String):
        raise ParseError('String ends with \\:\n{}'.format(context(poz,String)),poz)
    # jei komanda susideda is simbolio
    if not (String[poz+1] in string.ascii_letters):
        return 2
    i=poz+1
    while String[i] in COMMAND_CHARS:
        if EOS(i,String):
            # jei netycia komanda uzbaigtu stringa
            raise EOSError("String ends with command."+\
                           "\nPlease insert whitespace before parsing.",len(String))
        i+=1
    return i-poz
    
def skip_till_argument(poz,String):
    '''Praleidzia visus, nereiksmingus
    charus iki sekancio argumento.'''
    i=poz
    if not(String[poz] in {'\n','%',' ','\t'}):
           return 0
    if String[i] in WHITESPACE:
        i+=skip_whitespace(i,String)
        if String[i]=='\n': 
            i+=1
    if String[i]=='\n':
        i+=1
    while String[i] in {' ','\t','%'}:
        if String[i]=='%':
            i+=skip_comment(i,String)
        elif String[i] in WHITESPACE:
            i+=skip_whitespace(i,String)
        if EOS(i,String):
            raise EOSError(
                "String ends with command,"\
                "that must have argument:\n{}".format(context(i,String)),i)
    return i-poz
           
def skip_braced(poz,String,left='{',right='}'):
        '''Grazina apskliausto reiskinio ilgi.'''        
        i=poz
        if EOS(i,String):
            raise EOSError(
                "String ends where "\
                "should be an argument!".format(context(i,String)),i)
        i+=1
        braces=[1,0]
        while not braces[0]==braces[1]:
            if String[i]=='%':
                try:
                    i+=skip_comment(i,String)
                except EOSError:
                    raise MatchError(
                        'No pair found!:\n{}'.format(context(poz,String)),poz)
            if (String[i] in (left+right)) and metachar(i,String):
                if String[i]== left: 
                    braces[0]+=1
                elif String[i]==right:
                    braces[1]+=1
            if braces[0]==braces[1]: break
            if  EOS(i,String):
                raise MatchError(
                    'No pair found!:\n{}'.format(context(poz,String)),poz)
            i+=1
        return i-poz+1

def skip_argument(poz,String):
    '''Surenkamas komandos argumentas, priklausomai,
    nuo to koks dabartinis charas.'''
    i=poz
    if String[poz]=='\\':
        i+=skip_command(i,String)
    elif String[poz]=='{':
        i+=skip_braced(i,String)
    elif String[poz] in ARGUMENT:
        i+=1
    else: 
        raise AlgError(
            "Turejo buti pagrindinis argumentas:\n".format(context(i,String)),i)
    return i-poz
              
def collect_full_command(poz,String):
    global COMMANDS
    komanda=''
    args=[]
    i=poz

    ilg=skip_command(i,String)
    komanda=String[i:i+ilg]
    i+=ilg

    # susirenkam zvaigzdute
    # atsiskiria nuo komandos kaip ir argumentas
    ilg=skip_till_argument(i,String)
    if String[i+ilg]=='*':
        komanda=komanda+'*'
        i+=ilg
    else:
        pass
    
    pattern=COMMANDS.get(komanda,None)
    if not pattern:
        args=None
    else:
        for k in pattern:
            if k:
                ilg=skip_till_argument(i,String)
                i+=ilg

                ilg=skip_argument(i,String)
                args.append(String[i:i+ilg])
                i+=ilg
            else:
                ilg=skip_till_argument(i,String)
                if String[i+ilg]=='[':
                    # print("opcionalus",context(i,String))
                    i+=ilg
                    ilg=skip_braced(i,String,left='[',right=']')
                    args.append(String[i:i+ilg])
                    i+=ilg
                else:
                    print
                    args.append(None)
                    pass
                
    return i-poz, komanda, args, String[poz:i], (poz,i)    



