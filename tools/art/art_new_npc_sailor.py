"""npc_sailor：独立角色注册，人体关节与绘制工具共用。"""
import sys
sys.dont_write_bytecode = True
from art_later_people import register, PEOPLE
NEW = register('npc_sailor',{'idle':2,'walk':4,'talk':2,'hurt':1,'down':1,'portrait':2})
ONESHOT = {'hurt','down','slash','attack','grab','reveal','punch','shock','beg','hide','angry'}
STATIC_STATES = {'true_form'}
CHAR_INFO = {'npc_sailor': dict(zh=PEOPLE['npc_sailor'][0],en='npc_sailor',cat='人物',typ='人物')}
