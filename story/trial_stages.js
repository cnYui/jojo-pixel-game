// 星尘试炼：第一期 18 关的顺序与名牌文字（玩法脚本 §四、关卡表 §2.1）。
//   这里只放“关卡表”，每一关的布景 / 战斗配置在各章文件末尾登记的 G.TRIAL_SRC[id] 里，
//   流程按 id 去取，所以调整顺序 / 加第二期关卡只改这张表。
'use strict';
(function () {
  const G = window.G;
  const T = G.TRIAL = G.TRIAL || {};

  // 字段：id（G.TRIAL_SRC 的键）、title（名牌大字）、sub（地点 · 章）、chapter（G.CHAPTERS 的 key）、
  //   solo（只有最终关 DIO 为 true：其他人不上场）、noStop（这一关的 U 换回欧拉欧拉）、tune（Boss 伤害倍率）、
  //   par（评价的参考用时，取关卡表 §2.1；第 7 关按 §2.2 只打 J·凯尔，取 70）
  T.stages = [
    { id: 'b01_kakyoin', title: 'VS 花京院典明 · 绿色法皇', sub: '学校 · 序章', chapter: 'prologue', tune: 1, par: 90 },
    { id: 'b02_chariot', title: 'VS 波鲁纳雷夫 · 银色战车', sub: '香港 · 第1章', chapter: 'ch1', tune: 1, par: 100 },
    { id: 'b03_darkbluemoon', title: 'VS 暗蓝之月', sub: '南海 · 第2章', chapter: 'ch2', tune: 1, par: 110 },
    { id: 'b04_strength', title: 'VS 力量', sub: '南海 · 第2章', chapter: 'ch2', tune: 1, par: 100 },
    { id: 'b05_devo', title: 'VS 迪波 · 黑檀木恶魔', sub: '新加坡 · 第3章', chapter: 'ch3', tune: 1, par: 90 },
    { id: 'b06_yellowtemperance', title: 'VS 黄色节制', sub: '新加坡 · 第3章', chapter: 'ch3', tune: 1, par: 100 },
    { id: 'b07_hangedman', title: 'VS J·凯尔 · 倒吊人', sub: '印度 · 第4章', chapter: 'ch4', tune: 1, par: 70 },
    { id: 'b09b_wheeloffortune', title: 'VS 命运之轮', sub: '巴基斯坦 · 第5章', chapter: 'ch5', tune: 1, par: 75 },
    { id: 'b10_justice', title: 'VS 恩雅 · 正义', sub: '巴基斯坦 · 第5章', chapter: 'ch5', tune: 1, par: 110 },
    { id: 'b13b_death13', title: 'VS 死神 13', sub: '阿拉伯 · 第6章', chapter: 'ch6', tune: 1, par: 90 },
    { id: 'b14b_judgement', title: 'VS 审判', sub: '红海 · 第7章', chapter: 'ch7', tune: 1, par: 70 },
    // 时停和氧气倒计时的关系还没试打（关卡表 §2.2 第 12 关）：先不做限制，待试打确认后再改 true。
    { id: 'b15b_highpriestess', title: 'VS 女教皇', sub: '红海 · 第7章', chapter: 'ch7', noStop: false, tune: 1, par: 90 },
    { id: 'b18a_anubis', title: 'VS 阿努比斯神', sub: '尼罗河 · 第9章', chapter: 'ch9', tune: 1, par: 90 },
    { id: 'b19_bast', title: 'VS 巴斯特女神', sub: '尼罗河 · 第9章', chapter: 'ch9', tune: 1, par: 120 },
    { id: 'b23a_petshop', title: 'VS 荷鲁斯神', sub: '开罗 · 第10章', chapter: 'ch10', tune: 1, par: 90 },
    { id: 'b26b_cream', title: 'VS 瓦尼拉·艾斯', sub: 'DIO的馆 · 第11章', chapter: 'ch11', tune: 1, par: 180 },
    { id: 'b27_nukesaku', title: 'VS 努凯萨克', sub: 'DIO的馆 · 第11章', chapter: 'ch11', tune: 1, par: 40 },
    // 最终关三段一体：其他人站在场外，段 1 / 2 的 U 由这一战自己的 kitOverride 换回欧拉欧拉，段 3 才是白金之星·世界。
    { id: 'b28d_all', title: 'VS DIO', sub: '开罗 · 终章', chapter: 'final', solo: true, tune: 1, par: 420 },
  ];
})();
