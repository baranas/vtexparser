'''Automatonas skaidantis teksta i triju rusiu eilutes:
comment, verbatim ir other'''
try:
    if __IPYTHON__:
        if sys.platform=='win32':
            os.chdir('d:/Luko/vtexparser/')       
        else:
            sys.path.append('/home/lukas/vtexparser/')
except:
    pass

import string, sys, os 
import cmdparsing

VERB_CMD={'\\verb','\\xymatrix','\\index'}
VERB_ENV={'listing','Verbatim','verbatim'}
###### fikcines komandos ########
VERB_SWCH={{'\\verbon':'\\verbof'}}
COMMENT_CMD={'\\commentcmd'}
#################################
COMMENT_ENV={'comment'}
COMMENT_SWCH={{'\\comment':'\\endcomment'}}

def collectcommand(poz,String):
    '''Automatone padavus esama pozicija, 
    kurioje yra sliashas ir darbini stringa
    funkcija keliauja i prieki ir surenka komanda.

    Grazina komandos pav, ilgi ir paskutinio 
    simbolio pozicija paduoto stringo atzvilgiu.

    Tikrina komandas parsaytas tik ASCII.'''
    command=['\\']
    i=poz+1
    # jei netycia tekstas uzsibaigtu slashu
    try:
        # jei komanda ne is alfabeto
        if not (String[i] in string.ascii_letters):
            return String[poz:poz+2], 1, i
    except IndexError:
        return String[poz]
    
    while String[i] in string.ascii_letters:
        command.append(String[i])
        i+=1
        # jei komanda uzbaigia teksta
        try:
            String[i]
        except IndexError:
            break
    return ''.join(command), i-1, i-poz-1 

    

    

def switch_check(char,text,Poz,SWITCH):
    '''Tikrina ar esamas charas  nera perjungimas 
    i kita moda.

    Modos triju tipu:
    1.noncomment
    2.text
    3.verbatim

    Taip pat:
    Suskaiciuoja, kiek charu esama moda tesiasi i prieki.
    (Pvz.: komentaras suvalgo visus whitespace po saves).

    Verbatimo aplinkos pabaiga skaito pirmaji skirtuka,
    grazindama skip viso argumento su galiniu skirtuku ilgi.

    Returnas: (persijungia komentaras, persijungia verbatimas)
    '''
    global WHITESPACE, VERB

    try:
        text[Poz+1]
    except IndexError:
        return 1,0
        
    # jei esama moda komentaras, galim
    # rasti tik komentaro pabaiga
    if SWITCH[0]:
        if char != '\n':
            return False, False
        elif char == '\n':
            # suskaiciujam besitesencius whitespace
            white=0; 
            while text[Poz+white+1] in WHITESPACE:
                white+=1
            if text[Poz+white+1]=='%': return False, False
            else: return 2+white, False          # nes \n comment dalais

    # jei esama moda verbatimas, galim 
    # rasti tik verbatim pabaiga
    elif SWITCH[1]:
        # jei esamas charas ne alpha tai ieskom
        # kito tokio pat charo
        if not (char in string.ascii_letters):
            delimeter=char
            verb=0;
            while text[Poz+verb+1] != delimeter:
                verb+=1
            return False, 3+verb
        else: return False, False

    # jei esama moda nera nei komentaras nei verbatimas
    # galim rasti arba komentara arba verbatima 
    else:
        returnas=[]
    # IESKOM KOMENTARO
        try:
            if char == '%' and text[Poz-1]!='\\':
                return 1, False
        except IndexError:
            if char == '%':
                return 1, False
            else:
                pass

    # IESKOM VERBATIMO
        if char != '\\':
            return False, False
        else:
            # print('radau slasha', char)
            komanda=collectcommand(Poz,text)
            # print('radau komanda',komanda[0])
            if komanda[0] in VERB:
                # print('tai yra verbas')
                return False, 1                 
            else:
                # print('ne tai nera verbas')
                return False, False
            
     
              
        
    


        
        

def ParseVerbComments(text):
    '''Suparsinama duota eilute iskiriant
    komentarus ir verbatimus'''
    parsed=[]
    elem=[]
    # Pradines salygos 
    COMMENT, VERBATIM = False, False
    SWITCH=[False,False]
    skip=[None, None]
    for poz,char in enumerate(text):
        # Jei skipas turi ne None reiksme       
        if skip[0] or skip[1]:
            if skip[0]: k=0
            elif skip[1]: k=1
            skip[k]-=1
            if not skip[k]: 
                parsed.append(((SWITCH[0],SWITCH[1]),''.join(elem)))
                elem=[]
                SWITCH[k]=False if SWITCH[k] else True
            elem.append(char)
            # print(char,check)
            # print(repr(char), COMMENT,'skipinu')
            continue
        
        check=switch_check(char,text,poz,SWITCH)
        # print(char,check)
        
        if check[0] or check[1]:
                if check[0]: k=0
                elif check[1]: k=1
                if check[k]==1:
                    parsed.append(((SWITCH[0],SWITCH[1]),''.join(elem)))
                    elem=[]
                    SWITCH[k]=False if SWITCH[k]==True else True
                else:
                    skip[k]=check[k]-1
        elem.append(char)
        # print(SWITCH,char)
        # print(repr(char), COMMENT)
    if not parsed:
        raise TypeError('Nepavyko suparsinti teksto')

    # Reiks pataisyt algoritma, kad sito nereiktu
    if not parsed[0][1]:
        del parsed[0]
    
    return parsed
         

if __name__=='__main__':
    if sys.platform=='win32':
        failas=open('d:/test/test.tex','rt')
    else:
        failas=open('/home/lukas/programavimas/cparse/test/test.tex','rt')
    parsed=ParseVerbComments(failas.read())
    failas.close()


def printinfo(elem):
    if elem[0][0]:
        print('\n'+'-'*15,'\n(KOMENTARAS:)')
        print(elem[1],end='')
    elif elem[0][1]:
        print('\n'+'-'*15,'\n(VERBATIMAS:)')
        print(elem[1],end='')
    else:
        print('\n'+'-'*15,'\n(TEKSTAS:)')
        print(elem[1],end='')

        


if __name__ == '__main__':
    for elem in parsed:
        printinfo(elem)
