# -*- coding: utf-8 -*-
'''Modulis, kuriame aprasytas metodas surenkantis komanda ir jos argumentus, priklausomai,
nuo komandos tipo ir jos patterno apibrezto texsyntax modulyje.

Naudojimas: collect_full_command(pozicija,stringas)
pozicija -- komandos pradzia reiskianti metacharas "\\"
stringas -- parsinamo failo turinys

Return: (charu_skaicius,komanda,argumentu listas, originalus_tekstas)'''

import string, sys, os

try:
    if __IPYTHON__:
        if sys.platform=='win32':
            os.chdir('d:/Luko/vtexparser/')       
        else:
            sys.path.append('/home/lukas/vtexparser/')
except:
    pass

# LaTeX'o sintakse apibrezta 
# kitame modulyje
import latexsyntax

              ######################################## 
              #### PARSINIMO ERRORU APIBREZIMAI   ####
              ## tam, kad butu galima loginti visus ##
              ## netikusius parsinimo meginimus     ##
              
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

def context(poz,String,End=False,Range=50,Tag=False,Delim=False):
    '''Grazina eilutes konteksta apie esama
    symboli (symboliu seka).'''
    if Delim:
        delim=Delim
    else:
        delim=''
    if Tag:
        ltag=delim+'<'+Tag+'@-->'+delim
        rtag=delim+'<--@'+Tag+'>'+delim
    else:
        delim=''
        ltag=delim+'@-->>'
        rtag='<<@--'+delim
    if not End:
        
        End=poz
    else: End=End-1
    if poz<=Range: before=poz
    else: before=Range
        
    if len(String)-End<=Range: after=len(String)-End
    else: after=Range
    if Tag:
        return (ltag+String[poz:End+1]+rtag)
    else:
        if poz==0:
            return (ltag+String[poz:End+1]+rtag+String[End+1:End+after])
        else:
            return (String[poz-before:poz]+ltag+String[poz:End+1]+rtag\
                    +String[End+1:End+after])

              ######################################## 
              ####         PARSINIMO METU         ####
              ##     INICIALIZUOJAMI OBJEKTAI       ##
              
              ######################################## 
              ####      OBJEKTU KOMPONENTAI       ####

class Opening:
    '''Skirtukai atidanatys reiskini'''
    def __init__(self,Tipas,Name,Body):
        self.Type=Tipas
        self.name=Name
        self.body=Body
    def show_self(self):
        print('▼----------------------['+self.Type+':'+repr(self.body)+']')

class Closing(Opening):
    def __init__(self,Tipas,Name,Body):
        super().__init__(Tipas,Name,Body)
    def show_self(self):
       print('▲----------------------['+self.Type+':'+repr(self.body)+']')
                      
              ######################################## 
              ####         PATYS OBJEKTAI         ####
              
class ParseObject():
    '''Universalus objektas parsinime.'''
    def __init__(self,tipas):
        self.body=''                      # skriptinio pavidalo kunas
        self.Type=tipas

class FruitfullObject(ParseObject):
    '''Objektas turintis vidine struktura, sudaryta 
    is kitu objektu. Jis taip pat savyje turi opening 
    ir closing objektus.'''
    def __init__(self,tipas):
        super().__init__(tipas)
        self.kids=[]             # vidine struktura
        # butinas atidarantis reiskinys
        self.opening=Opening('PRADZIA','PRADZIA','PRADZIA')
        self.closing=Closing('PRADZIA','PRADZIA','PRADZIA')
        self.address=[]
    def show_self(self):
        print('  '*len(self.address),end='')
        self.opening.show_self()
        print('  '*len(self.address),end='')
        print('[stack:'+str([i['opening'] for i in self.stack])+']')
        for i in self.kids:
            i.show_self()
        print('  '*len(self.address),end='')
        self.closing.show_self()

class Block(ParseObject):
    def __init__(self,tipas):
        super().__init__(tipas)
        self.kids=[]            
        self.address=[]
        self.opening_representation=''
        self.body=None
    def show_self(self):
        print('  '*len(self.address),end='')
        print('*'*20)
        print(self.body.show_self())
        print("[Pilnas blokas:",repr(self.fulltext))
        print("Pabaiga:",self.pabaiga)
        print('  '*len(self.address),end='')
        print('*'*20)

class SimpleStructure(ParseObject):
    def __init__(self,tipas):
        super().__init__(tipas)
        self.fulltext=''
        self.address=[]
    def show_self(self):
        print('  '*len(self.address),end='') 
        print('['+self.Type+':'+repr(self.fulltext)+']')
        
class Command(ParseObject):
    '''Komanda su argumentais.
    syntax--sintakse kurioje inicializuota komanda
    name--komandos scriptine reprezentacija'''
    def __init__(self,tipas,name,syntax,address):
        self.Type=tipas
        self.name=name
        self.syntax=syntax
        self.address=address
        self.args=[]
    def show_self(self):
        print('  '*len(self.address),end='') 
        print(self.name,'<--Komanda:',self.Type)
        for i,arg in enumerate(self.args):
            print('  '*len(self.address),end='') 
            print('♣'+'-'*10,str(i+1)+'-as argumentas')
            arg.show_self()
            print('  '*len(self.address),end='') 
            print('♣'+'-'*20)

    
            
              ######################################## 
              ####   IPRASTI METODAI NAUDOJAMI    ####
              ##         PARSINIMO PROCESE          ##
                    
def escaped(poz,String,syntax='T'):
    '''Patikriname ar esamas charas 
    nera escapintas.
    Parasyta, numatant escape charo
    sintakses pasikeitimo galimybe.'''
    # DEBUGING :: jei syntakseje neapibreztas escape charas
    try:
        ESC_CH=latexsyntax.SYNTAX[syntax]['escape']
    except KeyError:
        return False
    # :::
    if poz==0: return False
    if not (String[poz-1] in ESC_CH.keys()):
        return False
    # DEBUGING :: PATIKRINAME AR NEBUVO SINTAKSES KEITIMO
    elif ESC_CH[String[poz-1]]:
        raise AlgError(
            "Pakeista escape charu sintakse "\
            "ir nenurodytas elgsenos tipas!!!:"\
            "\n{}\nEscape charu sarasas"\
            ":\n{}".format(context(poz-1,String),
                           ESC_CH),poz-1)    
    # :::
    else:
        # suskaiciuojam kiek yra 
        # vienas po kito einanciu backslashu
        # pries esama chara
        slashes=0
        i=poz-1
        while (String[i] in ESC_CH.keys()):
            slashes+=1
            if i==0: break
            i-=1
        if not slashes%2:return False
        else: return True

def metachar(poz,String,syntax='T'):
    '''Jei charas yra metacharu sarase, 
    tai patikrinam ar jis neeskeipintas.'''
    META_CH=latexsyntax.SYNTAX[syntax]['metach']
    keys=META_CH.keys()
    # print("\nmetacharai:",META_CH,'\nsymbolis:',String[poz])
    if not (String[poz] in keys):
        return False
    if poz==0:
        return True  
    if escaped(poz,String,syntax):
        return False
    else: return True

