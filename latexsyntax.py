'''Modulis kuriame aprasyta iprasta latexo syntakse'''
import string, os, sys

################################################## 
########## LaTeX'o IPRASTA SYNTAKSE ############## 


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
                # algoritmas parasytas taip, kad parsinant
                # neimanoma sutikti uzdaranciu reiskiniu
                # kiekvienas atidarantis reiskinys
                # inicijuoja nauja parsinimo procesa
                '}':'error',
                # aktyvus symboliai, kuriu negalima sutikti
                # tekstineje busenoje
                '#':'error',
                '^':'error',
                '_':'error',
                '&':'error'},
         'math':{
                '%':'icomment',
                '{':'mbraces',
                '~':'space',
                '\\':'mcommand',
                '^':'superscript',
                '_':'subscript',
                '$':'error',
                '}':'error',         
                '#':'error',
                '&':'error'},
         # kol kas verb vadinsime visas aplinkas,
         # kuriose nereikia gaudyti 
         # -inline komentaru
         # -matematikos 
         # -metaskliaustu  ir t.t. 
         'verb':{'\\':'vcommand'},
         # ineksuose syntakse visai sudirbta 
         'index':{'{':'mbraces',
                  '}':'error'},
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
# PVZ: * labas \index{aaa\} vakras
#        puikiai kompiliuojasi ir } nera eskapintas
#      * \begin{verbatim} aaaaa \\end{verbatim} irgi puikiai kompiliuojasi
#      * taciau \iffalse aaa \\fi --ne
# 
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
T_COMMANDS={
          '\\usepackage':{
              'pattern':(0,1),
              'type':'syntax'
              },
          '\\rule':{
              'pattern':(0,1,1),
              'type':'maketas'
              },
          '\\footnote':{
              'pattern':(0,'T'),
              'type':'footnote'
              },
          '\\newcommand':{
              'pattern':(1,0,0,1),
              'type':'syntax'
              },
          '\\renewcommand':{
              'pattern':(1,0,0,1),
              'type':'syntax'
              },
          '\\def':{
              'pattern':(1,1),
              'type':'syntax'
              },
          '\\label':{
              'pattern':(1,),
              'type':'label'
              },
          '\\part':{
              'pattern':(0,'T'),
              'type':'section'
              },
          '\\chapter':{
              'pattern':(0,'T'),
              'type':'section'
              },
          '\\section':{
              'pattern':(0,'T'),
              'type':'section'
              },                  
          '\\subsection':{
              'pattern':(0,'T'),
              'type':'section'
              },
          '\\subsubsection':{
              'pattern':(0,'T'),
              'type':'section'
              },
          '\\paragraph':{
              'pattern':(0,'T'),
              'type':'section'
              },
          '\\subparagraph':{
              'pattern':(0,'T'),
              'type':'section'
              },
          '\\subsubparagraph':{
              'pattern':(0,'T'),
              'type':'section'
              },
          '\\subsubsubparagraph':{
              'pattern':(0,'T'),
              'type':'section'
              },
          '\\mbox':{
              'pattern':('T',),
              'type':'text'
              },
          '\\index':{
              'pattern':('V',),
              'type':'index'
              },
          '\\textbackslash':{
              'pattern':None,
              'type':'tsymbol'}}

# MATEMATINES MODOS KOMANDOS 
M_COMMANDS={'\\frac':{
               'pattern':(1,1),
               'type':'fraction'
               },
            '\\alpha':{
                'pattern':None,
                'type':'msymbol'
                },
            '\\mathbf':{
                'pattern':('M',),
                'type':'mfont'}}

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
ENVIROMENTS={'equation':{
                 'pattern':(0,),
                 'content':'M'
                 },
             'pf':{
                 'pattern':(0,),
                 'syntax':'T'
                 },
             'pf*':{
                 'pattern':(1,),
                 'syntax':'T'
                 },
             'verbatim':{
                 'pattern':None,
                 'syntax':'V'
                 },
             'comment':{
                 'pattern':None,
                 'syntax':'V'
                 },
             'listing':{
                 'pattern':None,
                 'syntax':'V'}}

SWITCHES={'\\iffalse':{
               'closing':'\\fi',
               'content':'V',
               'type':'comment',
               'properties':[]
               },
          '\\comment':{
              'closing':'\\endcomment',
              'content':'V',
              'type':'comment',
              'properties':[]
              },
          '\\(':{
              'closing':'\\)',
              'content':'M',
              'type':'imath'
              },
          '\\[':{
              'closing':'\\]',
              'content':'M',
              'type':'dmath',
              'properties':[]
              }}
         

############### KOMENTARAI

# NUMATANT SINTAKSES KEITIMA
# METAJUNGIGLIS: (ISJUNGIKLIS, (SAVYBES,))
# w -- reiskia, kad po isjungimo bus suvalgomi whitespace
COMMENT={'%':('\n',('w',))}


############## SKIRTUKAI
######################################## 
# 'closing' -- uzdarantis reiskinys
# 'properties' -- savybes, kurias turi skirtukai:
#     * 'meta' -- symbolis turi buti neeskeipintas
#     * 'mch' -- symbolis gali tureti kita reiksme
#             jei paskui ji eis tam tikra kombinacija
#             butina tikrinti MULTICHAR_DELIMS ir perjungti 
#             i kita rezima
# 'content' -- kokios syntakses bus turinys gaubiamas siu 
#             skirtuku
#     * 'A' -- argumento atskirai apibrezta syntakse
#     * 'O' -- (OUTER) isorinio reiskinio syntakse
#     * 'M' -- matematine syntakse
#     * ... -- ir visos kitos apibreztos syntakse

DELIMS={'[':{
            'closing':'[',
            'properties':[],
            'content':'A'
            },
        '{':{
            'closing':'}',
            'properties':['meta'],
            'content':'O'
            },
        '$':{
            'closing':'$',
            'properties':['meta','mch'],
            'content':'M',
            'multichar':['$$']
            },
        '`':{
            'closing':"'",
            'properties':['mch'],
            'content':'O'}}

############## DAUGELIO SYMBOLIU SKIRTUKAI 
MULTICHAR_DELIMS={'$$':{
                       'closing':'$$',
                       'properties':['meta'],
                       'content':'M'
                       },
                  '``':{
                      'closing':"''",
                      'properties':[],
                      'content':'O'
                       }}

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
    # VERBATIMINES MODOS SYNTAKSE
    'V': {'metach':METACH['verb'],
          'cmd_chars':COMMAND_CHARS,
          'cmd_start':START_OF_CMD,
          'commands':{}},
    # INLINE COMMENTARU SYNTAKSE
    # end_w--reiskia: pasibaik 
    # ir surink trailing whitespace
    'C': {'metach':{'\n':'end_w'},
          'commands':{}},
    'I': {'metach':METACH['index'],
          'delims':
              {'{':DELIMS['{']}}
              }



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
