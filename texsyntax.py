'''Modulis kuriame aprasytos skirtinga sintaksine prasem turincios 
komandos'''
import string, os, sys

#################### METACHARAI IR JU REIKSMES
##############################################

########### IPRASTINIAI METACHARAI
# Skripto vykdymo metu bus tikrinama ar esamas charas
# nera metacharakteris
# (numatoma galimybe dinamiskai keisti sita aibe)
METACHARACTERS={'#','$','%','^','{','}','_','~','\\','&'}

###### METACHARAKTERIAI SKIRTINGOSE MODOSE
# Metacharo reiksme yra raktinis zodis,
# nurodanti kokio tipo objektas bus inicializuotas
# ir koks algoritmas bus taikomas objekto surinkimui.
#
# Inline verbatimai ir komentarai bus surenkami paprasciau.
#
# Laikui begant sis sarasas bus pildomas analizuojant dazniausiai
# pasitaikancius paketus ir ju aplinkas
# Reikia tureti omenyje, kad paketai gali (nors ir retai) pakeisti
# iprastine sintakse
#
# PRIELAIDA: visi metacharai susidaro is vieno ascii simbolio

# Iprastiniai metacharai iprastinese modose, be paketui.
# skirtingu paketu metacharakteriu sintakse bus papildyta veliau
# ja pajungiant i skripto darba, tada, kai toks paketas bus rastas

METACH={'text':{'$':'math',      # $->imath $$->dmath
                '%':'icomment',
                '{':'mbraces',
                '~':'space',
                '\\':'tcommand',
                # sutikus atidaranti skliausta, bus sokam
                # i chara uz uzdarancio
                # sutikti uzdaranciu negalima
                '}':'error',         
                '#':'error',
                '^':'error',
                '_':'error',
                '&':'error'},
         'math':{'$':'end',
                '%':'icomment',
                '{':'mbraces',
                '~':'space',
                '\\':'mcommand',
                '^':'superscript',
                '_':'subscript',
                '}':'error',         
                '#':'error',
                '&':'error'},
         # kol kas verb vadinsime visas aplinkas,
         # kuriose nereikia gaudyti 
         # -inline komentaru
         # -matematikos 
         # -metaskliaustu  ir t.t. 
         'verb':{'\\':'vcommand'},
         'tabular':{'$':'imath',
                '%':'icomment',
                '{':'mbraces',
                '~':'space',
                '\\':'tabcommand',
                '&':'sep',
                '}':'error',         
                '#':'error',
                '^':'error',
                '_':'error'},
          'array':{'$':'imath',
                '%':'icomment',
                '{':'mbraces',
                '~':'space',
                '\\':'mtabcommand',
                '&':'sep',
                '}':'error',         
                '#':'error',
                '^':'error',
                '_':'error'}}
                

# METACHARO ESKEIPAS
# simbolis kuriam esant pries metachara,
# metacharas igyja kita prasme
# (numatant galimybe dinamiskai keisti)
METACHAR_ESC={'\\':None}
     
# EILUTES Whitespace'ai  
WHITESPACE={' ','\t'}

############################## KOMANDOS 

# METACHARAS REISKIANTIS KOMANDOS PAVADINIMO PRADZIA
# (paliekama vieta opcijoms giliau nagrinejant TeX'o kalba)
START_OF_CMD={'\\':None}
    
# Komanda sudarantys simboliai, * priskirima prie komandos pav 
COMMAND_CHARS=set(string.ascii_letters)
# Sita reiks pakeisti
COMMAND_CHARS.update('*')

########### KOMANDU SU ARGUMENTAIS PATERNAI
# SARASAS NURODANTIS KIEK PAGRINDINIU IR OPCIONALIU ARGUMENTU TURI KOMANDA
# * JEI ARGUMENTU TIPAS NEZINOMAS, 
# NURODOMAS PATTERNAS: 1--pagr argumentas 0--opcionalus
# * JEI ARGUMENTE KEICIASI SINTAKSE (PVZ KOMENTARU)
# NURODOMA DIDZIOJI RAIDE PAGR. ARGUMENTAMS
# MAZOJI OPCIONALIEMS
# * JEI TIKSLIAI ZINOMA KAD, KOMANDOS ARGUMENTAS YRA IPRASTA
#   TEKSTINE MODA 
# RASOMA 'T' PAGR. ARGUMENTAMS, 't' OPCIONALIEMS
# 
# * JEI KOMANDA YRA SYMBOLIS TAI PATERNAAS YRA NONE