def metachar_greedy(poz,String):
    '''Jei esamas charas nera metacharas
    ismeta parsingo errora.
         
    Naudoti ten kur butinai reikalingas metachar'''
    if metachar(poz,String): return True
    else: 
        raise AlgError(
            'Sis simbolis nera metacharas:'\
            '\n{}'.format(context(poz,String)),poz)
            
def EOS(poz,String):
    '''Tikrinama ar esamas charas
    nera eilutes pabaiga.'''
    return poz>=len(String)-1
            
def skip_whitespace(poz,String,WHITES=latexsyntax.WHITESPACE):
    '''Praleidziam visus whitespace, kurie
    yra ne newline. 
    Grazinamas whitespacu sekos ilgis.'''
    # DEBUGING :::
    if (not (String[poz] in WHITES)) or escaped(poz,String):
        raise AlgError(
            'Tai nera whitespaceas:"\
            "\n{}'.format(context(poz,String)),poz)
    # ::: 
    i=poz
    while String[i] in WHITES:
        if EOS(i,String): 
            # paliekam viena whitespace
            # kitoms funkcijoms
            return i-poz
        i+=1
    return i-poz

              ######################################## 
              ####   INLINE KOMENTARU SURINKIMO   ####
              ##            MECHANIZMAS             ##

def is_start_of_comment(i,String,syntax):
    '''Patikriname ar esamas charas yra 
    inline komentaro pradzia. Jei taip grazina: 
    (chara kuris isjungs komentara, opciju rinkini).
    Opciju rinkinys yra reikalingas tam, nes galima
    perapibrezti komentara taip, kad sutikus isjungiamaji
    symboli, nebus surinkti sekantys whitespace.
    Taigi, raide 'w' nurodo, kad reikes surinkti whitespace.'''
    COMMENT=latexsyntax.SYNTAX[syntax]['icomment']
    if (String[i] in COMMENT.keys()) and metachar(i,String):
        return COMMENT[String[i]]
    else: return False
           
def skip_icomment(poz,String,syntax):
    '''Nuskaitomas komentaras ir grazinamas jo ilgis.
    Skaitoma tada, kai komentaro jungiklis yra metachar'''
    COMMENT=latexsyntax.SYNTAX[syntax]['icomment']
    if is_start_of_comment(poz,String,syntax):
        cstart=String[poz]
        cend=is_start_of_comment(poz,String,syntax)[0]
        cprop=is_start_of_comment(poz,String,syntax)[1]
    else:
        raise AlgError('Tai nera komentaro "\
          "jungiklis!:\n{}'.format(context(poz,String)),poz)
    MULTILINE=True
    i=poz
    while MULTILINE:
        while String[i]!=cend:
            # jei komentaras uzbaigtu faila
            if EOS(i,String):
                raise EOSError(
                    "Komentaras uzbaigia teksta.\n"\
                    "Tikriausiai buvo ieskoma komandos argumento."\
                    "Kitiems atvejams skip_comment naudoti, su try!!!\n"\
                    "{}".format(context(i,String)),i)
            i+=1
        i+=1
        if String[i]==cstart: continue
        # Jei isjungigklis surenka visus trailing whitespace
        elif ('w' in cprop) and  (String[i] in latexsyntax.WHITESPACE):
                i+=skip_whitespace(i,String)
                # jei paskutinis white charas buvo string pabaiga
                if EOS(i,String):
                    raise EOSError(
                    "Whitespace seka uzbaigia teksta.\n"\
                    "Tikriausiai buvo ieskoma komandos argumento."\
                    "Kitiems atvejams skip_comment naudoti, su try!!!"
                    "\n{}".format(context(i,String)),i)
                # SURENKAMA KOMENTARU SEKA 
                if String[i]==cstart: continue
                else:
                    return i-poz
        else: return i-poz

                ################################################# 
                ######    KELIONE IKI KOMANDOS ARGUMENTO ########
                #### Preliudija i komandu surinkimus         ####
                #### taciau pirma bus surenkami enviromentu  ####
                #### pavadinimai                             ####
                
def is_start_of_cmd(poz,String,syntax='T'):
    '''Patikrinama ar esamas charas yra komandos pradzia.'''
    START_OF_CMD=latexsyntax.SYNTAX[syntax]['cmd_start']
    COMMAND_CHARS=latexsyntax.SYNTAX[syntax]['cmd_chars']
    if not (String[poz] in START_OF_CMD.keys()):
        return False
    else:
        if metachar(poz,String): return True
        else: return False

def skip_command_name(poz,String,syntax='T'):
    '''Padavus esama aktyvu chara ir jo pozicija 
    grazinamas komandos pavadinimo ilgis.'''
    START_OF_CMD=latexsyntax.SYNTAX[syntax]['cmd_start']
    COMMAND_CHARS=latexsyntax.SYNTAX[syntax]['cmd_chars']
    # patikriname ar esamas charas yra komandos
    # pradzios metacharas
    char=String[poz]
    if not is_start_of_cmd(poz,String):
        raise AlgError("Tai nera komanda aktyvuojantis simbolis:"\
                       "\n{}".format(context(i,String)),poz)
                       
    if START_OF_CMD[char]:
        raise AlgError(
                      "Pakeista komandos aktyvavimo sintakse "\
                      "ir nenumatyta elgsena!!!:"\
                      "\n{}Komanda aktyvuojanciu charu sarasas"\
                      ":\n{}".format(context(poz,String),
                                      START_OF_CMD),poz)
    # Jei netycia parsinama eilute uzsibaigtu 
    # komanda aktyvuojanciu symboliu
    if EOS(poz,String):
        raise ParseError(
            'Parsinama eilute baigiasi ten kur turetu prasideti'\
            'komandos pradzia:\n{}'.format(context(poz,String)),poz)
    # jei komanda susideda is simbolio
    if not (String[poz+1] in COMMAND_CHARS-{'*'}):
        return 2
    i=poz+1
    while String[i] in COMMAND_CHARS:
        if EOS(i,String):
            # jei netycia komanda uzbaigtu parsinama stringa
            raise EOSError("Renkant komanda buvo pasiektas teksto  "\
                           "galas.\nPries parsinant gale "\
                           "idekite papildoma newline, arba naudokite"\
                           "try:\n".format(context(i,String),i))
        i+=1
    return i-poz

def is_strict_switch(poz,String,syntax='T'):
    '''Patikrina ar esamas reiskinys yra atidarantis 
    grieztas switchas. Jei taip grazina jo ilgi.'''
    switches=latexsyntax.SYNTAX[syntax]['switches'].keys()
    k=skip_command_name(poz,String,syntax)
    if String[poz:poz+k] in switches:
       return k
    else: return False

