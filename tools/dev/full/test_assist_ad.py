"""验证战败菜单「放水再来」的激励广告门（engine/fight.js）。

用 ?autotest=1 从标题直接进第2章「力量」这一战（和 dev_fight.py 同一个 G.DEV 入口），
把 G.combat.CFG.assistAfter 调成 1，再用假的 G.ads 覆盖广告接口；战斗中用 c.fail()
主动判负，然后只读 G.dbg.snapshot() / G.ui.menu 判断菜单文案和放水结果。

覆盖：
- 广告可用 + 看完整：菜单显示「看广告·放水再来」，放水并重开战斗；
- 广告可用 + 玩家关闭：不放水，提示后回到同一张菜单；
- 广告可用 + 技术失败：免费放水，并提示；
- supported 为 false / G.ads 不存在 / supported 抛异常：保持「放水再来」且免费。

用法：python -B tools\\dev\\full\\test_assist_ad.py
"""
from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path

sys.dont_write_bytecode = True
GAME = Path(__file__).resolve().parents[3]
OUT = GAME / "tools" / "_playtest" / "assist_ad"
ENTRY, CHAPTER, FIGHT = "ch2Strength", 2, "b04_strength"
AD_LABEL, FREE_LABEL = "看广告·放水再来", "放水再来"

SETUP_JS = """(mode) => {
  G.combat.CFG.assistAfter = 1;
  window.__notices = [];
  window.__watchScenes = [];
  window.__supportedCalls = 0;
  const orig = G.ui.notice.bind(G.ui);
  G.ui.notice = (o) => { window.__notices.push((o && (o.text || o.title)) || ''); return orig(o); };
  const rewarded = { success: true, reason: 'rewarded', technical: false };
  const closed = { success: false, reason: 'closed', technical: false };
  const technical = { success: false, reason: 'failed', technical: true };
  if (mode === 'missing') {
    try { delete window.G.ads; } catch (e) { window.G.ads = undefined; }
    window.G.ads = undefined;
  } else if (mode === 'unsupported') {
    G.ads = {
      supported: async () => { window.__supportedCalls++; return false; },
      watch: async (scene) => { window.__watchScenes.push(scene); return rewarded; },
    };
  } else if (mode === 'supported_throws') {
    G.ads = {
      supported: async () => { window.__supportedCalls++; throw new Error('sdk broken'); },
      watch: async (scene) => { window.__watchScenes.push(scene); return rewarded; },
    };
  } else {
    const r = mode === 'success' ? rewarded : mode === 'closed' ? closed : technical;
    G.ads = {
      supported: async () => { window.__supportedCalls++; return true; },
      watch: async (scene) => { window.__watchScenes.push(scene); return r; },
    };
  }
}"""


def expect(ok, msg):
    if not ok:
        raise AssertionError(msg)


def boot_and_lose(page, mode):
    page.goto(GAME.joinpath("index.html").as_uri() + "?autotest=1", wait_until="load")
    page.wait_for_function("e => G.booted && G.ui.menu && G.DEV && G.DEV[e]", arg=ENTRY, timeout=30000)
    page.evaluate(SETUP_JS, mode)
    page.evaluate("([i, e]) => { G.CHAPTERS[i].run = G.DEV[e]; }", [CHAPTER, ENTRY])
    choose(page, "选择章节")
    choose(page, "第2章")
    page.wait_for_function(
        "id => { const s = G.dbg.snapshot(); return s.fightId === id && s.combat; }",
        arg=FIGHT, timeout=30000)
    page.wait_for_timeout(200)
    # 直接判负比等敌人打死玩家快得多；失败结算和菜单仍然走 fight.js 的正式路径。
    page.evaluate("() => { const f = G.world.fight; if (f && typeof f.fail === 'function') f.fail(); }")
    page.wait_for_function(
        "() => (G.ui.menu && (G.ui.menu.options || []).some(x => String(x).includes('再来一次')))",
        timeout=15000)
    return page.evaluate("() => G.ui.menu.options.map(String)")


def choose(page, label):
    page.wait_for_function(
        "l => !!(G.ui.menu && (G.ui.menu.options || []).some(x => String(x).includes(l)))",
        arg=label, timeout=15000)
    # 菜单有 0.08 s 的弹出保护，先停一下再读高亮和按键，避免按在打开前。
    page.wait_for_timeout(180)
    opts = page.evaluate("() => G.ui.menu.options.map(String)")
    n = next(i for i, s in enumerate(opts) if label in s)
    cur = page.evaluate("() => G.ui.menu ? (G.ui.menu.idx || 0) : 0")
    key = "ArrowDown" if n >= cur else "ArrowUp"
    for _ in range(abs(n - cur)):
        page.keyboard.press(key)
        page.wait_for_timeout(60)
    page.wait_for_timeout(150)
    page.keyboard.press("Enter")
    page.wait_for_timeout(200)


def wait_assist(page):
    page.wait_for_function(
        "() => { const s = G.dbg.snapshot(); return !!s.assist && s.assistLevel >= 1 && !!s.combat; }",
        timeout=15000)


def snap(page):
    return page.evaluate("() => G.dbg.snapshot()")


def load(page, key):
    # 用 ?? 而不是 ||：计数器为 0 时 || 会把它当成缺省值换成 []，导致 == 0 的断言永远不成立
    return page.evaluate("k => window[k] ?? []", key)


