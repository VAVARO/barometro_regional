import json

with open(r"C:\AGY\BAROMETRO\scripts\computed_comparative_catalog.json", "r", encoding="utf-8") as f:
    cat = json.load(f)

for mod in cat:
    print(f"\n==========================================")
    print(f"{mod['module']} ({len(mod['charts'])} gráficos posibles)")
    print(f"==========================================")
    for ch in mod['charts']:
        status = "[EN APP]" if ch['in_app'] else "[NO INCLUIDO]"
        # check if all 7 regions have values
        regs_with_val = [k for k, v in ch['regional_values'].items() if v is not None]
        print(f"  * {status:<14} | {ch['title']}")
        print(f"    - Variable: {ch['col']} | Tipo: {ch['type']} | Regiones válidas ({len(regs_with_val)}/7): {', '.join(regs_with_val)}")
        if ch['type'] in ['target_pct', 'mean']:
            print(f"    - Valores: {ch['regional_values']}")