def skip_till_argument(poz,String,syntax='T'):
    '''Praleidzia visus, nereiksmingus
    charus iki sekancio argumento.
    Tarp komandos ir argumento galimi tik 
    iprastiniai komentarai % ir whitespacai.
    Taip pat, dar neprasidejus komentarui  
    yra galimas 1-as newline.'''
    BEGIN_OF_ARG=latexsyntax.SYNTAX[syntax]['arg_beg']
    i=poz
    if String[poz] in BEGIN_OF_ARG:
        return 0
    if String[i] in latexsyntax.WHITESPACE:
        i+=skip_whitespace(i,String)
    # po komandos su whitespace galimas tik vienas newline 
    if String[i]=='\n':
        i+=1
    while not (String[i] in BEGIN_OF_ARG):
        if is_start_of_comment(i,String,syntax):
            i+=skip_icomment(i,String,syntax)
        elif String[i] in latexsyntax.WHITESPACE:
            i+=skip_whitespace(i,String)
        else: raise AlgError(
                "Nenumatytas charas tarp argumentu:\n"\
                "{}".format(context(i,String)),i)
        if EOS(i,String):
            raise EOSError(
                "Parsinamas tekstas baigiasi "\
                "komanda, kuri turi tureti argumenta:"\
                "\n{}".format(context(i,String)),i)
    return i-poz

def is_start_of_env(poz,String,syntax='T'):
    '''Patikrinama ar esama komanda yra env
    pradza'''
    i=poz
    ENV_SWITCH=latexsyntax.SYNTAX[syntax]['env_switch']
    k=skip_command_name(i,String)
    if (String[i:i+k] in ENV_SWITCH.keys()):
        return True
    else:
        return False

def is_end_of_env(poz,String,syntax='T'):
    '''Patikrinama ar esama komanda yra env
    pabaiga'''
    i=poz
    ENV_SWITCH=latexsyntax.SYNTAX[syntax]['env_switch']
    k=skip_command_name(i,String)
    if (String[i:i+k] in ENV_SWITCH.values()):
        return True
    else:
        return False
       
def collect_enviroment_name(poz,String,syntax='T'):
    '''Surenkamas ir grazinamas enviromento 
    pavadinimas. Grazinama: 
      (ilgis nuo switch pabaigos iki arg pabaigos,
      env_pavadinimas).'''
    ENV_SWITCH=latexsyntax.SYNTAX[syntax]['env_switch']
    METABRACES=latexsyntax.SYNTAX[syntax]['mbraces']
    COMMENT=latexsyntax.SYNTAX[syntax]['icomment']
    if not is_start_of_cmd(poz,String):
        raise AlgError("Cia ne enviromento pradzia--"\
                       "net ne komandos pradzia\n"\
                       "{}".format(context(poz,String)),i)
    i=poz
    k=skip_command_name(i,String)
    if not ((String[i:i+k] in ENV_SWITCH.keys())\
        or (String[i:i+k] in ENV_SWITCH.values())):
        raise AlgError("Cia ne enviromento pradzia"\
                       "{}".format(context(poz,String)),i)
    i+=k
    k=skip_till_argument(i,String)
    if not (String[i+k] in METABRACES.keys()):
        raise AlgError(
            "Envromento pavadinimas turi "\
            "buti apskliausti metaskliaustais!!!\n"\
            "{}".format(context(i,String)),i)
    i+=k
    left=String[i]
    right=METABRACES[String[i]][0] 
    braces=[1,0]
    i+=1
    arg=''
    while braces[0]!=braces[1]:
        if String[i]==left: 
                braces[0]+=1; i+=1
                continue
        elif String[i]==right: 
            braces[1]+=1; i+=1
            continue
        elif is_start_of_comment(i,String,syntax):
             k=skip_comment(i,String,syntax)
             i+=k
             continue
        arg+=String[i]    
        i+=1
    return i-poz, arg

              ######################################## 
              ####  APLINKU UZSIDARYMO TIKRINIMO  ####
              ##            MECHANIZMAI             ##
              #    Aptikus, nauja aplinka, reikia    #
              # nustatyti, jos uzsidarymo mechanizma #
    
def check_matching_env(poz,String,syntax,opening):
    '''Tikrinama ar esamas reiskinys, yra 
    enviromento uzdarymas. Opening -- nurodomas 
    enviromento pavadinimas.'''
    print("Tikrinama ar neuzdaro enviromentas",opening)
    if not is_start_of_cmd(poz,String,syntax):
        return False
    if is_end_of_env(poz,String,syntax):
        if collect_enviroment_name(poz,String,syntax)[1]!=opening:
            return False
        else: 
            return collect_enviroment_name(poz,String,syntax)[0]
    
def check_matching_switch(poz,String,syntax,switch):
    '''Tikrina ar esamas reiskinys yra griezto switcho 
    uzdarymas.'''
    print("Tikrinama ar neuzdaro switchas",switch)
    METACH=latexsyntax.SYNTAX[syntax]['metach']
    closing=latexsyntax.SYNTAX[syntax]['switches'][switch]['closing']
    if not is_start_of_cmd(poz,String,syntax):
        return False
    else:
        k=skip_command_name(poz,String,syntax)
        if String[poz:poz+k]==closing:
            return k
        else: return False

def check_matching_delim(poz,String,syntax='T',opening='{'):
    '''Tikrina ar esmas charas yra uzdarantis esamo
    objekto parsinima vienazenklis skirtukas.'''
    print("Tikrinama ar neuzdaro skirtukas",opening)
    # DEBUGINIMUI :: istrinti po to, kai bus pilnai pratestuotas
    openings=latexsyntax.SYNTAX[syntax]['delims'].keys()
    if not (opening in openings):
        raise AlgError("Syntakseje \'{}\' neapibreztas"\
                       "skirtukas \'{}\'!\n Kontextas:\n"\
                       "{}".format(syntax,opening,context(poz,String)),poz)

    # :::
    closing=latexsyntax.SYNTAX[syntax]['delims'][opening]['closing']
    if String[poz]!=closing:
        return False
    # Jei esamas charas atitinka uzdarancio symbolio apibrezima
    # dar patikrinamos, kitos butinos savybes
    properties=latexsyntax.SYNTAX[syntax]['delims'][opening]['properties']
    if properties:
        if 'meta' in properties:
            # PROBLEMA: \\end{verbatim} 
            #       antras \ nesiskaito eskeipintas
            #       ir ji reiktu traktuoti, kaip metachar
            if metachar(poz,String,syntax):
                return 1
            else:
                return False
    # DEBUGINIMUI ::
    if escaped(poz,String,syntax):
        raise AlgError("Sis charas turejo buti surinktas "\
                       "kaip komanda:\n{}".format(context(poz,String)),
                       poz)
    # :::
    return True

def check_if_multichar(poz,String,syntax):
    '''Kai kurie aktyvus symboliai, gali sudaryti
    kombinacijas, pakeiciancias ju prasme. Butina tai
    pagauti is anksto!
    pvz.: $-->$$.'''
    if EOS(poz,String):
        raise ParseError("Esamas aktyvus charas uzbaigia parsinama eilute:"\
                         "\n{}".format(context(poz,String)),poz)
    char=String[poz]
    MULTICHAR=latexsyntax.SYNTAX[syntax]['delims'][char]['multichar']
    if String[poz:poz+2] in MULTICHAR:
        return String[poz:poz+2]
    else: 
        return False
            
