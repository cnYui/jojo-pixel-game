"""SPW工作人员：宽檐帽、眼镜、证件和旅行服用于辨认救援身份。"""
import sys
sys.dont_write_bytecode=True
from art_later_people import register, PEOPLE
NEW=register('npc_spw')
ONESHOT={'hurt','down'}
STATIC_STATES=set()
CHAR_INFO={'npc_spw':dict(zh=PEOPLE['npc_spw'][0],en='SPW staff',cat='人物',typ='人物')}
