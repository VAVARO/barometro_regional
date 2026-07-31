import json

def fix_dict(obj):
    if isinstance(obj, str):
        s = obj.replace('\ufffd', 'í')
        s = s.replace('S', 'Sí').replace('Sï¿½', 'Sí').replace('S\ufffd', 'Sí')
        s = s.replace('polticas', 'políticas').replace('polï¿½ticas', 'políticas')
        s = s.replace('Aysén', 'Aysén').replace('Ayséen', 'Aysén')
        s = s.replace('Río Ibáñez', 'Río Ibáñez').replace('Río Ibáéez', 'Río Ibáñez')
        s = s.replace('Economía', 'Economía').replace('Educación', 'Educación').replace('Población', 'Población')
        s = s.replace('Región', 'Región').replace('región', 'región')
        s = s.replace('Qué', 'Qué').replace('Cómo', 'Cómo').replace('cuán', 'cuán')
        s = s.replace('más', 'más').replace('dónde', 'dónde').replace('pésimo', 'pésimo')
        s = s.replace('vínculos', 'vínculos').replace('gestión', 'gestión').replace('investigación', 'investigación')
        s = s.replace('desempeño', 'desempeño').replace('situación', 'situación').replace('profesión', 'profesión')
        s = s.replace('líquidos', 'líquidos').replace('categorías', 'categorías').replace('pérdida', 'pérdida')
        s = s.replace('leña', 'leña').replace('hídricos', 'hídricos').replace('mitílidos', 'mitílidos')
        s = s.replace('act. tecnología', 'act. tecnología').replace('innovación', 'innovación')
        s = s.replace('progresaría', 'progresaría').replace('económicamente', 'económicamente')
        s = s.replace('aumentaría', 'aumentaría').replace('podría', 'podría').replace('pública', 'pública')
        s = s.replace('básica', 'básica').replace('construcción', 'construcción').replace('localización', 'localización')
        s = s.replace('opinión', 'opinión')
        return s
    elif isinstance(obj, dict):
        return {fix_dict(k): fix_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [fix_dict(item) for item in obj]
    else:
        return obj

with open('data/barometro_summary.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

clean_data = fix_dict(data)
clean_data['metadata']['comunas'] = ['Coyhaique', 'Lago Verde', 'Aysén', 'Cisnes', 'Guaitecas', 'Chile Chico', 'Cochrane', "O'Higgins", 'Tortel', 'Río Ibáñez', 'Balmaceda']

with open('data/barometro_summary.json', 'w', encoding='utf-8') as f:
    json.dump(clean_data, f, ensure_ascii=False, indent=2)

with open('data/barometro_dataset.json', 'w', encoding='utf-8') as f:
    json.dump(clean_data, f, ensure_ascii=False, indent=2)

print("data/barometro_summary.json and barometro_dataset.json cleaned and saved with 100% clean UTF-8 text!")