def check_matching_multichar_delim(poz,String,syntax,opening):
    '''Sutikus  skirtuka, ar komanda, kuris turi opcija 'rpt' 
    (si opcija, reiskia, jog galimas ilgesnis  reiskinys,
    turintis kirtinga prasme), tikrinama, ar tai nera tas
    ilgesnis reiskinys.
    Pvz: sutikus $, tikrinama ar ne $$'''
    print("Tikrinama ar neuzdaro multicharo",opening)
    MULTICHAR_DELIMS=latexsyntax.SYNTAX[syntax]['mch_delims']
    closing=MULTICHAR_DELIMS[opening]['closing']
    properties=MULTICHAR_DELIMS[opening]['properties']
    if properties:
        if 'meta' in properties:
            if not metachar(poz,String,syntax):
                return False
    if String[poz]!=closing[0]:
        return False
    else:
        if String[poz:poz+len(closing)]==closing:
            return len(closing)

def check_end_of_block(poz,String,syntax,opening):
    print("Bloko uzdatymo tikrinimas")
    if type(opening)==Command:
        print("Tikrinama ar neuzdaro",opening.name)
        if not is_start_of_cmd(poz,String,syntax):
            print("NE")
            return False
        else:
            k=skip_command_name(poz,String,syntax)
            if String[poz:poz+k]==opening.name:
                print("UZSIDARE")
                return True
            else:
                print("NE",String[poz:poz+k],"=/",opening.name)
                return False
    elif type(opening)==str:
            print("Tikrinama ar neuzdaro",opening)
            if String[poz]==opening:
                print("U")
                return True
            else:
                print("NE")                
                return False
    
def identify_opening(opening,syntax='T'):
    '''Parenka parsinamo reiskinio 
    uzdarymo mechanizma atpazystanti metoda.
    Grazina funkcija, kuria bus tikrinama.
    Parenkama funkcija grazina:
    (a) uzdarancio reiskinio ilgi
    (b) spec zinute, jeigu tokia yra'''
    DELIMS=latexsyntax.SYNTAX[syntax]['delims']
    MCH_DELIMS=latexsyntax.SYNTAX[syntax]['mch_delims']
    SWITCHES=latexsyntax.SYNTAX[syntax]['switches']
    ENVIROMENTS=latexsyntax.SYNTAX[syntax]['enviroments']
    # Blokas: tabuliaro skirtukas (\\) row skirtukas & item skirtukas \\item 
    BLOCKS=''
    if opening in DELIMS.keys():
        return lambda poz, String:\
           check_matching_delim(poz,String,syntax,opening), 'delimeter'
    if opening in MCH_DELIMS.keys():
        return lambda poz, String:\
           check_matching_multichar_delim(poz,String,syntax,opening), 'multichar_delimeter'
    elif opening in ENVIROMENTS.keys():
        return lambda poz, String:\
           check_matching_env(poz,String,syntax,opening), 'enviroment'           
    elif opening in SWITCHES.keys():
        return lambda poz, String:\
           check_matching_switch(poz,String,syntax,opening), 'switch'
    else: 
        raise AlgError("Reiskinys, kurio uzdarymo ieskoma "\
             "yra neapibreztas."
             "\n{}".format(opening),0)
    
              ######################################## 
              ####  PAPRASTOS STRUKTUROS OBJEKTU  ####
              ##       SURINKIMO  MECHANIZMAI       ##
            
def skip_text(poz,String,syntax):
    '''Surenkamas visas tekstas, kuris
    nera aktyvuotas aktyviais simboliais.'''
    i=poz
    while not metachar(i,String,syntax):
        if EOS(i,String):
            break
        i+=1
    return i-poz

def parse_icomment(poz,String,syntax):
    "inicializuoja komentara"
    k=skip_icomment(poz,String,syntax)
    return k

              ######################################## 
              ####            KOMANDOS            ####
              ##       SURINKIMO  MECHANIZMAI       ##
        
def collect_argument(poz,String,syntax,address,new_stack):
    '''Surenka argumenta priklausomai nuo to, 
    koks jo tipas. Sis metodas pats atpazysta argumento tipa,
    istirdamas pirmaji argumento symboli.
    Grazina argumento objekta ir jo ilgi.'''
    print("Pradedamas surinkineti argumentas")
    print("Esamas charas",String[poz])
    print("Argumentui priskiriamas adresas",address)
    # symboliai, kurie gali buti argumento pradzios
    arg_beg=latexsyntax.SYNTAX[syntax]['arg_beg']
    if not (String[poz] in arg_beg):
        raise ParseError("Cia turetu buti argumento pradzia, "\
                         "taciau symbolis neatitinka argumento"\
                         "pradzios apibrezimo:{}\n"\
                         "{}".format(arg_beg,context(poz,String)),poz)
    braces=latexsyntax.SYNTAX[syntax]['mbraces']
    if String[poz] in braces.keys():
        print("Sis argumentas turi vidine struktura")
        Object, lenght=parse_wraped(poz,String,syntax,String[poz],1,
                                    address,new_stack)
        Object.Type='arg_complex'
        return Object, lenght
    cmd_start=latexsyntax.SYNTAX[syntax]['cmd_start']
    if String[poz] in cmd_start.keys():
        print("Sis argumentas yra komandos tipo")
        Argumentas, lenght, inner_messa=collect_command(poz,String,syntax,address,new_stack)
        Argumentas.body=String[poz:poz+lenght]
        Argumentas.Type='arg_cmd'
        return Argumentas, lenght
    else:
        print("Sis argumentas yra tiesiog symbolis")
        Argumentas=ParseObject('symbol')
        Argumentas.body=String[poz]
        Argumentas.address=new_address
        Argumentas.Type='arg_symb'
        return Argumentas, 1

def collect_optional_argument(poz,String,syntax):
    '''Surenka opcionalu argumenta.
    Grazina paprastos strukturos objekta.'''
    delims=latexsyntax.SYNTAX[syntax]['odelims']
    if not String[poz] in delims.keys():
        raise AlgError("Esamas symbolis nera opcionalaus"\
                       "argumento pradzia:"\
                       "\n{}".format(context(poz,String)),poz)
    left=String[poz]
    right=delims[String[poz]]
    braces=[1,0]
    i=poz+1
    while braces[0]!=braces[1]:
        if String[i]==left: braces[0]+=1
        elif String[i]==right: braces[1]+=1
        if  EOS(i,String):
            raise MatchError(
                'Nerasta skliausto pora!:\n{}'.format(
                context(poz,String)),poz)
        i+=1
    Opcionalus_argumentas=SimpleStructure('opt_arg')
    Opcionalus_argumentas.fulltext=String[poz:i]
    return Opcionalus_argumentas, i-poz
        
oarg, ilg=collect_optional_argument(1,' [aaaa[aaaaaa]aaaaa]   ','T')
    
    
    