# TEKSTINES MODOS KOMANDOS
T_COMMANDS={'\\usepackage':(0,1),
          '\\rule':(0,1,1),
          '\\footnote':(0,'T'),
          '\\newcommand':(1,0,0,1),
          '\\renewcommand':(1,0,0,1),
          '\\def':(1,1),
          '\\label':(1,),
          '\\part':(0,'T'),
          '\\chapter':(0,'T'),
          '\\section':(0,'T'),
          '\\subsection':(0,'T'),
          '\\subsubsection':(0,'T'),
          '\\paragraph':(0,'T'),
          '\\subparagraph':(0,'T'),
          '\\subsubparagraph':(0,'T'),
          '\\subsubsubparagraph':(0,'T'),
          '\\mbox':('T',),
          '\\index':('V',),
          '\\def':(1,1),
          '\\textbackslash':None}

# MATEMATINES MODOS KOMANDOS 
M_COMMANDS={'\\frac':(1,1),
            '\\alpha':None,
            '\\mathbf':(1,)}

# TABBULAR IR ARRAY atitinkamai naudosis tais paciais
# T_COMMANDS ir M_COMMANDS komandu rinkiniais
# tik skirtingai traktuos \\\\ ir prisides keletas
# nauju komandu, tokiu, kaip \\cr, \\eqncr ir t.t.
   
# BEVEIK VISOMS MODOMS BUDINGOS KOMANDOS

##################### ENVIROMENTAI

#### ENV PRADZIOS AR PABAIGOS JUNGIKLIAI
# PALIEKAMA GALIMYBE PAPILDYTI
# SUTIKTAS PAVYZDYS:
# \def{\be}{\begin}
ENV_SWITCH={'\\begin':'\\end'}

############### ENVIROMENTU PATERNAI IR TIPAI
# PIRMAS ARGUMENTAS NURODO PATERNA
# ANTRAS NURODO TURINIO SYNTAKSE
ENVIROMENTS={'equation':[(0,),'M'],
             'pf':[(0,),'T'],
             'pf*':[(1,),'T'],
             'verbatim':[None,'V'],
             'comment':[None,'V'],
             'listing':[None,'V']}

SWITCHES={'\\iffalse':['\\fi','V'],
          '\\comment':['\\endcomment','V'],
          '$$':['$$','M'],                # display TeX trumpinys
          '\(':['\)','M'],                # inline LaTeX trumpinys
          '\[':['\]','M']}                # display LaTeX trumpinys

############### KOMANDU ARGUMENTAI
    

# CHARAI KURIUOS SUTIKUS AISKU, KAD 


############### KOMENTARAI

# NUMATANT SINTAKSES KEITIMA
# METAJUNGIGLIS: (ISJUNGIKLIS, (SAVYBES,))
# w -- reiskia, kad po isjungimo bus suvalgomi whitespace
COMMENT={'%':('\n',('w',))}


############## SUPORUOTI REISKINIAI
# opcijos: 
# meta--butina tikrinti ar
#     neeskeipintas
# None -- vieno simbolio skirtukai
# rpt -- butina patikrinti ar sekantis symbolis nera
#        tas pats
# mch -- sudarytas is daugiau, negu vieno charo
DELIMS={'[':[']',None],
        '(':[')',None],
        '{':['}','meta'],
        '``':["''",''],
        '$':['$','meta','rpt'],}

MULTICHAR_DELIMS={'$$':['$$',None]}

ARG_DELIMS={'{':['}','meta']}

# SKIRTUKAI APGAUBIANTYS PAGRINDINI ARGUMENTA


