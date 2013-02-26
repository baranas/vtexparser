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
import texsyntax

              ######################################## 
              #### PARSINIMO ERRORU APIBREZIMAI ######
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
    charu seka, iskirdama chara.'''
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
                    #### IPRASTOS PATIKROS IR PAPRASTI  #### 
                    #### METODAI NAUDOJAMI PARSINIME    ####
                    
def escaped(poz,String,syntax='T'):
    '''Patikriname ar esamas charas 
    nera escapintas.'''
    ESC_CH=texsyntax.SYNTAX[syntax]['escape']
    if poz==0: return False
    if not (String[poz-1] in ESC_CH.keys()):
        return False
    # PATIKRINAME AR NEBUVO SINTAKSES KEITIMO
    elif ESC_CH[String[poz-1]]:
        raise AlgError(
            "Pakeista escape charu sintakse "\
            "ir nenurodytas elgsenos tipas!!!:"\
            "\n{}\nEscape charu sarasas"\
            ":\n{}".format(context(poz-1,String),
                           ESC_CH),poz-1)    
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
    META_CH=texsyntax.SYNTAX[syntax]['metach']
    if not (String[poz] in META_CH):
        return False
    if poz==0:
        return True  
    if escaped(poz,String):
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
            
def skip_whitespace(poz,String,WHITES=texsyntax.WHITESPACE):
    '''Praleidziam visus whitespace, kurie
    yra ne newline. 
    Grazinam whitespacu sekos ilgi.'''
    if (not (String[poz] in WHITES)) or escaped(poz,String):
        raise AlgError(
            'Tai nera whitespaceas:"\
            "\n{}'.format(context(poz,String)),poz)
    i=poz
    while String[i] in WHITES:
        if EOS(i,String): 
            # paliekam viena whitespace
            # kitoms funkcijoms
            return i-poz
        i+=1
    return i-poz


          ########################################### 
          ###### INLINE KOMENTARU SURINKIMAI ########

def is_start_of_comment(i,String,syntax='T'):
    '''Patikriname ar esamas charas yra 
    inline komentaro pradzia. 
    Jei taip grazina: 
    (chara kuris isjungs komentara, opciju rinkini)'''
    COMMENT=texsyntax.SYNTAX[syntax]['icomment']
    if (String[i] in COMMENT.keys()) and metachar(i,String):
        return COMMENT[String[i]]
    else: return False
           
def skip_comment(poz,String,syntax='T'):
    '''Nuskaitomas komentaras ir grazinamas jo ilgis.
    Skaitoma tada, kai komentaro jungiklis yra metachar'''
    COMMENT=texsyntax.SYNTAX[syntax]['icomment']
    if is_start_of_comment(poz,String,syntax):
        cstart=String[poz]
        cend=is_start_of_comment(poz,String)[0]
        cprop=is_start_of_comment(poz,String)[1]
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
        elif ('w' in cprop) and  (String[i] in texsyntax.WHITESPACE):
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
                    
                    if taginam:
                        print(String[poz,i])

                    return i-poz
        else: return i-poz

                

                ################################################# 
                ######  KELIONE IKI KOMANDOS ARGUMENTO %%%%%%%%%%
                #### preliudija i komandu surinkimus         ####
                #### taciau pirma bus surenkami enviromentu  ####
                #### pavadinimai                             ####
                
def is_start_of_cmd(poz,String,syntax='T'):
    '''Patikrinama ar esamas charas yra komandos pradzia.'''
    START_OF_CMD=texsyntax.SYNTAX[syntax]['cmd_start']
    COMMAND_CHARS=texsyntax.SYNTAX[syntax]['cmd_chars']
    if not (String[poz] in START_OF_CMD.keys()):
        return False
    else:
        if metachar(poz,String): return True
        else: return False

def skip_command_name(poz,String,syntax='T'):
    '''Padavus esama aktyvu chara ir jo pozicija 
    grazinamas komandos pavadinimo ilgis.'''
    START_OF_CMD=texsyntax.SYNTAX[syntax]['cmd_start']
    COMMAND_CHARS=texsyntax.SYNTAX[syntax]['cmd_chars']
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
       
def skip_till_argument(poz,String,syntax='T'):
    '''Praleidzia visus, nereiksmingus
    charus iki sekancio argumento.
    
    Tarp komandos ir argumento galimi tik 
    iprastiniai komentarai % ir whitespacai.'''
    BEGIN_OF_ARG=texsyntax.SYNTAX[syntax]['arg_beg']
    i=poz
    if String[poz] in BEGIN_OF_ARG:
        return 0
    if String[i] in texsyntax.WHITESPACE:
        i+=skip_whitespace(i,String)
    # po komandos su whitespace galimas tik vienas newline 
    if String[i]=='\n':
        i+=1
    while not (String[i] in BEGIN_OF_ARG):
        if is_start_of_comment(i,String):
            i+=skip_comment(i,String)
        elif String[i] in texsyntax.WHITESPACE:
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
    ENV_SWITCH=texsyntax.SYNTAX[syntax]['env_switch']
    k=skip_command_name(i,String)
    if (String[i:i+k] in ENV_SWITCH.keys()):
        return True
    else:
        return False

def is_end_of_env(poz,String,syntax='T'):
    '''Patikrinama ar esama komanda yra env
    pabaiga'''
    i=poz
    ENV_SWITCH=texsyntax.SYNTAX[syntax]['env_switch']
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
    ENV_SWITCH=texsyntax.SYNTAX[syntax]['env_switch']
    METABRACES=texsyntax.SYNTAX[syntax]['mbraces']
    COMMENT=texsyntax.SYNTAX[syntax]['icomment']
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
    right=METABRACES[String[i]] 
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

def check_matching_env(poz,String,env_pav,syntax='T'):
    '''Tikrinama ar esamas reiskinys, 
    yra enviromento uzdarymas ar dar vienas 
    atidarantis reiskinys.
    TABULIARE GALI BUTI TABULIARAS
    TACIAU KOMENTE NEGALI BUTI KOMENTO
    AR VERBATIME VERBATIMO
    Grazina: ('left' arba 'right', reiskinio ilgi)'''
    METACH=texsyntax.SYNTAX[syntax]['metach']
    if not metachar(poz,String,syntax):
        return False
    if not is_start_of_cmd(poz,String,syntax):
        return False
    if  is_start_of_env(poz,String,syntax):
        # print("enviromento pradzia")
        # PRIELAIDA: VERBATIMINIO TIPO ENVIROMENTUOSE
        # NEGALI BUTI NESTED TIPO STRUKTURU SUDARYTU
        # IS TO PACIO ENVIROMENTO
        if syntax=='V':
            return False
        else: delim='left'
    elif is_end_of_env(poz,String,syntax):
        # print("enviromento pabaiga")
        delim='right'
    else: return False
    if collect_enviroment_name(poz,String,syntax)[1]!=env_pav:
        return False
    else: 
        return collect_enviroment_name(poz,String,syntax)[0], delim 

def is_strict_switch(poz,String,syntax='T'):
    '''Patikrina ar esamas reiskinys yra switchas.
    Jei taip grazina jo ilgi.'''
    keys=texsyntax.SYNTAX[syntax]['switches'].keys()
    values=[i for i,j in texsyntax.SYNTAX[syntax]['switches'].values()]
    k=skip_command_name(poz,String,syntax)
    if (String[poz:poz+k] in keys) or\
       (String[poz:poz+k] in values):
       return True
    else: return False
    
def check_matching_switches(poz,String,switch,syntax='T'):
    '''Tikrina ar esamas reiskinys yra griezto switcho 
    uzdarymas ar dar vienas atidarymas.'''
    METACH=texsyntax.SYNTAX[syntax]['metach']
    SWITCHES=texsyntax.SYNTAX[syntax]['switches']     
    if not metachar(poz,String,syntax):
        return False
    if not is_start_of_cmd(poz,String,syntax):
        return False
    if not is_strict_switch(poz,String,syntax):
        return False
    else:
        k=skip_command_name(poz,String,syntax)
        if String[poz:poz+k]==switch:
            return False
            # return k,'left'
        elif String[poz:poz+k]==SWITCHES[switch][0]:
            return k,'right'

def check_mathcing_braces(poz,String,char='{',syntax='T'):
    '''Tikrina ar esmas charas yra uzdarantis ar 
    atidarantis.'''
    i=poz
    keys=texsyntax.SYNTAX[syntax]['braces'].keys()
    values=[i for i,j in texsyntax.SYNTAX[syntax]['braces'].values()]
    # jei ieskosime metaskliaustu
    # idedamas tikrinimas ar neeskeipintas charas
    BRACES=texsyntax.SYNTAX[syntax]['braces']
    if (String[poz]!=char) and (String[poz]!=BRACES[char][0]):
        return False
    # JEI ieskomas charas yra metacharas
    # butina patikrinti ar jis ir yra
    # metacharas ir ar neeskeipintas
    if 'meta' in BRACES[char]:
        check=lambda i,String,syntax : metachar(i,String,syntax)
    # JEI ne tai tik tikrinam ar neeskeipintas 
    else: 
        check=lambda i,String,syntax : not escaped(i,String,syntax)
    if check(i,String,syntax):
         if String[poz]==char:
             # return ('left',1)
             return False
         else:
             return (1,'right')



         
# ESAMAME LYGMENYJE KELIAUJAMA PO CHARA KOL SUTINKAMAS ESAMOS
# SINTAKSES METACHARAS, SUTIKUS PARENKAMAS ATITINKAMAS ALGORITMAS 
# ESAMOJE SINTAKSEJE. 

# TEKSTINEJE MODOJE JEI SUTINKAMAS '%' SURENKAMAS I KOMENTARAS
# SU TRAILING WHITESPACE IR NUSOKAMA I PIRMA NEKOMENTARO SIMBOLI

# JEI SUTINKAMA KOMANDA PATIKRINAMA AR YRA KAS NORS ZINOMA APIE JA.
# JEI TA KOMANDA YRA KOMANDA SU ARGUMENTAIS SURINKINEJAMI ARGUMENTAI
# VIDUJE JU PARENKANT ATITINKAMA SINTAKSE

# JEI TAI GRIEZTAS SWITCHAS SURENKAMAS JO TURINYS ATITINKAMAI PARENKANT
# SINTAKSE VIDUJE

# JEI TAI ENVIROMENTAS SURENKAMAS JO TURINYS, ATITINKAMAI PARINKUS JO 
# SINTAKSE VIDUJE 


def skip_text(poz,String,syntax='T',address=[0]):
    '''Surenkamas visas tekstas, kuris
    nera aktyvuotas aktyviais simboliais.'''
    i=poz
    while not metachar(i,String,syntax):
        if EOS(i,String):
            break
        i+=1
    return i-poz
        
# Apibreziami metodai, ir opcionaliai
# tagai
def collect_name_and_choose(poz,String,syntax):
    '''Sutikus komanda aktyvuojanti symboli,
    surenkamas komandos pavadinimas ir parenkamas
    tolimesnis rinkimo algoritmas'''
    pass

def choose_checking(opening,syntax='T'):
    '''Parenka modos uzdarymo tikrinimo mechanizma!!!
    Grazina funkcija, kuria bus tikrinama!'''
    BRACES=texsyntax.SYNTAX[syntax]['braces']
    SWITCHES=texsyntax.SYNTAX[syntax]['switches']
    ENVIROMENTS=texsyntax.SYNTAX[syntax]['enviroments']   
    if opening in BRACES.keys():
        return lambda poz, String:\
           check_mathcing_braces(poz,String,opening,syntax)    
    elif opening in ENVIROMENTS.keys():
        return lambda poz, String:\
           check_matching_env(poz,String,opening,syntax)           
    elif opening in SWITCHES.keys():
        return lambda poz, String:\
           check_matching_switches(poz,String,opening,syntax)
    else: 
        raise AlgError("Reiskinys, kurio uzdarymo ieskoma:\n{}\n"\
             "neapibreztas, nei tarp metaskliaustu:\n{}\n"\
             "nei tarp enviromentu:\n{}\n"\
             "nei tarp grieztu switchu:\n{}"\
             "\n".format(opening,BRACES),0)


def parse(String,syntax='T',opening=None,address=[0]):
    '''Surinkinejamas teskstas iki tol, kol
    kol bus sutiktas esamos modos uzdarymo 
    reiskinys!'''
    SYNTAX=texsyntax.SYNTAX[syntax]
    # JEI REIKIA TIKRINTI, KADA UZSIBAIGS MODA
    # REIKIA NURODYTI CHECK MECHANIZMA
    if opening:
        checkas=choose_checking(opening,syntax)
    else:
        checkas=lambda x,y:False
    i=0
    nr=0
    while True:
        if EOS(i,String):
            print("PABAIGA")
            break
        try:
            if not metachar(i,String,syntax):
                nr+=1
                # print("\nSKIP_TEXT:",address)
                # print("CHR:",String[i])
                k=skip_text(i,String,syntax,address+[nr])
                # print("SKIP_TEXT_END:")
                i+=k
                # print("CHR:",String[i],'\n')
                continue
            else:
                if checkas(i,String):
                    return i+checkas(i,String)[1]
                else:
                    nr+=1
                    # print("\nDO_WHAT_IS_RIGHT:",address)
                    # print("CHR:",String[i])
                    k=do_the_right_thing(i,String,syntax,opening,address+[nr])
                    i+=k
                    # print("DONE:")
                    # print("CHR:",String[i])
                    continue
        except EOSError:
            print("\n\nPASIBAIGE!!!")

def parse_braced(poz,String,syntax,Address):
    "Paduodama eilute uz skliausto pozicijos."
    # print("PARSINU APSKLIAUSTA")
    i=poz
    
    if taginam:
        print('{',end='')
        
    k=parse(String[poz+1:],syntax,opening='{',address=Address)

    if taginam:
        print('}',end='')
    
    return k+1



METHODS={'icomment':[skip_comment,'comment'],
         'tcommand':[collect_name_and_choose,'cmd_nm'],
         'mbraces':[parse_braced,'braces']}

def do_the_right_thing(poz,String,syntax='T',opening='?',address=[0]):
    '''Jei esamas charas yra metacharas,
    apibreztoje syntakseje, iskviecia
    reikalinga algoritma. Ir grazina ilgi 
    skriptinio teksto, kuris buvo suparsintas.'''
    METACHARS=texsyntax.SYNTAX[syntax]['metach']
    if metachar(poz,String,syntax):
        # PARENKAMAS METODAS
        method=METHODS[METACHARS[String[poz]]][0]
        tipas=METHODS[METACHARS[String[poz]]][0]

        if taginam:
            print('<'+tipas+str(address)+'@->',end='')
            
        k=method(poz,String,syntax,address)

        if taginam:
            print('<-@'+tipas+str(address)+'>',end='')
            
        return k, tipas
    else:

        if taginam:
            print('<'+tipas+str(address)+'@->',end='')
        k=skip_text(poz,String,syntax)
        
        return k, tipas
                
        

textas='''aaaaaa {aaaaa}  bbbbbbbbbb {{ bbbbb {ddddd} eeee}} cccccc'''

taginam=True
parse(textas)
    
    


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
    

         
def find_match(poz,String,syntax='T'):
    '''IESKOMA SUPORUOTO REISKINIO, 
    ATITINKAMAI KVIECIANT SITA PACIA 
    FUNKCIJA PAIESKOS PROCESE!
    - verbatiminiai komandu argumentai
    - verbatiminiai enviromentai
    - verbatiminiai griezti switchai
    Apejimas atliekamas, naudojant taip pat sita 
    funkcija.'''
    # PIRMA NUSTATOMA, KA APIEDINESIM
    # KREIPIANTI I FUNKCIJA NURODOMA VIDUJE 
    # SUPORUOTU REISKINIU ESANTI SYNTAKSE
    METACHARS=texsyntax.SYNTAX[syntax]['metach']
    pass
    
    
        

            
# ######################################## 
# ########################################     
# test_dir=os.path.join(os.path.curdir,'test/')
# list_of_files=os.listdir(test_dir)
# list_of_files=[os.path.join(test_dir,a) for a in list_of_files]
# print()
# for fn in list_of_files:
#     if fn[-10:]!='testas.tex': continue
#     with open(fn,'rt',encoding="ascii") as failas:
#         textas=failas.read()
#         i=0
#         try:
#             while True:
#                 k=do_the_right_thing(i,textas)
#                 i+=k
#         except EOSError:
#             print("DARBAS BAIGTAS")
#             failas.close()
#         except IndexError:
#             print("DARBAS BAIGTAS")
#             failas.close()


def skip_braced(poz,String,
                meta=True,
                verb=False,
                COMMENT_SYNTAX=texsyntax.COMMENT,
                METACHARACTERS=texsyntax.METACHARACTERS):
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
        COMMENT_SYNTAX=texsyntax.COMMENT
        if meta:
            DELIMETERS=texsyntax.ARG_DELIMS
        else:
            DELIMETERS=texsyntax.BRACES
        # jei apskliaustas reiskinys yra
        # verbatimine aplinka, ir procento zenklas nereiskia 
        # komentaro pradzios
        if verb:
            del COMMENT_SYNTAX['%']
        i=poz
        char=String[poz]
        if (char in texsyntax.DELIMETERS.keys()) and metachar(poz,String):
            left=String[poz]
            right=texsyntax.ARG_DELIMS[left]
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


            
def find_matching(poz,String,syntax='T'):
    '''Suranda suporuota reiskini,
    supranta ar ieskoti:
    - metaskliaustu
    - ar griezto switch
    - ar enviromento.
    Ieskodamas apeina inline komentarus,
    inline verbatimus ir kitas komentarines ir 
    verbatimines aplinkas.'''
    # NUSTATYMAS KO IESKOSIM IR KAS BUS ATIDARANTYS
    # IR UZDARANTYS REISKINIAI
    

            

        
# def is_verbatim(poz,String,VERB=texsyntax.VERB):
#     '''Patikrina ar esama komanda yra
#     verbatimines aplinkos pradzia.
#     Grazina: 
#     i-jei inline verbatimas
#     e-jei enviromentas
#     s-jei grieztas switchas'''
#     if not is_start_of_cmd(poz,String):
#         return False
#     k=skip_command_name(poz,String)
#     if String[poz:poz+k] in VERB.keys():
#         return VERB[String[poz:poz+k]]
#     else: return False
    



    



    




        
############## DEMONSTRACIJA 
test_dir=os.path.join(os.path.curdir,'test/')
list_of_files=os.listdir(test_dir)
list_of_files=[os.path.join(test_dir,a) for a in list_of_files]
for fn in list_of_files:
    if fn[-8:]!='test_nereik.tex': continue
    with open(fn,'rt',encoding="ascii") as failas:
        textas=failas.read()
        i=0
        try:
            while True:
                textas[i]
                ###################################
                # komentaru parsinimo demonstracija
                if (i<3357):
                    i+=1
                    continue
                    if is_start_of_comment(i,textas):
                        k=skip_comment(i,textas)
                        print(context(i,textas,End=i+k,Tag='C',Range=0,Delim=''),end='')
                        i+=k
                        continue
                    else:
                        print(textas[i],end='')
                        i+=1
                        continue
                ###################################
                # komandu atpazinimo demonstracija
                # komandos vardo pradzia
                if (i>=3357) and (i<3844):
                    # skipinimui
                    i+=1
                    continue
                    if is_start_of_cmd(i,textas):
                        print(context(i,textas,End=i+k,Range=0,Delim=''),end='')
                        i+=k
                        continue
                    else:
                        print(textas[i],end='')
                        i+=1
                        continue
                # komandos vardas 
                if (i>=3844) and (i<3992):
                    i+=1
                    continue 
                    if is_start_of_cmd(i,textas):
                        k=skip_command_name(i,textas)
                        print(context(i,textas,End=i+k,Tag='NoC',Range=0,Delim=''),end='')
                        i+=k
                        continue
                    else:
                        print(textas[i],end='')
                        i+=1
                        continue
                ################################
                # inline verbatimai 
                if (i>=3992) and (4554>i):
                    i+=1
                    continue 
                    if is_verbatim(i,textas):
                        k=skip_inline_verbatim(i,textas)
                        print(context(i,textas,End=i+k,Tag='V',Range=0,Delim=''),end='')
                        i+=k
                        continue
                    else:
                        print(textas[i],end='')
                        i+=1
                        continue
                ############################## 
                # kelione iki argumento
                if (i>=4554) and (5119>i):
                    if is_start_of_cmd(i,textas):
                        k=skip_command_name(i,textas)
                        name=textas[i:i+k]
                        print(name,end='')
                        i+=k
                        i+=skip_till_argument(i,textas)
                        continue
                    else:
                        print(textas[i],end='')
                        i+=1
                        continue

                i+=1
        except EOSError:
            print("DARBAS BAIGTAS")
            failas.close()
        except IndexError:
            print("DARBAS BAIGTAS")
            failas.close()


        
