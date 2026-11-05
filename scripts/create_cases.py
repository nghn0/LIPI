"""Author task-specific gold cases before inspecting predictions."""

import json
from pathlib import Path

rows = [
    ("everyday", "namaste", "नमस्ते"),
    ("everyday", "aap kaise hain?", "आप कैसे हैं?"),
    ("everyday", "mujhe paani chahiye.", "मुझे पानी चाहिए."),
    ("everyday", "mera naam rahul hai.", "मेरा नाम राहुल है."),
    ("everyday", "hum ghar ja rahe hain.", "हम घर जा रहे हैं."),
    ("everyday", "kal subah milte hain.", "कल सुबह मिलते हैं."),
    ("everyday", "aaj mausam achha hai.", "आज मौसम अच्छा है."),
    ("everyday", "bahut dhanyavaad!", "बहुत धन्यवाद!"),
    ("everyday", "aap kahan rehte hain?", "आप कहाँ रहते हैं?"),
    ("everyday", "mujhe hindi pasand hai.", "मुझे hindi पसंद है."),
    ("campus", "mujhe padhai karni hai.", "मुझे पढ़ाई करनी है."),
    ("campus", "kal exam hai.", "कल exam है."),
    ("campus", "apna assignment submit karo.", "अपना assignment submit करो."),
    ("campus", "project ki deadline somvaar hai.", "project की deadline सोमवार है."),
    ("campus", "kripya notes bhej dijiye.", "कृपया notes भेज दीजिए."),
    ("campus", "hamari class subah hai.", "हमारी class सुबह है."),
    ("campus", "mujhe chhutti chahiye.", "मुझे छुट्टी चाहिए."),
    ("campus", "aap ka feedback chahiye.", "आप का feedback चाहिए."),
    ("spelling variants", "mai ghar par hu.", "मैं घर पर हूँ."),
    ("spelling variants", "main ghar par hoon.", "मैं घर पर हूँ."),
    ("spelling variants", "mujhe nahi pata.", "मुझे नहीं पता."),
    ("spelling variants", "mujhe nahin pata.", "मुझे नहीं पता."),
    ("spelling variants", "yeh meri kitaab hai.", "यह मेरी किताब है."),
    ("spelling variants", "woh mera dost hai.", "वह मेरा दोस्त है."),
    ("code switching", "meeting ke liye taiyaar ho?", "meeting के लिए तैयार हो?"),
    ("code switching", "apna email check karo.", "अपना email चेक करो."),
    ("code switching", "python mein code likho.", "python में code लिखो."),
    ("code switching", "online class kab hai?", "online class कब है?"),
    ("code switching", "report upload kar do.", "report upload कर दो."),
    ("code switching", "laptop ki battery khatam hai.", "laptop की बैटरी खत्म है."),
    ("named entities", "rahul aur priya", "राहुल और प्रिया"),
    ("named entities", "bharat hamara desh hai.", "भारत हमारा देश है."),
    ("named entities", "dilli se mumbai", "दिल्ली से मुंबई"),
    ("named entities", "bengaluru mein rehta hoon.", "बेंगलुरु में रहता हूँ."),
    ("protected content", "kal 10:30 baje milte hain.", "कल 10:30 बजे मिलते हैं."),
    ("protected content", "email: student@example.com", "email: student@example.com"),
    (
        "protected content",
        "https://example.com/forms?year=2026",
        "https://example.com/forms?year=2026",
    ),
    ("protected content", "@rahul #campus2026", "@rahul #campus2026"),
    ("protected content", "नमस्ते! aap kaise hain?", "नमस्ते! आप कैसे हैं?"),
    ("protected content", "namaste!\nphir milenge.", "नमस्ते!\nफिर मिलेंगे."),
]
assert len(rows) == 40
cases = [
    {
        "id": f"T{i:02}",
        "category": category,
        "input": text,
        "expected": expected,
        "preserve_english": True,
    }
    for i, (category, text, expected) in enumerate(rows, 1)
]
Path("data/test_cases.json").write_text(json.dumps(cases, ensure_ascii=False, indent=2))
