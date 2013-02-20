import string, sys, re, os

if __IPYTHON__:
    if sys.platform=='win32':
        os.chdir('d:/Luko/emacs/programavimas/Projektas/CTVparsingas/')       
    else:
        sys.path.append('/home/lukas/programavimas/Projektai/CTV/')

import parseCTV 

METACHARACTERS={'#','$','%','^','{','}','_','~','\\'}
CONVERTED_METACH={'#':'\\#',
                  '$':'\\$',
                  '%':'\\%',
                  '^':'\\^{}',
                  '{':'\\{',
                  '}':'\\}',
                  '_':'\\_',
                  '~':'\\~',
                  '\\':'\\textbackslash '}


class Elementas():
    '''Abstrakciausias objektas NUOSEKLIAME parsinime
    su turiniu ir rodyklemis i pries ir po greta esancius
    elementus.'''
    def mytype(self):
        return 'elementas'

    def syntax_repr(self):
        '''Saves reprezentacija
        sintakses analizei'''
        return self.body

    def context_repr(self):
        '''Saves reprezentacija statistinems 
        paieskoms'''
        return self.body

    def formated_repr(self):
        '''Pagrazinta reprezentacija''' 
        return self.body
    
    def __init__(self,text,Pp=None,Np=None,Pst=None,Nst=None):
        '''inicializacijai paduodamas turinys, nuoroda
        i pries tai einanti objekta ir po jo.
        Taip pat galima priskirti nuorodas i gretutinius
        same-type objektus.'''
        self.body=text
        self.pp=Pp; self.np=Np            # rodykles i gretutinius elementus
        self.nst=Nst; self.pst=Pst        # rodykles i gret. same-type elementus
        self.poz=[None,None]              # Poz. txt. su komentarais atzvilgu
        self.pozst=[None,None]            # Poz. txt. be komentaru atzvilgiu
        self.points=[]                    # taskai priskiriami elementui
 
    def __str__(self):
        '''Informacija gaunama naudojant print f-ija'''
        return "\n"+"-"*10+"\nType: {}\n".format(self.mytype())+\
          "-"*10+ "\nBody:\n{}".format(self.body)
        
    def getlock(self):
        '''Gauna esamo elemento paskutinio simbolio 
        pozicija, uzfiksuojant ir pirma, viso teksto atzvilgiu.
        Tuo paciu uzfiksuodama visu pries tai buvusiu
        elementu pirmu ir paskutiniu elementu pozicijas.'''
        if self.pp==None:
            self.poz[1]=[0,len(self.body)-1]          
        else:
            self.poz=[self.pp.getlock()+1,self.begin+len(self.body)-1]
        return self.poz[1]

    def gettypelock(self):
        '''Gauna esamo elemento paskutinio simbolio 
        pozicija to paties tipo teksto  atzvilgiu
        tuo paciu uzfiksuodama visu pries tai buvusiu
        elementu pirmu ir paskutiniu elementu pozicijas.'''
        if self.pst==None:
            self.pozst=[0,len(self.body)-1]          
        else:
            self.pozst=[self.pst.gettypelock()+1,self.beginst+len(self.body)-1]
        return self.pozst[1]

    def addpoint(self,point):
        '''Tasko priskyrimas elementui''' 
        self.points.append(point)

    def split(self, point):
        '''Skeliamas elementas per paduota taska,
        grazinami du tarpusavyje sujungti elementai.
        Skelimo taskas priskiriamas antram elementui.
        Taskas yra charo pozicija, nuo elemento pradzios.'''
        elem1, elem2=__class__(self.body[:point]),__class__(self.body[point:])
        elem1.pp, elem2.np, elem1.pst, elem2.nst = self.pp, self.np, self.pst, self.nst
        elem1.np=elem1.nst=elem2
        elem2.pp=elem2.pst=elem1
        # Pakeiciam elementu rodanciu i 
        # esama elementa nuorodas
        self.pp.np=self.pst.nst=elem1
        self.np.pp=self.nst.pst=elem2

        return elem1, elem2
        
    def endswithlatexcommand(self):
        '''Metodas patikrinantis ar esamas elementas
        baigiasi LaTeX komanda.'''
        if not (self.body[-1] in string.ascii_letters):
            return False
        else:
            i=1
            while self.body[-i] in string.ascii_letters:
                i+=1
            if self.body[-i]=='\\':
                return True

    def newlines(self):
        '''suskaiciuoja, kiek newlinu yra
        stringe'''
        return self.body.count('\n')

    def tex_commands(self):
        '''[TODO]
        Grazina visas latex komandasa.
        esancias elemento kune set pavidalu'''
        command={}
        for i,elem in enumerate(self.body):
            if elem=='\\':
                x=parseCTV.collectcommand(i,self.body)
                tmp=command.get(x[0],0)
                command[x[0]]=tmp+1
        return command

    
                

class Comment(Elementas):
    '''Komentaro tipo elementas, turintis savyje
    informacija apie pati komentara.

    format metodas nustato esamo komentaro tipa 
    ir ji pakeicia'''
    
    def mytype(self):
        '''Tipo identifikavimui.'''
        return 'comment'

    def syntax_repr(self):
        '''Sintaksine saves reprezentacija.
        Si reprezentacija svarbi sintakses analizei'''
        if self.pp.endswithlatexcommand():
            return ' '
        else: return ''

    def context_repr(self):
        return syntax_repr(self)

    def formated_repr(self):
        '''Pagrazinta reprezentacija''' 
        if self.pp.starts_newline():
            return '%\n'
        else: return ''
    
    def __init__(self,text,Pp=None,Np=None,Nst=None,Pst=None):
        super().__init__(text,Pp=None,Np=None,Nst=None,Pst=None)

    
    def starts_newline(self):
        '''Nustato ar esamas komantaras prasideda 
        nauja eilute texiname faile.'''
        if not self.pp: return True
        if (type(self.Pp)==type(self)):
            return True
        else:
            if self.pp.body[-1]=='\n':
                return True
            else: return False

    # def is_multiline(self):
    #     '''Nustato ar esamas komentaras
    #     tesiasi per keleta eiluciu.'''
    #     if self.newlines>1:
    #         return True
        
    # def is_informative(self):
    #     '''Nustato ar komentare yra raidziu,
    #     tai yra ar jis atlieka kokia nors funkcija 
    #     be lauzymo ir isskyrimo'''
    #     word=re.compile(r'[a-zA-Z0-9]')
    #     if word.search(self.body):
    #         return True
    #     else: return False