def skip_braced_verb(poz,String,left='{',right='}'):
        '''Grazina apskliausto reiskinio ilgi.
        Reiskinyje netikrinamas komentaru buvimas'''        
        i=poz
        if left=='{':
            if EOS(i,String):
                raise EOSError(
                        "Tekstas baigiasi, ten kur "\
                        "turetu buti pagrindinis argumentas!".format(
                                context(i,String)),i)
        i+=1
        braces=[1,0]
        while not braces[0]==braces[1]:
            if (String[i] in (left+right)) and metachar(i,String):
                if String[i]== left: 
                    braces[0]+=1
                elif String[i]==right:
                    braces[1]+=1
            if braces[0]==braces[1]: break
            if  EOS(i,String):
                raise MatchError(
                    'Nerasta skliausto pora:\n{}'.format(
                        context(poz,String)),poz)
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
    elif String[poz] in texsyntax.ARGUMENT:
        i+=1
    else: 
        raise AlgError(
            "Turejo buti "\
            " pagrindinis argumentas:\n".format(context(i,String)),i)
    return i-poz

def skip_argument_verb(poz,String):
    '''Surenkamas komandos argumentas,
    kurio turinys verbatiminis.'''
    i=poz
    if String[poz]=='\\':
        raise ParseEroor(
            "Esamas argumentas turetu buti apskliaustas"\
            "nes jo turinys verbatim tipo".format(
                context(i,String),i))
    elif String[poz]=='{':
        # NEBEIGNORUOJAM KOMENTARU ARGUMENTE 
        i+=skip_braced_verb(i,String)
    elif String[poz] in texsyntax.ARGUMENT:
        raise ParseEroor(
            "Esamas argumentas turetu buti apskliaustas"\
            "nes jo turinys verbatim tipo".format(
                context(i,String),i))
    else: 
        raise AlgError(
            "Turejo buti "\
            " pagrindinis argumentas:\n".format(context(i,String)),i)
    return i-poz

    
