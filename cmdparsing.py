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

import texsyntax

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
        ltag=delim+'<'+Tag+'@@@>'+delim
        rtag=delim+'<@@@'+Tag+'>'+delim
    else:
        delim=''
        ltag=' @@@>>'
        rtag='<<@@@ '
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

def escaped(poz,String,ESC_CH=texsyntax.METACHAR_ESC):
    '''Patikriname ar esamas charas 
    nera escapintas.'''
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

def metachar(poz,String,META_CH=texsyntax.METACHARACTERS):
    '''Jei charas yra metacharu sarase, 
    tai patikrinam ar jis neeskeipintas.'''
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
    nera eilutes pabaiga. 
    !!! SUGALVOTI, KAIP OPTIMIZUOTI'''
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

def is_start_of_comment(i,String,COMMENT=texsyntax.COMMENT):
    '''Patikriname ar esamas charas yra komentaro
    pradzia. 
    Jei taip grazina: 
    (chara kuris isjungs komentara, opciju rinkini)'''
    if (String[i] in COMMENT.keys()) and metachar(i,String):
        return COMMENT[String[i]]
    else: return False
           
def skip_comment(poz,String,COMMENT=texsyntax.COMMENT):
    '''Nuskaitomas komentaras ir grazinamas jo ilgis.
    Skaitoma tada, kai komentaro jungiklis yra metachar'''
    if is_start_of_comment(poz,String,COMMENT):
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
                else: return i-poz
        else: return i-poz

def is_start_of_cmd(poz,String,                  
                    START_OF_CMD=texsyntax.START_OF_CMD,
                    COMMAND_CHARS=texsyntax.COMMAND_CHARS):
    '''Patikrinama ar esamas charas yra komandos pradzia.'''
    if not (String[poz] in START_OF_CMD.keys()):
        return False
    else:
        if metachar(poz,String): return True
        else: return False

def skip_command(poz,String,
                 START_OF_CMD=texsyntax.START_OF_CMD,
                 COMMAND_CHARS=texsyntax.COMMAND_CHARS):
    '''Padavus esama \\ pozicija 
    (\\ gali buti perapibreztas)
    ir tikrinama stringa grazina komandos ilgi.'''
    # patikriname ar esamas charas yra komandos
    # pradzios metacharas
    char=String[poz]
    if not is_start_of_cmd(poz,String):
        raise AlgError("Tai nera komanda aktyvuojantis simbolis:"\
                       "\n{}".format(context(i,String)),poz)
    elif not START_OF_CMD[char]:
         raise AlgError(
                      "Pakeista komandos aktyvavimo sintakse "\
                      "ir nenumatyta elgsena!!!:"\
                      "\n{}Komanda aktyvuojanciu charu sarasas"\
                      ":\n{}".format(context(poz,String),
                                      START_OF_CMD),poz)
    else: pass
    # Jei netycia parsinama eilute uzsibaigtu \\
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
            # jei netycia komanda uzbaigtu stringa
            raise EOSError("Renkant komanda buvo pasiektas teksto galas. "\
                           "\nPries parsinant gale idekite papildoma newline,"\
                           "arba naudokite try:\n".format(context(i,String),i))
        i+=1
    return i-poz

# ############# Komandos vardu atpazinimas 
test_dir=os.path.join(os.path.curdir,'test/')
list_of_files=os.listdir(test_dir)
list_of_files=[os.path.join(test_dir,a) for a in list_of_files]
for fn in list_of_files:
    if fn[-8:]!='test.tex': continue
    with open(fn,'rt',encoding="ascii") as failas:
        textas=failas.read()
        i=0
        try:
            while True:
                textas[i]
                # komentaru parsinimo demonstracija
                if (i<3284):
                    if is_start_of_comment(i,textas):
                        k=skip_comment(i,textas)
                        print(context(i,textas,End=i+k,Tag='COMMENT',Range=0))
                        i+=k
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
    
            
    
def skip_till_argument(poz,String,BEGIN_OF_ARG=texsyntax.BEGIN_OF_ARG):
    '''Praleidzia visus, nereiksmingus
    charus iki sekancio argumento.
    Tarp komandos ir argumento galimi tik 
    iprastiniai komentarai \'%\'.'''
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
        if EOS(i,String):
            raise EOSError(
                "Parsinamas tekstas baigiasi "\
                "komanda, kuri turi tureti argumenta:"\
                "\n{}".format(context(i,String)),i)
        else: raise AlgError(
                "Nenumatytas charas tarp argumentu:\n"\
                "{}".format(context(i,String)),i)
    return i-poz
   
def skip_braced(poz,String,meta=True,verb=False,
                COMMENT_SYNTAX=texsyntax.COMMENT):
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