def scenario(browser, name, mode):
    errors, page = [], None
    try:
        page = browser.new_page(viewport={"width": 1280, "height": 720}, device_scale_factor=1)
        page.on("pageerror", lambda e: errors.append({"kind": "pageerror", "text": str(e)}))
        page.on("console", lambda m: errors.append({"kind": "console_" + m.type, "text": m.text})
                if m.type == "error" else None)
        items = boot_and_lose(page, mode)
        if mode in ("success", "closed", "technical"):
            expect(len(items) == 3 and items[-1] == AD_LABEL,
                   f"广告可用时第三项应为「{AD_LABEL}」，实际 {items}")
            expect(FREE_LABEL not in items, f"广告可用时不应再出现免费项「{FREE_LABEL}」，实际 {items}")
        else:
            expect(len(items) == 3 and items[-1] == FREE_LABEL,
                   f"无广告 / 不支持时第三项应保持「{FREE_LABEL}」，实际 {items}")
            expect(AD_LABEL not in items, f"无广告 / 不支持时不应出现广告项「{AD_LABEL}」，实际 {items}")

        choose(page, AD_LABEL if mode in ("success", "closed", "technical") else FREE_LABEL)

        if mode == "success":
            wait_assist(page)
            s = snap(page)
            expect(s.get("assist") is True and s.get("assistLevel") == 1, f"看完广告后应放水一次：{s.get('assist')}/{s.get('assistLevel')}")
            expect(s.get("fightId") == FIGHT and s.get("combat") is True, "看完广告后应回到同一场战斗重试")
            expect(load(page, "__watchScenes") == ["assist"], f"watch 场景名应为 assist：{load(page, '__watchScenes')}")
            expect(load(page, "__supportedCalls") == 1, "supported 只应在开菜单前调用一次")
        elif mode == "closed":
            page.wait_for_function(
                "() => (window.__notices || []).some(t => String(t).includes('广告没有看完，没有放水'))",
                timeout=10000)
            page.wait_for_function(
                "() => !!(G.ui.menu && (G.ui.menu.options || []).some(x => String(x).includes('看广告·放水再来')))",
                timeout=15000)
            s = snap(page)
            expect(not s.get("assist") and s.get("assistLevel") == 0, f"关闭广告不应放水：{s.get('assist')}/{s.get('assistLevel')}")
            expect(load(page, "__watchScenes") == ["assist"], f"watch 场景名应为 assist：{load(page, '__watchScenes')}")
            expect(load(page, "__supportedCalls") == 1, "supported 只应在开菜单前调用一次")
            # 回到菜单后再选「再来一次」，确认没有把玩家困在广告版菜单里。
            choose(page, "再来一次")
            page.wait_for_function("() => { const s = G.dbg.snapshot(); return s.fightId === 'b04_strength' && s.combat; }", timeout=15000)
            s = snap(page)
            expect(not s.get("assist") and s.get("assistLevel") == 0, "重新选「再来一次」不应带放水")
        elif mode == "technical":
            page.wait_for_function(
                "() => (window.__notices || []).some(t => String(t).includes('广告暂时无法播放，本次免费放水'))",
                timeout=10000)
            wait_assist(page)
            s = snap(page)
            expect(s.get("assist") is True and s.get("assistLevel") == 1, f"技术失败应免费放水：{s.get('assist')}/{s.get('assistLevel')}")
            expect(s.get("fightId") == FIGHT and s.get("combat") is True, "技术失败免费放水后应重试同一场战斗")
            expect(load(page, "__watchScenes") == ["assist"], f"watch 场景名应为 assist：{load(page, '__watchScenes')}")
        else:
            wait_assist(page)
            s = snap(page)
            expect(s.get("assist") is True and s.get("assistLevel") == 1, f"无广告时应免费放水：{s.get('assist')}/{s.get('assistLevel')}")
            expect(s.get("fightId") == FIGHT and s.get("combat") is True, "免费放水后应重试同一场战斗")
            expect(load(page, "__watchScenes") == [], f"无广告时不应调用 watch：{load(page, '__watchScenes')}")
            if mode == "unsupported":
                expect(load(page, "__supportedCalls") == 1, "supported 为 false 时也应只询问一次")
            elif mode == "supported_throws":
                expect(load(page, "__supportedCalls") == 1, "supported 抛异常时也应只询问一次")
            else:
                expect(load(page, "__supportedCalls") == 0, "G.ads 不存在时不应调用 supported")
        if errors:
            raise AssertionError(f"页面报错：{errors}")
        return {"ok": True, "items": items}
    except Exception as e:
        return {"ok": False, "error": str(e), "traceback": traceback.format_exc(),
                "items": locals().get("items"), "page_errors": errors}
    finally:
        if page:
            page.close()


def main():
    from playwright.sync_api import sync_playwright
    OUT.mkdir(parents=True, exist_ok=True)
    modes = [
        ("success", "success"),
        ("closed", "closed"),
        ("technical", "technical"),
        ("unsupported", "unsupported"),
        ("missing", "missing"),
        ("supported_throws", "supported_throws"),
    ]
    results = {}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required"])
        try:
            for name, mode in modes:
                print(f"[assist-ad] {name} ...", flush=True)
                results[name] = scenario(browser, name, mode)
                print(json.dumps(results[name], ensure_ascii=False), flush=True)
        finally:
            browser.close()
    report = {"ok": all(r.get("ok") for r in results.values()), "results": results}
    (OUT / "result.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": report["ok"], "out": str(OUT)}, ensure_ascii=False))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