def collect_command(poz,String):
    '''Surenka komanda, su jos argumentais, jei komandos
    argumentas yra verb tipo tai netikriname, komentaru buvimo
    ir pasiimame iki uzdarancio skliausto.

    Jei komanda turi comment tipo argumenta, velgi sokama
    i uzdaranti skliausta.'''
    komanda=''
    args=[]
    i=poz
    
    ilg=skip_command(i,String)
    komanda=String[i:i+ilg]
    i+=ilg
    print('\n\n')
    print("KOMANDA:",komanda)
    print("POZICIJA:", context(i,String))

    # susirenkam zvaigzdute
    # ji atsiskiria nuo komandos kaip ir argumentas
    if komanda[-1:]!='*':
        ilg=skip_till_argument(i,String)
        if String[i+ilg]=='*':
            komanda=komanda+'*'
            i+=ilg+1
            print("surinkau komanda su zvaigzdute\n"\
            "dabartine mano pozicija:{}".format(
                context(i,String)))
            print("KOMANDASUZV:",komanda)
            
        else:
            pass
    
    print("Pradedu rinkti argumentus:\n",context(i,String)) 
    pattern=texsyntax.COMMANDS.get(komanda,None)
    print("Paternas:",pattern)
    if not pattern:
        args=None
    else:
        print("Si komanda turi paterna!!!")
        print("ESAME:",context(i,String))
        for nr,k in enumerate(pattern):
            # jei komandos argumentas verb tipo
            if komanda in texsyntax.VERB_ARGS.keys():
                print("Si komanda turi verbatiminiu argumentu")
                if texsyntax.VERB_ARGS[komanda][nr]:
                    skip=skip_argument_verb
                else: skip=skip_argument
            else: skip=skip_argument
            
            if k:
                print("ieskom pagrindinio argumento:\n",
                      context(i,String))
                ilg=skip_till_argument(i,String)
                i+=ilg
                print("pagrindinio argumento pradzia:\n",
                      context(i,String))

                ilg=skip(i,String)
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
                    args.append(None)
                    pass
                
    return i-poz, komanda, args, String[poz:i], (poz,i)

