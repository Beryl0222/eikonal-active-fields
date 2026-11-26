"""按固定种子生成容量输入，不计算算子输出。"""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
BASE=Path(__file__).resolve().parent

def generate(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    rng=np.random.default_rng(261126)
    arrays={};meta={'format_version':1,'source':'本地合成容量输入','seed':261126}
    H=W=256;tile=32
    speed=rng.uniform(.8,1.2,(H,W));kind=np.zeros((H,W),dtype='int8')
    kind[40:210,128]=1;kind[120:132,128]=0;kind[150:158,180:188]=2
    sources=[dict(id='s'+str(i),position=[16+24*i,16+21*i],t0=.1*i,trainable=True) for i in range(8)]
    meta.update(H=H,W=W,tile=tile,spacing=[1.,.8],kind_codes={'free':0,'obstacle':1,'missing':2},sources=sources,speed_bounds=[.6,2.],block_reads=5000,edits=[dict(op='withdraw_source',source='s0'),dict(op='change_type',position=[125,128],new_type='obstacle')])
    for row in range(0,H,tile):
        for col in range(0,W,tile):
            arrays['speed_'+str(row)+'_'+str(col)]=speed[row:row+tile,col:col+tile]
            arrays['kind_'+str(row)+'_'+str(col)]=kind[row:row+tile,col:col+tile]
    np.savez(output/'arrays.npz',**arrays)
    meta['arrays']={k:{'shape':list(v.shape),'dtype':str(v.dtype)} for k,v in arrays.items()}
    (output/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return meta

if __name__=='__main__':
    parser=argparse.ArgumentParser(description='生成可复现的合成容量输入')
    parser.add_argument('--output',required=True)
    args=parser.parse_args();meta=generate(args.output)
    print(json.dumps({'数组数':len(meta['arrays']),'资料SHA256':hashlib.sha256((Path(args.output)/'arrays.npz').read_bytes()).hexdigest()},ensure_ascii=False))
