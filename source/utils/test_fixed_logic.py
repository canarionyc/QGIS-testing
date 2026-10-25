import sys
sys.path.append(r"C:\Users\tglla\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins")

from PyQt5.QtCore import QCoreApplication
app = QCoreApplication.instance()
if not app:
    app = QCoreApplication(sys.argv)

from operator import itemgetter
from istacqgis.controllers.istacpy import istacpy

subjects = istacpy.get_subjects()
subject_items = subjects.get('items', [])
print(f"Total subjects: {len(subject_items)}")

pop_subj = next((s for s in subject_items if "Poblaci" in s.get('title', {}).get('es', '')), None)
if pop_subj:
    sid = pop_subj['id']
    stitle = pop_subj['title']['es']
    print(f"\nFound Population subject: id='{sid}', title='{stitle}'")
    
    query = f'subjectCode EQ "{sid}"'
    indicators = istacpy.get_indicators(q=query, limit=999)
    print("Indicators result type:", type(indicators))
    items = indicators.get('items', [])
    print(f"Total indicators found: {len(items)}")
    
    indicators_title_es = {}
    for indicator in items:
        ind_id = indicator.get("id")
        title_dict = indicator.get("title", {})
        ind_title = title_dict.get("es") or title_dict.get("__default__") or ind_id
        indicators_title_es[ind_id] = ind_title
        
    sorted_inds = sorted(indicators_title_es.items(), key=itemgetter(1))
    print("\nSample indicators:")
    for k, v in sorted_inds[:8]:
        print(f"  [{k}] -> {v}")
