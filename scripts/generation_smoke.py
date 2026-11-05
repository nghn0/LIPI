"""Run real Param smoke cases; logs model output, never invents human ratings."""
import sys,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from backend.param import generate
cases=[
 ('G01','मुझे कल की meeting के लिए अपने project की report तैयार करनी है।','polish','formal'),
 ('G02','आप कैसे हैं? बहुत दिन बाद बात हुई।','polish','friendly'),
 ('G03','नमस्ते! मुझे कल की meeting के लिए अपने project की report तैयार करनी है.','translate','natural'),
 ('G04','राहुल सोमवार को सुबह 10:30 बजे आएगा।','translate','natural')]
rows=[]
for id,text,task,tone in cases:
 try:row={'id':id,'input':text,'task':task,'tone':tone,**generate(text,task,tone)}
 except Exception as exc:row={'id':id,'input':text,'task':task,'error':str(exc)}
 rows.append(row);print(id,row.get('output',row.get('error')),flush=True)
(ROOT/'data/generation_smoke.json').write_text(json.dumps({'created_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'note':'Real local generation smoke outputs. Successful inference is not a human quality rating. Review grammar and meaning.','results':rows},ensure_ascii=False,indent=2))
