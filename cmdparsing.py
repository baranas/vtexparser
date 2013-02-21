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
        
def metachar(poz,String):
    '''Jei charas yra metacharu sarase, 
    tai patikrinam ar pries ji buves simbolis 
    nera \\'''
    if poz==0:
          return True 
    if String[poz] in texsyntax.METACHARACTERS:
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
        return repr('>>'+String[poz]+'<<'+String[poz+1:poz+after])
    else:
        return repr(String[poz-before:poz]+'>>'+String[poz]+'<<'\
                    +String[poz+1:poz+after])
    
def skip_whitespace(poz,String):
    '''Praleidziam visus whitespace,
    grazinam ju ilgi'''
    i=poz
    if not (String[poz] in texsyntax.WHITESPACE):
        raise AlgError(
            'This is not a "\
            "whitespace:\n{}'.format(context(poz,String)),poz)
    while String[i] in texsyntax.WHITESPACE:
        if EOS(i,String): 
            # paliekam viena whitespace
            # kitoms funkcijoms
            return i-poz
        i+=1
    return i-poz

def skip_comment(poz,String):
    '''Nuskaitomas komentaras ir grazinamas jo ilgis.'''
    if not metachar(poz,String):
        raise AlgError('This is not "\
          "a comment:\n{}'.format(context(poz,String)),poz)
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
        elif String[i] in texsyntax.WHITESPACE:
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
        raise AlgError(
            "This is not "\
            "a start of command:\n{}".format(context(poz,String)),poz)
    if metachar_greedy(poz,String): pass
    if EOS(poz,String):
        raise ParseError(
            'String ends with \\:\n{}'.format(context(poz,String)),poz)
    # jei komanda susideda is simbolio
    if not (String[poz+1] in string.ascii_letters):
        return 2
    i=poz+1
    while String[i] in texsyntax.COMMAND_CHARS:
        if EOS(i,String):
            # jei netycia komanda uzbaigtu stringa
            raise EOSError("String ends with command. "\
                           "\nPlease insert whitespace "\
                           "before parsing.".format(context(i,String),i))
        i+=1
    return i-poz
    
def skip_till_argument(poz,String):
    '''Praleidzia visus, nereiksmingus
    charus iki sekancio argumento.'''
    i=poz
    if not(String[poz] in {'\n','%',' ','\t'}):
           return 0
    if String[i] in texsyntax.WHITESPACE:
        i+=skip_whitespace(i,String)
        if String[i]=='\n': 
            i+=1
    if String[i]=='\n':
        i+=1
    while String[i] in {' ','\t','%'}:
        if String[i]=='%':
            i+=skip_comment(i,String)
        elif String[i] in texsyntax.WHITESPACE:
            i+=skip_whitespace(i,String)
        if EOS(i,String):
            raise EOSError(
                "String ends with command,"\
                "that must have argument:\n{}".format(context(i,String)),i)
    return i-poz
           
def skip_braced(poz,String,left='{',right='}'):
        '''Grazina apskliausto reiskinio ilgi.'''        
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
            if String[i]=='%':
                try:
                    i+=skip_comment(i,String)
                except EOSError:
                    raise MatchError(
                        'Nerasta skliausto pora!:\n{}'.format(
                            context(poz,String)),poz)
            if (String[i] in (left+right)) and metachar(i,String):
                if String[i]== left: 
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



          


print()
if __name__=='__main__':
    eil='''\\begin    *    {equation} \\it \\iffalse \\fi \\section   {Tragedija}
\\index{%cia tik argumentas}, \\comentinarg    {CIA KOMENTARAS} \\def\\zodis{verbatim enviromentas\\begin{a}}'''
    for i,char in enumerate(eil):
        if char=='\\' and metachar(i,eil):
            print(collect_command(i,eil))
    


        


    