# KAS BUS ARGUMENTU, JEI TAI NE KOMANDA IR NE APSKLIAUSTAS
# REISKINYS
ARGUMENT=set(string.ascii_letters+string.digits)
# ARGUMENTO PRADZIOS SIMBOLIAI
BEGIN_OF_ARG=ARGUMENT
BEGIN_OF_ARG.update(set(START_OF_CMD.keys()))
BEGIN_OF_ARG.update(set(ARG_DELIMS.keys()))

########################################
####################  SYNTAKSES
######################################## 
# APIBREZIAMOS SKIRTINGOS SYNTAKSES
# KURIOS BUS PERDUODAMOS SKIRTINGOSM 
# MODOMS

SYNTAX={
    # TEKSTINES MODOS SINTAKSE
    'T': {'metach':METACH['text'],
          'cmd_chars':COMMAND_CHARS,
          'cmd_start':START_OF_CMD,
          'escape':METACHAR_ESC,
          'commands':T_COMMANDS,
          'icomment':COMMENT,
          'env_switch':ENV_SWITCH,
          'enviroments':ENVIROMENTS,
          'mbraces':ARG_DELIMS,
          'delims':DELIMS,
          'mch_delims':MULTICHAR_DELIMS,
          'arg_beg':BEGIN_OF_ARG,
          'switches':SWITCHES},
    # MATEMATINES MODOS SINTAKSE
    'M': {'metach':METACH['math'],
          'cmd_chars':COMMAND_CHARS,
          'escape':METACHAR_ESC,
          'cmd_start':START_OF_CMD,
          'commands':T_COMMANDS,
          'icomment':COMMENT},
    # VERBATIMINES MODOS SYNTAKSE
    'V': {'metach':METACH['verb'],
          'cmd_chars':COMMAND_CHARS,
          'cmd_start':START_OF_CMD,
          'commands':{}},
    # INLINE COMMENTARU SYNTAKSE
    # end_w--reiskia: pasibaik 
    # ir surink trailing whitespace
    'C': {'metach':{'\n':'end_w'},
          'commands':{}}}


# Negriezti switchai: ju gyvavimo sritis
# yra esama aplinka
SWITCH={'\\it','\\tt','\\em'}


# PAGRINDINIAI KOMANDU TIPAI 
#     * iverb -- inline verbatimas (skirtukai--bet kokie nonalpha symboliai)
#     * nocomment -- komandos kuriu argumentuose % nereiskia komentaro pradzios
#     * package -- \usepackage
#     * env -- enviromentu tagai \begin \end
#     * switch -- jungiklis
#     * math -- matematines komandos
#     * covered -- komandos kuriu argumentai apgaubia komanda is abieju pusiu

# GREITESNIAM TIPO SUZINOJIMUI
# R_TYPE={'iverb':['\\verb'],
#        'nocomment':['\\index',],
#        'package':['\\usepackage'],
#        'syntax':['\\newcommand','\\def']
#        'env':['\\begin','\\end'],
#        'switch':['\\it','\\bf','\\em'],    # switchai neturi nei vieno argumento
#        'math':['\\frac','\\sin','\\leq']
#        'msymbol':['\\alpha','\\beta'],
#        'tsymbol':['\textmu','\textbackslash']}

##### R_TYPE APVERTIMAS #####
# kad galetume gauti komandos tipa
# GRAZINAMAS: TYPE
# TYPE={}
# LIST=[]
# for i in R_TYPE.keys():
#     LIST.append([i,R_TYPE[i]])
# for i,j in LIST:
#     for k in j: TYPE[k]=i 
# del LIST
# del R_TYPE
##############################

### Papildom COMMANDS is R_TYPE #####
# for i in R_TYPE['switch']:
#     COMMANDS[i]=None
######################################
    


# KADA MESTI PARSE ERRORA
BAISUS_PAKETAI={'fancyvrb','listings'}
BAISIOS_KOMANDOS={'\\DefineShortVerb',     #\DefineShortVerb{ \|} -> |%labas%|
                  '\\UndefineShortVerb',
                  '\\newif',
                  '\\includecomment',
                  '\\excludecomment',
                  '\\specialcomment'}