def skip_braced(poz,String,
                meta=True,
                verb=False,
                COMMENT_SYNTAX=latexsyntax.COMMENT,
                METACHARACTERS=latexsyntax.METACHARACTERS):
        '''Grazina apskliausto reiskinio ilgi.
        Jei meta=True, tai renka tik aktyvius skliaustus,
        jei ne tai ieskos esamo skliausto poros.

        Jei verb==True, tai is sintakses bus trumpam ismesti 
        komentaro charai ir tarp skliaustu esancius % traktuos 
        kaip simbolius.'''
        if len(COMMENT_SYNTAX)!=1:
            raise AlgError(
                "Komentaro sintakses apibrezime yra daugiau"\
                "negu vienas simbolis:\n"\
                "{}\n{}".format(COMMENT_SYNTAX,context(i,String)),i)           
        COMMENT_SYNTAX=latexsyntax.COMMENT
        if meta:
            DELIMETERS=latexsyntax.ARG_DELIMS
        else:
            DELIMETERS=latexsyntax.BRACES
        # jei apskliaustas reiskinys yra
        # verbatimine aplinka, ir procento zenklas nereiskia 
        # komentaro pradzios
        if verb:
            del COMMENT_SYNTAX['%']
        i=poz
        char=String[poz]
        if (char in latexsyntax.DELIMETERS.keys()) and metachar(poz,String):
            left=String[poz]
            right=latexsyntax.ARG_DELIMS[left]
        else:
            raise AlgError("Tai nera argumento skirtukas:"\
                           "\n{}".format(context(i,String)),i)
        if EOS(i,String):
            raise EOSError(
                "Tekstas baigiasi, ten kur "\
                "turetu buti skliaudziamas argumentas!".format(
                    context(i,String)),i)
        i+=1
        braces=[1,0]
        while not braces[0]==braces[1]:
            if String[i] in COMMENT_SYNTAX.keys() and metachar(i,String):
                try:
                    i+=skip_comment(i,String)
                except EOSError:
                    raise MatchError(
                        'Nerasta skliausto pora!:\n{}'.format(
                            context(poz,String)),poz)
            if (String[i] in (left+right)) and metachar(i,String):
                if String[i]==left: 
                    braces[0]+=1
                elif String[i]==right:
                    braces[1]+=1
            if braces[0]==braces[1]: break
            if  EOS(i,String):
                raise MatchError(
                    'Nerasta skliausto pora!:\n{}'.format(
                        context(poz,String)),poz)
            i+=1
        return i-poz+1
                  
def collect_command(poz,String,syntax,address,new_stack):
    '''Surenka komanda, su jos argumentais, jei komandos
    argumentas yra verb tipo tai netikriname, komentaru buvimo
    ir pasiimame iki uzdarancio skliausto.
    Grazinamas komandos tipo objektas!'''
    print("\n\nPradedu komandos surinkima")
    argument_nr=0
    i=poz
    ilg=skip_command_name(poz,String,syntax)
    Komandos_pav=String[i:i+ilg]
    commands=latexsyntax.SYNTAX[syntax]['commands']
    pattern=commands[Komandos_pav]['pattern']
    Type=commands[Komandos_pav]['type']
    i+=ilg
    print("KOMANDA:",Komandos_pav)
    print("ESAMA_POZICIJA:", context(i,String))
    print("Sios komandos adresas",address)
    # susirenkam zvaigzdute
    # ji atsiskiria nuo komandos kaip ir argumentas
    if Komandos_pav[-1:]!='*':
        ilg=skip_till_argument(i,String)
        if String[i+ilg]=='*':
            Komandos_pav=Komandos_pav+'*'
            i+=ilg+1
            print("Surinkau komandos zvaigzdute\n"\
            "dabartine mano pozicija:{}".format(
                context(i,String)))
        else:
            pass
    # Inicijuojamas komandos tipo objektas 
    command=Command(Type,Komandos_pav,syntax,address)
    print("Pradedu rinkti argumentus:\n",context(i,String)) 
    print("Komandos_Paternas:",pattern)
    if not pattern:
        args=None
    else:
        print("Si komanda turi paterna!!!")
        print("ESAME:",context(i,String))
        for nr,k in enumerate(pattern):
            # jei argumentas pagrindinis
            # 1 ir didzioji raide reprezentuoja pagrindini argumenta
            if  (type(k)==int and k==1) or (type(k)==str and  k.isupper()):
                # jei argumento syntakse nenurodyta
                if type(k)==int:
                    inner_syntax=syntax
                else:
                    inner_syntax=k
                print("ieskom pagrindinio argumento:\n",
                      context(i,String))
                ilg=skip_till_argument(i,String,syntax)
                i+=ilg
                print("pagrindinio argumento pradzia:\n",
                      context(i,String))
                arg_address=address+[argument_nr]
                argument_nr+=1
                print("Pagrindiniam argumentui perduodamas adresas:",
                      arg_address)
                argument, lenght=collect_argument(i,String,inner_syntax,
                                                  arg_address,new_stack)
                argument.address.append(arg_address)
                argument.lenght=lenght
                command.args.append(argument)
                i+=lenght
            # jei argumentas opcionalus 
            else:
                print("Pradedamas surinkineti opcionalus argumentas")
                odelims=latexsyntax.SYNTAX[syntax]['odelims']
                ilg=skip_till_argument(i,String)
                if String[i+ilg] in odelims.keys():
                    print("Rastas opcionalus argumentas")
                    print("opcionalus:",context(i,String))
                    arg_address=address+[argument_nr]
                    argument_nr+=1
                    argument, lenght=collect_optional_argument(i,String,syntax)
                    argument.address.append(arg_address)
                    argument.lenght=lenght
                    command.args.append(argument)
                    i+=lenght
                else:
                    pass
    print("Komanda baigta parsinti taske:\n",context(i,String))
    command.fulltext=String[poz:i]

    # SWITCHAI 
    Message={}
    if command.Type=='groop_switch':
        GSType=commands[Komandos_pav]['group_switch_type']
        Message={'groop_switch':[GSType,Komandos_pav]}
    if command.Type=='start_of_block':
        block_type=commands[Komandos_pav]['block_type']
        Message={'start_of_block':block_type}
    return command, i-poz, Message
    
           ############################################### 
             ######       PARSINIMO PROCESAS      #####
                #################################### 
                    ############################ 

              ######################################## 
              ####  PARSINIMO METODAI IR JU TIPAI ####
              #   Kiekvienoje syntakseje, aktyvus    #
              #    symboliai siejasi su metodais,    #
              #   Kiekvienas metodas turi savo tipa, #
              # i kuri atsizvelgus iskvieciamas atit-#
              # kamas algoritmas ir sukuriamas ati-  #
              # tinkamas objektas                    #
              
METHODS={
    # metodus sarase yra irasyti triju tipu objektai
    # simple_strc -- do_the_right_thing aptikes toki
    #       objekta, panaudoja metoda tokiam objektui
    #       surinkti
    'icomment':{
        'parse_type':'simple_str',
        'type':'comment',
        'method':parse_icomment
        },
    # wraped_up -- objektai reikalaujantys gilesnio parsinimo
    # ir turintys vienokius ar kitokius skirtukus
    'mbraces':{
        'parse_type':'inner_parse',
        'opening':'{',
        'syntax':'O',   # O reiskia isorine sintakse
        'type':'braced'
        },
    'math':{
        'parse_type':'inner_parse',
        'syntax':'M',
        'opening':'multichar',
        'type':'math'
        },
    'switch':{
        'parse_type':'inner_parse'
        },
    'tcommand':{
        'parse_type':'command'},
    'mcommand':{
        'parse_type':'command'},
    # verbatimo aplinkose komandos surenkamos kaip tekstiniai
    # elementai
    'vcommand':{
        'parse_type':'vcommand'}}

