"""233 专属副本补丁：apply 游戏副本目录；sdk 输入.zip 输出.zip。"""
import argparse
from pathlib import Path
import re
import zipfile

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[1] / '游戏'
SDK_TAG = '<script async src="https://cdn.233xyx.com/h5ad/metah5ad_v1.min.js"></script>'
OLD_FAILED = """      const opts=['再来一次','回到标题'];if(attempt+1>=G.combat.CFG.assistAfter)opts.push('放水再来');let choice=1;try{choice=await Promise.race([G.ui.openMenu(null,opts),G.until(()=>!active()).then(()=>1)]);}catch(e){if(!G.cancelled(e))throw e;}
      if(!active()||choice===1)return false;if(choice===2)assist=true;attempt++;G.post.filter('sepia',null);W.cine=null;return true;"""
NEW_FAILED = """      // 查询和播放都跟随战斗生命周期结束，避免回标题后遗留等待或奖励。
      const adGuard=async p=>{
        try{return await Promise.race([p,G.until(()=>!active()).then(()=>null)]);}
        finally{if(!active()&&G.ads&&G.ads.cancel)G.ads.cancel();}
      };
      let ad=false;
      if(attempt+1>=G.combat.CFG.assistAfter&&G.ads&&typeof G.ads.supported==='function'){
        try{ad=await adGuard(G.ads.supported());}catch(e){ad=false;}
        if(!active())return false;
      }
      for(;;){
        const opts=['再来一次','回到标题'];if(attempt+1>=G.combat.CFG.assistAfter)opts.push(ad?'看广告·放水再来':'放水再来');
        let choice=1;try{choice=await Promise.race([G.ui.openMenu(null,opts),G.until(()=>!active()).then(()=>1)]);}catch(e){if(!G.cancelled(e))throw e;}
        if(!active()||choice===1)return false;
        if(choice===2){
          if(ad){
            let r;try{r=await adGuard(G.ads.watch('assist'));}catch(e){r={success:false,reason:'exception',technical:true};}
            if(!active())return false;
            if(r&&r.success)assist=true;
            else if(r&&r.technical){
              assist=true;
              if(G.ui.notice)await guard(G.ui.notice({text:'广告暂时无法播放，本次免费放水',minT:1.2,auto:true}));
              if(!active())return false;
            }else{
              if(G.ui.notice)await guard(G.ui.notice({text:'广告没有看完，没有放水',minT:1.2,auto:true}));
              if(!active())return false;
              continue;
            }
          }else assist=true;
        }
        attempt++;G.post.filter('sepia',null);W.cine=null;return true;
      }"""
PATCHES = {
    'index.html': [('<script src="engine/core.js"></script>',
                    '<script src="engine/core.js"></script>\n<script src="engine/ads.js"></script>')],
    'engine/fight.js': [(OLD_FAILED, NEW_FAILED)],
}


def apply(game_dir):
    """先验证所有锚点，再写入副本，防止文本漂移造成半份补丁。"""
    game = Path(game_dir).resolve()
    if game == SOURCE.resolve():
        raise ValueError('禁止修改第四部游戏源码，请传入游戏副本目录')
    ads = game / 'engine/ads.js'
    if ads.exists():
        raise ValueError('已经存在 engine/ads.js，禁止重复应用')
    changes = []
    for rel, pairs in PATCHES.items():
        path = game / rel
        raw = path.read_bytes()
        text = raw.decode('utf-8')
        nl = '\r\n' if '\r\n' in text else '\n'
        for old, new in pairs:
            old, new = old.replace('\n', nl), new.replace('\n', nl)
            count = text.count(old)
            if count != 1:
                raise ValueError('%s 补丁命中 %d 次，必须恰好一次' % (rel, count))
            text = text.replace(old, new)
        changes.append((path, text.encode('utf-8')))
    for path, data in changes:
        path.write_bytes(data)
    ads.write_bytes((HERE / 'ads.js').read_bytes())


def inject_sdk(src, dst):
    """只改根 index.html 的 head；其他条目保留内容、顺序和 ZipInfo 元数据。"""
    if Path(src).resolve() == Path(dst).resolve():
        raise ValueError('输入输出 zip 必须不同')
    with zipfile.ZipFile(src) as zin:
        entries = zin.infolist()
        if sum(i.filename == 'index.html' for i in entries) != 1:
            raise ValueError('zip 必须恰好有一个根 index.html')
        html = zin.read('index.html').decode('utf-8')
        if re.search(r'<script\b[^>]*metah5ad', html, re.I):
            raise ValueError('已经有 233 SDK，禁止重复注入')
        heads = list(re.finditer(r'<head\b[^>]*>(.*?)</head\s*>', html, re.I | re.S))
        if len(heads) != 1:
            raise ValueError('必须恰好有一个 head')
        head = heads[0]
        metas = list(re.finditer(r'<meta\s+charset\b[^>]*>', head.group(1), re.I))
        if len(metas) != 1:
            raise ValueError('head 内必须恰好有一个 meta charset')
        pos = head.start(1) + metas[0].end()
        nl = '\r\n' if '\r\n' in html else '\n'
        html = html[:pos] + nl + SDK_TAG + html[pos:]
        order = [i for i in entries if i.filename == 'index.html'] + [i for i in entries if i.filename != 'index.html']
        with zipfile.ZipFile(dst, 'w') as zout:
            zout.comment = zin.comment
            for info in order:
                zout.writestr(info, html.encode('utf-8') if info.filename == 'index.html' else zin.read(info))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('apply').add_argument('game_dir')
    sdk = sub.add_parser('sdk')
    sdk.add_argument('src')
    sdk.add_argument('dst')
    args = parser.parse_args()
    try:
        if args.command == 'apply':
            apply(args.game_dir)
        else:
            inject_sdk(args.src, args.dst)
    except (ValueError, OSError, zipfile.BadZipFile) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
