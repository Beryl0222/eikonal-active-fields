"""读取并核对本地合成资料，不计算产品结果。"""
from pathlib import Path
import hashlib,json,math
import numpy as np

BASE=Path(__file__).resolve().parent

def _finite(value):
    if isinstance(value,dict):
        for v in value.values():_finite(v)
    elif isinstance(value,list):
        for v in value:_finite(v)
    elif isinstance(value,float):
        if not math.isfinite(value):raise ValueError('资料含非有限数值')

def validate():
    d=json.loads((BASE/'data/materials.json').read_text(encoding='utf-8'))
    events=json.loads((BASE/'data/events.json').read_text(encoding='utf-8'))
    _finite(d)
    assert d['metadata']['format_version']==1
    assert isinstance(events,list) and len(events)>5
    assert all(isinstance(e.get('op'),str) for e in events)
    a=np.asarray(d['speed']);assert a.shape==np.asarray(d['kind']).shape
    assert np.all(a>0) and set(x for row in d['kind'] for x in row)=={'free','missing','obstacle'}
    for s in d['sources']:
        r,c=s['position'];assert d['kind'][r][c]=='free' and s['t0']>=0
    assert len({s['id'] for s in d['sources']})==len(d['sources'])
    assert all(e['op']!='edit' or e['edit'] in {x['id'] for x in d['edits']} for e in events)
    sample=d['sampling']
    block_ids={b['block_id'] for b in sample['blocks']}
    assert len(block_ids)==len(sample['blocks'])
    for arrival in sample['arrivals']:
        assert arrival['block_id'] in block_ids
        for v in arrival['values']:
            r,c=v['position'];assert d['kind'][r][c]=='missing' and v['speed']>0
    assert sample['budget']<sum(b['cost'] for b in sample['blocks'])
    return d,events

if __name__=='__main__':
    d,events=validate()
    raw=(BASE/'data/materials.json').read_bytes()+(BASE/'data/events.json').read_bytes()
    print(json.dumps({'产品':d['metadata']['product'],'资料核对':'通过','操作输入数':len(events),'资料SHA256':hashlib.sha256(raw).hexdigest()},ensure_ascii=False))