# Zinutes, jas gali parse proceduros perduoti viena kitai
# Zinutes pavidalas, {'pavadinimas': reikalingas turinys}
# pav: {'block':None } parsinimo procedura supras, kad reikia tikrinti ne tik esamo 
# reiskinio uzsibaigima, bet ir isorinio
# Jei isorinis yra irgi block_kas 

def parse(String, syntax='T', checking=None, address=[],stack=[],
          outer_message=None,
          prevobjec=None):
    '''Grazinama: 
    1) =parse objektas=, 
    2) =objekto ilgis=.
    3) =objekta uzdarancio skirtuko ilgis=
    4) =Spec zinute kuri bus interpretuojama isoriniame lygmenyje='''
    ParseObject=FruitfullObject('MAIN')
    ParseObject.stack=stack
    # jei esamas reiskinys yra gilesnis
    print('\n\n>>>',address,"ISIJUNGIA PARSINIMO MECHANIZMAS")
    print('>>>VIDINE_SYNTAKSE:',syntax)
    # checkas -- esmamo objekto uzsibaigimo tikrinimo mechanizmas
    if checking:
        checkas=checking
    else:
        checkas=lambda x,y: False

        ########################################
        # JEI YRA ISORINIU ZINUCIU
    # busimas tikrinimu stackas
    checkings=[]
    Property={}
    new_message={}
    # suformuojama tuscia zinute
    # kuri bus perduodama isorinems strukturoms
    if outer_message:
        print("Gauta isorine zinute",outer_message)
        # jei parsinamas elementas yra bloko strukturos
        if 'block' in outer_message.keys():
            print("Ji sako, kad esamas objektas yra bloko strukturos")
            # pirma bus tikrinamas esamo reiskinio uzsibaigimas
            # suformuojama tikrinimu seka
            print("Taigi reikia formuoti stacka visu isoriniu bloku"\
                  " + 1 grupes")
            print("Esamas stackas",[i['opening'] for i in stack])
            print("Formuojamas tikrinimo mechanizmu stackas:",end='')
            for nr,obj in enumerate(reversed(stack)):
                if nr==0: continue
                if obj['object_type']=='block':
                    print("blokas",obj['opening'],end='|')
                    checkings.append(obj['function'])
                elif obj['object_type']=='group':
                    print("Grupe",obj['opening'])
                    checkings.append(obj['function'])
                    break
        # Jei esamas elementas igyja tam tikras savybes is isores
        if 'group_property' in outer_message.keys():
            print("Ji sako, kad parsinamas objektas"\
                  "turi isskirtiniu savybiu",outer_message)
            Property.update(message['group_property'])
            # susirenku visa stacka isoriniu blokiniu strukturu 
            # + 1 grupes tikrinimo mechanizmus
        #########################################
    elem=0
    i=0
    while True:
        # Patikrinama ar esamas symbolis nera skriptinio teksto pabaiga
        if EOS(i,String):
            ParseObject.fulltext=String
            print("****PARSINIMO PABAIGA****",address)
            return ParseObject
        try:
            # Atliekamas esamos strukturos 
            # uzsidarymo tikrinimas
            print("Atliekamas tikrinimas ar neuzsibaige esama struktura")
            print(context(i,String))
            if checkas(i,String):
                print("Taip")
                # grazinamas objektas, 
                # jo skriptinis ilgis 
                # ji uzdarancio reiskinio ilgis
                # zinute isoriniui procesui
                return ParseObject, i, checkas(i,String), new_message
            ############################## 
            # JEI PARSINAMA BLOKINE STRUKTURA
            # ir reikes tikrinti visa stacka 
            # uzbaigiamuju reiskiniu
            elif checkings:
                print("Esama struktura yra bloko tipo")
                print("Tikrinamas isoriniu strukturu uzsibaigimas")
                for nr, check in enumerate(checkings):
                    print(nr,'as stacko tikrinimas')
                    if check(i,String):
                        print("Esama struktura uzsibaige kartu su"\
                              "{}-a isorine struktura")
                        new_message.update({"end":[nr,check(i,String)]})
                        print("Suformuota zinute isoriniems procesams:",
                              new_message)
                        return ParseObject,i,check(i,String), new_message
                print("Blokas neuzsibaige")
            ##############################  

            print("Toliau tiriami vidiniai reiskiniai")    
            # address -- esamo objekto adresas
            # ParseObject -- sio parsinimo metu kuriamas objektas
            #    jo lipdymas slepiasi funkcijoje do_the_right_thing
            # elem -- vidinio reiskinio numeris, naudojamas nauju adresu
            #    kurimui
            # checking -- esamos grupes uzbaigimo tikrinimo mechanizmas
            k, inner_message=do_the_right_thing(i,String,syntax,ParseObject,
                                                address,elem,checking,stack,
                                                Property)
            # Jei parsinamas elementas turi savybiu veikianciu grupes 
            # likusius elementus
            elem+=1
            i+=k
            if inner_message:
                print("Is vidinio elemento gauta zinute",inner_message)
                if 'group_property' in inner_message.keys():
                    print("Ka tik buves elementas visiems sekantiems"\
                          "elementams priskirs tam tikra savybe")
                    Property.update(inner_message['group_property'])
                if 'end' in inner_message.keys():
                    print("\n\nGAUTA_ZINUTE_NUTRAUKTI_PARSINIMA:")
                    print(inner_message)
                    if inner_message['end'][0]==0:
                        print("Nutraukiamas isorinio reiskinio parsinimas")
                        print(context(i,String))
                        print("Isorini bloka uzdarantis reiskinys:")
                        print('['+String[i:i+inner_message['end'][1]]+']')
                        return ParseObject, i, inner_message['end'][1], None
                    elif inner_message['end'][0]>0:
                        print("Susikaupes ilgesnis isoriniu strukturu skaicius")
                        print("Esama struktura yra bloko tipo")
                        inner_message['end'][0]-=0
                        return ParseObject, i, 0, inner_message
        except EOSError:
            print("Pasibaige nebaigus")

