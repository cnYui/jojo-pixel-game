"""埃及水果商人：包头巾、胡须和长袍区别于通用小镇居民。"""
import sys
sys.dont_write_bytecode=True
from art_later_people import register, PEOPLE
NEW=register('npc_merchant')
ONESHOT={'hurt','down'}
STATIC_STATES=set()
CHAR_INFO={'npc_merchant':dict(zh=PEOPLE['npc_merchant'][0],en='Fruit merchant',cat='人物',typ='人物')}
