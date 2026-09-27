# usage: python3 render.py <saved download json path> <expected file id> [outdir]
# Refuses to render if the saved download is for a different file (guards against temp-file collisions).
import sys,json,base64,pymupdf,os
src,fid=sys.argv[1],sys.argv[2]
out=sys.argv[3] if len(sys.argv)>3 else os.path.join(os.path.dirname(os.path.abspath(__file__)),'img')
os.makedirs(out,exist_ok=True)
d=json.load(open(src))
if d.get('id') and d['id']!=fid:
    print(f"MISMATCH: this download is file {d['id']} ({d.get('title')}), not {fid}. Download again ONE at a time."); sys.exit(2)
print('title:',d.get('title'))
b=base64.b64decode(d['content'])
doc=pymupdf.open(stream=b,filetype='pdf')
for i in range(min(doc.page_count,3)):
    p=os.path.join(out,f'{fid}_p{i+1}.png'); doc[i].get_pixmap(dpi=60).save(p); print(p)
print('pages_total',doc.page_count)