def do_the_right_thing(poz,String,syntax,Father,address,elem,
                       checking,old_stack,Property):
    '''Jei esamas charas yra metacharas,
    apibreztoje syntakseje, kreipiasi i kita
    algoritma, kuris priklausomai nuo esamo,
    konteksto ir metacharui priskirtos reiksmes 
    grazina parsinimo metoda, tipa.

    Inicializuojant nauja elementa turi buti perduodamas
    tevelio adresas, kad ji butu galima ijungti i jo vidine struktura'''
    print("DO_THE_RIGHT_THING:",'\n'+repr(context(poz,String)))
    print("Isorinis addresas",address)
    print("Sis elementas isoriniame reiskinyje yra",elem)
    print("Esama syntakse",syntax)
    print("Numatyta savybe", Property)
    new_address=address+[elem]
    # sukuriamas tuscias stack elementas
    # kuriame bus saugojami tikrinimo mechanizmai
    new_stack=list(old_stack)
    print("Sukurtas naujas adresas",new_address)
    METACHARS=latexsyntax.SYNTAX[syntax]['metach']
    # jei esamas symbolis yra metacharas esamoje syntakseje
    if metachar(poz,String,syntax):
        char=String[poz]
        # istraukiamas metodo pavadinimas susijes su metacharu
        method=latexsyntax.SYNTAX[syntax]['metach'][char]
        print("Su charu sisijes metodas",method)
        # is metodo istraukiamas busimo objekto parsinimo tipas 
        parse_type=METHODS[method]['parse_type']
        ############################## 
        # jei esamas metacharas yra skirtukas 
        ##############################         
        if parse_type=='inner_parse':
            print("Esamas metacharas yra skirtukas")
            opening=METHODS[method]['opening']
            # jei atidarantis reiskinys turi ir kitokiu kombinaciuju 
            if opening=='multichar':
                if check_if_multichar(poz,String,syntax):
                    delim=check_if_multichar(poz,String,syntax)
                    print("sis skirtukas yra symboliu kombinacija", delim)
                else:
                    print("sis skirtukas yra vieno symbolio")
                    delim=String[poz]
            else: delim=String[poz]
            # Nustatome syntakse
            inner_syntax=METHODS[method]['syntax']
            # jei vidine syntakse lygi isorinei
            if inner_syntax == 'O':
                inner_syntax=syntax
            # ISKVIEVIAMAS METODAS PARSINANTIS ISSKIRTA REISKINI,
            # PERDUODAMAS ISORINIO REISKINIO ADRESAS, 
            # ATIDARANCIO SKIRTUKO ILGIS
            # VIDINIO REISKINIO NUMATOMA SINTAKSE
            Object, lenght, inner_message=parse_wraped(poz,String,inner_syntax,delim,
                                        len(delim),new_address,new_stack)
            Object.property=Property
            Father.kids.append(Object)
            return lenght, inner_message
            
        ############################## 
        # jei esamas metacharas reiskia komandos pradzia 
        ############################## 
        elif parse_type=='command':
            #################### 
            ## jei esama komanda yra grieztas switchas
            if is_strict_switch(poz,String,syntax):
                print("Esamas metacharas yra switchas")
                k=is_strict_switch(poz,String,syntax)
                switch=String[poz:poz+k]
                inner_syntax=latexsyntax.SYNTAX[syntax]['switches']\
                  [switch]['content']
                if inner_syntax == 'O':
                    inner_syntax=syntax
                Object, lenght, inner_message=parse_wraped(poz,String,inner_syntax,switch,
                                    len(switch),new_address,new_stack)
                Object.property=Property                
                Father.kids.append(Object)
                return lenght, inner_message
                
            #################### 
            ## jei esama komanda yra enviromento pradzia 
            elif is_start_of_env(poz,String,syntax):
                print("Esamas metacharas yra enviromento pradzia") 
                lenght, env_name=collect_enviroment_name(poz,String,syntax)
                opening=String[poz:poz+lenght]
                inner_syntax=latexsyntax.SYNTAX[syntax]['enviroments']\
                  [env_name]['content']
                if inner_syntax == 'O':
                    inner_syntax=syntax
                Object, lenght, inner_message=parse_wraped(poz,String,inner_syntax,env_name,
                                    lenght,new_address,new_stack)
                Object.opening.formated='\\begin{'+env_name+'}'
                Object.closing.formated='\\end{'+env_name+'}'
                Object.property=Property                
                Father.kids.append(Object)
                return lenght, inner_message
                
            ####################                 
            ## jei tai nei enviromento nei switch tipo komanda
            else:
                # TODO: SUKISTI VISKA I COLLECT_COMMAND METODA
                print("Esamas metacharas yra komandos pradzia")
                k=skip_command_name(poz,String,syntax)
                commands=latexsyntax.SYNTAX[syntax]['commands']
                command=String[poz:poz+k]
                # jei tai zinoma komanda
                if command in commands.keys():
                    print("Si komanda yra aprasyta syntakseje")
                    pattern=commands[command]['pattern']
                    Type=commands[command]['type']
                    print("perduodamas_adresas:",new_address)
                    Object,lenght, inner_message=collect_command(poz,String,syntax,
                                                  new_address,new_stack)
                    ############################## 
                    # BLOKAI
                    # jei esama komanda yra bloko pradzia
                    if 'start_of_block' in inner_message.keys():
                        Object, lenght, inner_message=ParseBlock(poz,String,syntax,
                                                                 new_address,new_stack, 
                                                                 Object, lenght)
                        if inner_message:
                            print("Znute gauta is bloko parsinimo:",inner_message)
                        Object.pabaiga=inner_message
                        Father.kids.append(Object)
                        return lenght, inner_message
                    
                    Father.kids.append(Object)
                    return lenght, inner_message
                
                # jei tai nezinoma komanda, surenkamas jos
                # skriptinis pavadinimas ir inicializuojama 
                # nezinoma komanda 
                else:
                    print("Si komanda yra nezinoma")
                    Object=Command('unknown',String[poz:poz+k],
                                   syntax,new_address)
                    Object.body=String[poz:poz+k]
                    Object.lenght=k
                    Object.property=Property
                    print("Sios komandos kunas:",Object.body)
                    Father.kids.append(Object)
                    return k, None
                
        elif parse_type=='vcommand':
            print("Radau komanda verbatimineje aplinkoje!")
            k=skip_command_name(poz,String,syntax)
            print("Jos ilgis",k)
            command=String[poz:poz+k]
            print("Komanda:",command)
            Object=SimpleStructure("verbatim_text")
            Object.fulltext=String[poz:poz+k]
            Object.lenght=k
            Object.address=new_address
            Father.kids.append(Object)
            return k, None
        ##############################
        ### jei tai struktura, kurios turinys paprastai surenkamas
        elif parse_type=='simple_str':
            Method=METHODS[method]['method']
            Type=METHODS[method]['type']
            k=Method(poz,String,syntax)
            Object=SimpleStructure(Type)
            Object.fulltext=String[poz:poz+k]
            Object.lenght=k
            Object.address=new_address
            Object.property=Property
            print("SUKURTAS PAPRASTOS STRUKTUROS OBJEKTAS:",
                  '>>'+Object.body+'<<')
            Father.kids.append(Object)
            return Object.lenght, None
    else:
        k=skip_text(poz,String,syntax)
        Object=SimpleStructure("text")
        Object.fulltext=String[poz:poz+k]
        Object.lenght=k
        Object.address=new_address
        Object.property=Property
        Father.kids.append(Object)
        print("SUKURTAS TEKSTO OBJEKTAS:",'>>'+Object.fulltext+'<<')
        return Object.lenght, None