class Verbatim(Elementas):
    '''Nustatoma ar verbatimas reprezentuoja,
    tik simboli ar jame surasytas tekstas.'''
    def mytype(self):
        return 'verbatim'
        
    def context_repr(self):
        '''Sintaksine saves reprezentacija.
        Si reprezentacija svarbi sintakses analizei.'''
        if not self.body[6:-1]:
            return ''
        else:
            result=[]
            for i in self.body[6:-1]:
                if i in METACHARACTERS:
                    result.append(CONVERTED_METACH[i])
                else: result.append(i)
                    
        return '\\texttt{'+''.join(result)+'}'
                
    def syntax_repr(self):
        return self.context_repr()
 
       

    def formated_repr(self):
        '''Pagrazinta reprezentacija''' 
        if self.pp.starts_newline():
            return '%\n'
        else: return ''

    
    def __init__(self,text,Pp=None,Np=None,Nst=None,Pst=None):
        super().__init__(text,Pp=None,Np=None,Nst=None,Pst=None)





class CTVobject():
    '''Elementu ir tasku konteineris.
    Apibrezti metodai 
    - paieskos tik nekomentaruose.
    - elementu skelimas itakojant visus fiksuotus taskus
    - elementu sukeitimas vietomis keiciant taskus'''

    def check_comments(self):
        '''Patikrina ar greta esantys teksto elementai, 
        tarp kuriu yra komentaras nesulimpa su zalingom 
        pasekmem.

        Jei pirmasis teksto elementas baigiasi LaTeX komanda,
        ir antrasis prasideda zodziu, tokiu atveju i antraji ikeliamas
        whitespace, kad nepasidarytu sulipinus viena ilga LaTeX komanda.

        TODO sugalvoti metoda, kaip islaikyti nuoroda i originalu teksta'''
        for i,elem in enumerate(self.noncomments):
            # Jei esamas elementas baigiasi LaTeX komanda
            if elem.endswithlatexcommand() and elem.nst != None:
                # jei kito noncomments elemento pirmas simbolis raide
                if self.noncomments[i+1].body[0] in string.ascii_letters:
                    self.noncomments[i+1].body=' '+ self.noncomments[i+1].body 
                    # pazymiu, kad yra nukrypimas nuo originalaus tekstinio
                    # failo
                    self.noncomments[i+1].aditionalwhitespace=True
            else: continue

    def type_init(self, type_switch):
        '''Nustato, kokio tipo yra elementas ir 
        grazina atitinkama klase.'''
        if type_switch[0]:
            return Comment
        elif type_switch[1]:
            return Verbatim
        else: return Elementas
            
    def __init__(self, listas):
        '''Inicializacija pasiima lista, apazysta tipa,
        priskiria tipa ir sukonstruoja nuoseklu klases
        Elementai objektu lista, kiekviename elemente
        irasydama nuoroda i pries tai buvusi objekta ir 
        i sekanti.

        Taip pat inicijuojami atskiri tik
        comment ir tik text tipo listai su nuorodomis
        i greta esancius tokio pat tipo elementus.'''
        # Sukuriamas misrus sarasas, nustatant  kiekvieno 
        # elemento tipa
        self.full=[]
        self.types={}
        for i,(check,elem) in enumerate(listas):
            # sukuriamas elementas be rodykliu
            self.full.append(self.type_init(check)(elem))
            
            # Sujungiam gretutinius elementus 
            try:
                self.full[i].pp, self.full[i-1].np = self.full[i-1], self.full[i]                
            except IndexError:
                self.full[i].pp=None
                
            # Sujungiam gretutinius to paties tipo elementus 
            try:
                self.full[i].pst=self.types[self.full[i].mytype()]
                self.types[self.full[i].mytype()].nst=self.full[i]
                self.types[self.full[i].mytype()]=self.full[i]
            except KeyError:
                self.types[self.full[i].mytype()]=self.full[i]

        

    def get_noncomments(self):
        '''Generatorius grazinantis tik elementus,
        kuriuose yra tekstas be komentaru'''
        for i in self.full:
            if i.mytype()!='comment':
                yield i


    def get_clean(self):
        '''Generatorius grazinantis elementus,
        kurie nera nei verbatimas nei komentaras.'''
        for i in self.full:
            if i.mytype!='comment' and i.mytype!='verbatim':
                yield i

    def get_syntax_repr(self):
        for i in self.full:
            yield i.syntax_repr()
                
            
            


if __name__=='__main__':
    if sys.platform=='win32':
        failas=open('test.tex','rt')
    else:
        failas=open('/home/lukas/programavimas/cparse/test/test.tex','rt')


        parsed=parseCTV.ParseVerbComments(failas.read())

        # CIA BRUDAS
        if not parsed[0][1]:
            del parsed[0]

    failas.close()    
    doc=CTVobject(parsed)

print()
    
for i in doc.get_syntax_repr():
    print(i,end='')
    

