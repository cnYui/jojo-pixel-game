"""生成 JS 联系表、参考并排图与逐函数性能报告；不更改原工程。"""
from pathlib import Path
import json
import sys
from PIL import Image
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
OUT = HERE / '_out'


def main():
    OUT.mkdir(exist_ok=True)
    errors = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1450, 'height': 1900}, device_scale_factor=1)
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto((HERE / 'fx_sheet.html').as_uri(), wait_until='load')
        page.wait_for_function('() => P2_RESULT.ready', timeout=120000)
        result = page.evaluate('() => P2_RESULT')
        for sheet in page.locator('canvas[id^="sheet_"]').all():
            si = sheet.get_attribute('id').split('_')[1]
            dest = OUT / f'js_sheet_{si}.png'
            sheet.screenshot(path=str(dest))
            ref = Image.open(OUT / f'ref_sheet_{si}.png').convert('RGB')
            js = Image.open(dest).convert('RGB')
            comp = Image.new('RGB', (ref.width + js.width + 8, max(ref.height, js.height)), (24, 22, 32))
            comp.paste(ref, (0, 0))
            comp.paste(js, (ref.width + 8, 0))
            comp.save(OUT / f'compare_{si}.png')
        browser.close()
    result['pageerrors'] = errors
    result['overBudget'] = [r for r in result['timing'] if r['ms'] >= r['limit']]
    result['ok'] = not (result['errors'] or errors or result['events'] or result['missingImg'] or result['overBudget']) and result.get('instances', {}).get('ms', 999) < 4
    (OUT / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'ok': result['ok'], 'cases': len(result['timing']), 'errors': result['errors'], 'missingImg': result['missingImg'], 'overBudget': result['overBudget'], 'instances': result.get('instances'), 'out': str(OUT)}, ensure_ascii=False))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