def parse_wraped(poz,String,syntax,opening,len,address,new_stack):
    '''Metodas suparsinantis isskirta reiskini.
    Jam inicializuoti perduodamas atidarantis reiskinys
    Grazinamas objektas su visa vidine struktursada ir jo ilgis!'''
    print("\nParsinu_apgaubta:",context(poz,String))
    print("Atidarantis_reiskinys:",opening)
    print("Naujo_elemento_adresas:",address)
    Tikrinimo_mechanizmas, skirtuko_tipas = identify_opening(opening, syntax)
    new_stack.append({
            'function':Tikrinimo_mechanizmas,
            'type':skirtuko_tipas,
            'object_type':'group',
            'opening':opening,
            'poz':poz})
    print("Skirtuko_tipas:",skirtuko_tipas)
    # Sukuriamas atidarancio skirtuko objektas
    Atidarantis_skirtukas=Opening(skirtuko_tipas,opening,String[poz:poz+len])
    # Kreipiamasi i parse funkcija
    Objektas, lenght, closing_len, message = parse(String[poz+len:],
                                                   syntax,Tikrinimo_mechanizmas,
                                                   address,new_stack)
    k=lenght
    print("\nVidinio reiskinio ilgis:",lenght)
    print("Vidinis_reiskinys:",'>>'+String[poz+len:poz+len+lenght]+'<<')
    print("Uzdarantis reiskinys:",String[poz+len+lenght:poz+len+lenght+closing_len])
    print("Viso reiskinio ilgis:",len+lenght+closing_len)
    # print("apgaubtas_baigesi:",String[poz+k+closing_len:])
    Uzdarantis_skirtukas=Closing(skirtuko_tipas,opening,String[poz+len+k:poz+len+k+closing_len])
    Objektas.lenght=len+k+closing_len
    Objektas.address=address
    Objektas.body=String[poz+len:poz+len+k]
    Objektas.opening=Atidarantis_skirtukas
    Objektas.closing=Uzdarantis_skirtukas
    # objekta, jo_ilgis, zinute
    return Objektas, Objektas.lenght, None 


def ParseBlock(poz,String,syntax,address,new_stack,
               start_of_block,lenght_of_start):
    '''Parsinamas bloko tipo elemetas. Sukuriamas tikrinimo mechanizmas
    kuris grazina 0 jei randa, tokios pat tipo elementa (komanda)'''
    print("Pradedamas_parsinti_blokas:")
    print(context(poz+lenght_of_start,String))
    if type(start_of_block)==Command:
        print("Si bloka atidarantis reiskinys yra komanda")
        start_representation=start_of_block.name
    else: start_representation=start_of_block
    print("Bloko parsinima iniciaves reiskinys",start_representation)     
    print(context(poz,String))
    print("Atidarantis_reiskinys:",start_of_block)
    print("Bloko pradzia:\n{}".format(context(poz+lenght_of_start,String)))
    ending_check=lambda poz, String: check_end_of_block(poz,String,syntax,start_of_block)
    new_stack.append({
            'function':ending_check,
            'type':'just block',
            'object_type':'block',
            'opening':start_representation,
            'poz':poz})    
    InnerObject,lenght,closing, inner_message = parse(String[poz+lenght_of_start:], 
                                                      syntax, ending_check, address, new_stack,
                                                      {'block':start_representation})
    InnerObject.address=address
    print("Baigta parsinti vidine bloko struktura")
    print("Blokas uzsibaige:\n{}".format(context(poz+lenght_of_start+lenght,String)))
    print("Uzbaigian bloka gauta zinute:",inner_message)
    print("Sukuriamas bloko elementas")
    Blokas=Block('block')
    Blokas.body=InnerObject
    Blokas.fulltext=String[poz:poz+lenght_of_start+lenght]
    Blokas.opening=start_of_block
    Blokas.opening_representation=start_representation
    Blokas.lenght=lenght_of_start+lenght
    Blokas.address=address
    Blokas.pabaiga=context(poz+Blokas.lenght,String)
    print("Baigtas parsinti blokas ir griztama i isorini procesa")
    print("Taip pat issiunciama zinute isorinei funkcijai")
    return Blokas, Blokas.lenght, inner_message 
    
    
    

# Blokas:
#  Jo elementai gali buti gilios ir paprastos strukturos objektai.
#  Pvz: Tabularo turinys:
#      - row (eilute, kuri reikalauja atskiro parsinimo)
#        eilutes yra atskirtos tam tikrais symboliais 
#        arba komandomis
#        [eilute:a & b & \multicolumn{2}{l}{c+d)\\]
#      - komanda (\hline,\ccline{3-4},\cline{2})
#        Komandos turincios bloko pabaigos reiksme
#        turi buti murodytos




# test=''' { \\begin{equation}
#     \\[ apacia \\]  pries 
#     \\iffalse {sito \\[nereikia\\] $parsinti$ } \\fi 
#      po 
#      \\end
#      %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#      {equation}  
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#      { $cia mtm$  { ir t.t  {   $ { kalno virsus  } $ }}}} $$ {a+b}{c+d} $$ $ x+y$ \\begin   
#     {equation}  aaa \\begin%    
#     {verbatim}   bbb \\end {verbatim}  aaaa  \\end{equation}   
#      '''

testas='''
\\documentclass[12pt]{article}

\\begin{document}
\\section                  *               
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    {Gilus parsinimas}%+++++
%----------------------------
Parse medis teoriskai gali buti begalinis
\\begin
%ĮĮĮĮĮĮĮĮĮĮĮĮĮĮĮĮĮĮĮĮĮ
{equation}
%%%%%%%%%%%%% $
\\frac{ \\mbox{arg\,max $f(\\mbox{sup $x$})$}}
{\\mbox{denominator as $ x+\\iffalse \\alpha + \\beta \\fi y$}}
\end{equation}

TeX'iniai skliaustai yra ypatingos svarbos 
{kiekvienas reiskinys {skliaustuose {susirenka isorines {savybes 
{ir gali {tureti tik savo individualias}}}}}}. 

Butinos parsinimo salygos:
\\begin{itemize}
\\item visi \TeX{}'iniai skliaustai turi buti suporuoti
\\end{itemize}

tebunie taip \\mbox{vidinis argumentas}  $ pirmoji matematika $  
% tai yra komentaras
\\begin
%%%%%%%%%%%%
{equation}
%%%%%%%%%%%%
c+b+d
\\mbox{tekstas matematikoje $x+y\\mbox{ tai $$ z \\times{aaaa} x $$  $a$$b$tekstas} $}
\\end  {equation}
teksto pabaiga 
\\iffalse   $ {     \\begin       \\fi \\[ display matematika \\iffalse \\] \\fi \\] 
\\end{document}
'''

test='''\\begin{itemize} \\item pirmas itemas \\item antras itemas  \\end{itemize}
tolimesnis tekstas 
'''


print()
print()
objektas=parse(test,'T')
objektas.show_self()

def prasuk_objekta(objektas):
    for i in objektas.kids:
        if type(i)==FruitfullObject:
            print('   '*len(i.address), i.opening.body)
            prasuk_objekta(i)
            print('   '*len(i.address), i.closing.body)
        else:
            print('   '*len(i.address),'['+i.tipas+':'+i.body+']')
    
# prasuk_objekta(objektas)

def skip_inline_verbatim(poz,String):
    '''Verbatimine aplinka neturi aktyviu charu
    vienintelis aktyvus charas yra verbatimo esamas
    skirtukas.'''
    i=poz
    k=skip_command_name(poz,String)
    if String[i:i+k]!='\\verb':
        raise AlgError(
            "Cia ne inline verbatimo pradzia:\n"\
            "{}".format(context(i,String)),i)
    i+=k
    sym=String[i]; i+=1
    while String[i]!=sym:
        i+=1
        if EOS(i,String):
            raise EOSError("Renkant inline verbatima buvo "\
                         "pasiektas teksto galas.:\n"\
                         "{}".format(context(poz,String),poz),poz)
    i+=1
    return i-poz
           