def cmd_type(poz,String):
    '''Grazinamas komandos tipas, patikra vyksta 
    nuo \\. 
    
    Return: (tipas,tipo_patenas)'''
    i=poz
    i+=skip_command(poz,String)
    if String[poz:i] in texsyntax.ENV_START:
        print(collect_command(poz,String))
        return 'envstart', collect_command(poz,String)[2][0]
    elif String[poz:i] in texsyntax.ENV_END:
        return 'envend', collect_command(poz,String)[2][0]
    elif String[poz:i] in texsyntax.SWITCH:
        return 'switch', None
    elif String[poz:i] in texsyntax.STRICT_SWITCH.keys():
        return 'strictswitch',texsyntax.STRICT_SWITCH[String[poz:i]]
    elif String[poz:i] in texsyntax.COMMANDS.keys():
        return 'command', texsyntax.COMMANDS[String[poz:i]]
    else: return None


################# PRISTATYMUI ##########
######################################## 

#################### METACHARU TIKRINIMAS ##########
# for fn in list_of_files:
#     with open(fn,'rt',encoding="ascii") as failas:
#         textas=failas.read()
#         for i,j in enumerate(textas):
#             if metachar(i,textas):
#                 print(context(i,textas))
#                 input()        

  
# # #############INLINE KOMENTARU TESTINIMAS
# test_dir=os.path.join(os.path.curdir,'test/')
# list_of_files=os.listdir(test_dir)
# list_of_files=[os.path.join(test_dir,a) for a in list_of_files]
# for fn in list_of_files:
#     if fn[-8:]!='test.tex': continue
#     with open(fn,'rt',encoding="ascii") as failas:
#         textas=failas.read()
#         i=0
#         try:
#             while True:
#                 if is_start_of_comment(i,textas):
#                     k=skip_comment(i,textas)
#                     print(context(i,textas,End=i+k,Tag='komentaras'))
#                     input()
#                     i+=k 
#                 i+=1
#         except IndexError:
#             print("DARBAS BAIGTAS")
#         except EOSError:
#             print("DARBAS BAIGTAS")

