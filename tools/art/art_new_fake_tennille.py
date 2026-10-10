"""fake_tennille：独立角色注册，人体关节与绘制工具共用。"""
import sys
sys.dont_write_bytecode = True
from art_later_people import register, PEOPLE
NEW = register('fake_tennille',{'idle':2,'walk':4,'talk':2,'hurt':1,'down':1,'portrait':2,'grab':1,'reveal':1,'portrait_reveal':1})
ONESHOT = {'hurt','down','slash','attack','grab','reveal','punch','shock','beg','hide','angry'}
STATIC_STATES = {'true_form'}
CHAR_INFO = {'fake_tennille': dict(zh=PEOPLE['fake_tennille'][0],en='fake_tennille',cat='人物',typ='人物')}
