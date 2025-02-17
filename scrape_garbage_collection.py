import requests
import datetime
import json
import uuid

def get_waste_schedule():
    base_url = "https://bip.jaktorow.pl/odpady-komunalne/getterminy/"
    start_date = datetime.date.today().replace(month=1, day=1).isoformat()
    end_date = datetime.date.today().replace(month=12, day=31).isoformat()
    
    payload = {
        "spot": 13,
        "fraction": 0, # get all fractions
        "property_type": 0,
        "start": f"{start_date}T00:00:00+01:00",
        "end": f"{end_date}T23:59:59+01:00",
    }
    
    response = requests.post(base_url, data=payload)
    response.raise_for_status()
    return response.json()

FRACTION_EMOJIS = {
    1: "\U0001F5D1\U0001F9F9 Zmieszane",      # 🗑🧹
    2: "\U0001F5D1\U0001F5FF Szkło",          # 🗑🗿
    3: "\U0001F5D1\U0001F4DA Papier",         # 🗑📚
    4: "\U0001F5D1\U0001F6E2 Plastik",        # 🗑🛢
    5: "\U0001F5D1\U0001F331 Bio",            # 🗑🌱
    6: "\U0001F6CB\U0000FE0F Gabaryty",       # 🗑🛋️
    7: "\U0001F6CB\U0001F6DE Gabaryty",       # 🗑🛞
}

def convert_to_ics(waste_data):
    ics_content = "BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//WasteSchedule//EN\r\n"
    for entry in waste_data:
        title = FRACTION_EMOJIS.get(entry["fraction"], "Wywóz śmieci")
        event_date = entry["start"].replace("-", "")
        uid = str(uuid.uuid4())
        dtstamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%SZ")
        
        ics_content += f"BEGIN:VEVENT\r\nUID:{uid}\r\nDTSTAMP:{dtstamp}\r\nSUMMARY:{title}\r\nDTSTART;VALUE=DATE:{event_date}\r\nDTEND;VALUE=DATE:{event_date}\r\n"
        
        # Przypomnienia dla frakcji 1-5: dzień wcześniej o 17:00
        if entry["fraction"] in [1, 2, 3, 4, 5]:
            ics_content += f"BEGIN:VALARM\r\nACTION:DISPLAY\r\nTRIGGER:-P0DT7H0M0S\r\nDESCRIPTION:Przypomnienie o wywozie\r\nEND:VALARM\r\n"
        
        # Przypomnienia dla frakcji 6-7: 2 tygodnie wcześniej i dzień wcześniej o 17:00
        if entry["fraction"] in [6, 7]:
            ics_content += f"BEGIN:VALARM\r\nACTION:DISPLAY\r\nTRIGGER:-P13DT7H0M0S\r\nDESCRIPTION:Przypomnienie o wywozie\r\nEND:VALARM\r\n"
            ics_content += f"BEGIN:VALARM\r\nACTION:DISPLAY\r\nTRIGGER:-P0DT7H0M0S\r\nDESCRIPTION:Przypomnienie o wywozie\r\nEND:VALARM\r\n"
        
        ics_content += "END:VEVENT\r\n"
    ics_content += "END:VCALENDAR\r\n"
    return ics_content

if __name__ == "__main__":
    waste_data = get_waste_schedule()
    ics_data = convert_to_ics(waste_data)
    
    with open("waste_schedule.ics", "w", encoding="utf-8") as f:
        f.write(ics_data)
    
    print("Terminy wywozu śmieci zapisano w 'waste_schedule.ics'")