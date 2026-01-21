# Salus Enhanced - Home Assistant Integration

O integrare îmbunătățită pentru Home Assistant care suportă **IT600 și IT500** - multiple modele Salus și entități extinse.

## 🚀 Caracteristici

- **Suport pentru IT600 și IT500**: Control local (IT600) și cloud (IT500)
- **Suport extins pentru dispozitive**: Termostați, senzori, întrerupătoare, jaluzele și senzori binari
- **Modele multiple Salus**: 
  - IT600: HTRP-RF, TS600, VS10/VS20, SQ610, FC600 + multe altele
  - IT500: IT500, RT310i, RT310, RT510, RT520, XT500
- **Entități bogate**: Temperatură, umiditate, baterie, stare încălzire, poziție valvă
- **Configurare prin UI**: Config flow complet cu selecție tip gateway
- **Actualizări coordonate**: Folosește DataUpdateCoordinator pentru eficiență
- **Modular și extensibil**: Cod structurat pentru adăugarea ușoară de noi dispozitive

## 📦 Instalare

### HACS (Recomandat)

1. Deschide HACS în Home Assistant
2. Mergi la "Integrations"
3. Click pe "..." (top-right) și selectează "Custom repositories"
4. Adaugă URL-ul acestui repo și selectează categoria "Integration"
5. Click "Install"
6. Restart Home Assistant

### Manual

1. Copiază folderul `custom_components/salus_enhanced` în `/config/custom_components/`
2. Restart Home Assistant

## ⚙️ Configurare

### IT600 (Gateway Local - UGE600)

1. Mergi la **Settings** → **Devices & Services**
2. Click pe **"+ Add Integration"**
3. Caută **"Salus Enhanced"**
4. Selectează **"IT600 (Local Gateway - UGE600)"**
5. Introdu:
   - **Host**: IP-ul local al gateway-ului (ex: `192.168.1.100`)
   - **EUID**: EUID-ul gateway-ului (scris pe fundația acestuia, ex: `001E5E0D32906128`)
     - Dacă nu funcționează, încearcă `0000000000000000`

**Note IT600:**
- Verifică că "Local WiFi Mode" este activat în aplicația Salus
- Gateway-ul trebuie să fie în aceeași rețea cu Home Assistant

### IT500 (Cloud - salus-it500.com)

1. Mergi la **Settings** → **Devices & Services**
2. Click pe **"+ Add Integration"**
3. Caută **"Salus Enhanced"**
4. Selectează **"IT500 (Cloud - salus-it500.com)"**
5. Introdu:
   - **Email**: Email-ul tău de la salus-it500.com
   - **Password**: Parola ta
   - **Device ID**: ID-ul dispozitivului

**Cum găsești Device ID pentru IT500:**
1. Deschide browser și mergi la https://salus-it500.com
2. Login cu email și parola din aplicația mobilă
3. Click pe dispozitivul tău
4. În URL vei vedea: `https://salus-it500.com/public/control.php?devId=34508332`
5. Copiază numărul după `devId=` (ex: `34508332`)

## 🔧 Dispozitive Suportate

### IT600 - Termostați (Climate)
- HTRP-RF / HTRP-RF50
- TS600
- VS10WRF / VS10BRF
- VS20WRF / VS20BRF
- SQ610 / SQ610RF
- FC600

### IT600 - Senzori Binari
- SW600 (Senzor fereastră)
- WLS600 (Senzor scurgere apă)
- OS600 (Senzor ocupare)
- SD600 (Detector fum)
- MS600 (Senzor mișcare)
- TRV10RFM (Cap termostatic)
- RX10RF (Receptor)

### IT600 - Senzori
- PS600 (Senzor temperatură)
- Baterie (pentru toate dispozitivele compatibile)
- Umiditate (de la termostate compatibile)

### IT600 - Întrerupătoare
- SPE600
- RS600
- SR600
- SP600

### IT600 - Jaluzele (Cover)
- RS600 (Controller rolete)

### IT500 - Termostați
- IT500
- RT310i
- RT310
- RT510
- RT520
- XT500

## 📊 Entități Create

Pentru fiecare dispozitiv, integrarea creează:

### Climate (Termostați)
- Entitate principală cu control temperatură
- Atribute: baterie, umiditate, fereastră deschisă (IT600)
- Moduri HVAC: Heat, Auto, Off
- Preset modes: home, away, sleep, manual

### Sensor
- Temperatură curentă
- Nivel baterie (dacă disponibil)
- Umiditate (dacă disponibil)

### Binary Sensor (IT600)
- Stare (deschis/închis, detectare mișcare, etc.)
- Atribute: nivel baterie

### Switch (IT600)
- Control on/off
- Atribute: putere, energie consumată (dacă disponibil)

### Cover (IT600)
- Control deschidere/închidere
- Setare poziție
- Control stop

## 🆚 Diferențe IT600 vs IT500

| Caracteristică | IT600 | IT500 |
|----------------|-------|-------|
| **Control** | Local (LAN) | Cloud (Internet) |
| **Gateway** | UGE600 | iTG500/iTG310 |
| **Latență** | Foarte mică | Depinde de internet |
| **Funcționare offline** | Da | Nu |
| **Dispozitive suportate** | Multiple tipuri | Doar termostate |
| **Configurare** | IP + EUID | Email + Password + Device ID |

## 🛠️ Configurare Avansată

### Interval Actualizare

Poți modifica intervalul de actualizare în `const.py`:

```python
SCAN_INTERVAL = 30  # secunde
```

### Adăugare Modele Noi

Pentru a adăuga suport pentru un model nou, editează `IT600_DEVICE_MODELS` sau `IT500_DEVICE_MODELS` în `const.py`:

```python
IT600_DEVICE_MODELS = {
    "climate": {
        "MODEL_NOU": {"name": "Nume Afișat"},
        # ...
    }
}
```

## 🐛 Troubleshooting

### IT600 - Gateway-ul nu se conectează
- Verifică că "Local WiFi Mode" este activat în aplicația Salus
- Restart gateway (scoate/bagă USB)
- Încearcă EUID `0000000000000000` dacă cel real nu funcționează
- Verifică că gateway-ul este în aceeași rețea cu HA

### IT500 - Nu se poate conecta
- Verifică email și parola (aceleași ca în app)
- Verifică că Device ID este corect
- Asigură-te că ai conexiune la internet
- Unele cont-uri pot fi blocate temporar după login-uri eșuate (așteaptă 30 min)

### Dispozitivele nu apar
- Verifică logs în Home Assistant
- Asigură-te că dispozitivele sunt configurate în aplicația Salus
- Restart integrarea

### Erori după actualizare HA
- Verifică că ai ultima versiune a integrării
- Șterge și re-adaugă integrarea dacă persistă problemele

## 📝 Log-uri

Pentru debugging, activează log-uri detaliate în `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.salus_enhanced: debug
    pyit600: debug
    pyit500: debug
```

## 🤝 Contribuții

Contribuțiile sunt binevenite! Pentru a adăuga suport pentru un dispozitiv nou:

1. Fork repository-ul
2. Adaugă modelul în `const.py`
3. Testează funcționalitatea
4. Creează un Pull Request

## 📄 Licență

MIT License - vezi fișierul LICENSE pentru detalii

## 🙏 Credite

Bazat pe:
- [homeassistant_salus](https://github.com/epoplavskis/homeassistant_salus) de epoplavskis - pentru IT600
- [pyit600](https://github.com/epoplavskis/pyit600) library
- [home-assistant-salus-it500](https://github.com/RichyA/home-assistant-salus-it500) - pentru IT500
- [pyit500](https://github.com/RichyA/pyit500) library

## 📞 Suport

Pentru probleme sau întrebări:
- Deschide un [Issue pe GitHub](https://github.com/yourusername/salus_enhanced/issues)
- Consultă [Home Assistant Community](https://community.home-assistant.io/)

## 🚀 Caracteristici

- **Suport extins pentru dispozitive**: Termostați, senzori, întrerupătoare, jaluzele și senzori binari
- **Modele multiple Salus**: HTRP-RF, TS600, VS10/VS20, SQ610, FC600 și multe altele
- **Entități bogate**: Temperatură, umiditate, baterie, stare încălzire, poziție valvă
- **Configurare prin UI**: Config flow complet pentru setup ușor
- **Actualizări coordonate**: Folosește DataUpdateCoordinator pentru eficiență
- **Modular și extensibil**: Cod structurat pentru adăugarea ușoară de noi dispozitive

## 📦 Instalare

### HACS (Recomandat)

1. Deschide HACS în Home Assistant
2. Mergi la "Integrations"
3. Click pe "..." (top-right) și selectează "Custom repositories"
4. Adaugă URL-ul acestui repo și selectează categoria "Integration"
5. Click "Install"
6. Restart Home Assistant

### Manual

1. Copiază folderul `custom_components/salus_enhanced` în `/config/custom_components/`
2. Restart Home Assistant

## ⚙️ Configurare

1. Mergi la **Settings** → **Devices & Services**
2. Click pe **"+ Add Integration"**
3. Caută **"Salus Enhanced"**
4. Introdu:
   - **Host**: IP-ul local al gateway-ului (ex: `192.168.1.100`)
   - **EUID**: EUID-ul gateway-ului (scris pe fundația acestuia, ex: `001E5E0D32906128`)
     - Dacă nu funcționează, încearcă `0000000000000000`

## 🔧 Dispozitive Suportate

### Termostați (Climate)
- HTRP-RF / HTRP-RF50
- TS600
- VS10WRF / VS10BRF
- VS20WRF / VS20BRF
- SQ610 / SQ610RF
- FC600

### Senzori Binari
- SW600 (Senzor fereastră)
- WLS600 (Senzor scurgere apă)
- OS600 (Senzor ocupare)
- SD600 (Detector fum)
- MS600 (Senzor mișcare)
- TRV10RFM (Cap termostatic)
- RX10RF (Receptor)

### Senzori
- PS600 (Senzor temperatură)
- Baterie (pentru toate dispozitivele compatibile)
- Umiditate (de la termostate compatibile)

### Întrerupătoare
- SPE600
- RS600
- SR600
- SP600

### Jaluzele (Cover)
- RS600 (Controller rolete)

## 📊 Entități Create

Pentru fiecare dispozitiv, integrarea creează:

### Climate (Termostați)
- Entitate principală cu control temperatură
- Atribute: baterie, umiditate, fereastră deschisă
- Moduri HVAC: Heat, Auto, Off
- Preset modes: home, away, sleep, manual

### Sensor
- Temperatură curentă
- Nivel baterie (dacă disponibil)
- Umiditate (dacă disponibil)

### Binary Sensor
- Stare (deschis/închis, detectare mișcare, etc.)
- Atribute: nivel baterie

### Switch
- Control on/off
- Atribute: putere, energie consumată (dacă disponibil)

### Cover
- Control deschidere/închidere
- Setare poziție
- Control stop

## 🛠️ Configurare Avansată

### Interval Actualizare

Poți modifica intervalul de actualizare în `const.py`:

```python
SCAN_INTERVAL = 30  # secunde
```

### Adăugare Modele Noi

Pentru a adăuga suport pentru un model nou, editează `DEVICE_MODELS` în `const.py`:

```python
DEVICE_MODELS = {
    "climate": {
        "MODEL_NOU": {"name": "Nume Afișat"},
        # ...
    }
}
```

## 🐛 Troubleshooting

### Gateway-ul nu se conectează
- Verifică că "Local WiFi Mode" este activat în aplicația Salus
- Restart gateway (scoate/bagă USB)
- Încearcă EUID `0000000000000000` dacă cel real nu funcționează

### Dispozitivele nu apar
- Verifică logs în Home Assistant
- Asigură-te că dispozitivele sunt configurate în aplicația Salus
- Restart integrarea

### Erori după actualizare HA
- Verifică că ai ultima versiune a integrării
- Șterge și re-adaugă integrarea dacă persistă problemele

## 📝 Log-uri

Pentru debugging, activează log-uri detaliate în `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.salus_enhanced: debug
    pyit600: debug
```

## 🤝 Contribuții

Contribuțiile sunt binevenite! Pentru a adăuga suport pentru un dispozitiv nou:

1. Fork repository-ul
2. Adaugă modelul în `const.py`
3. Testează funcționalitatea
4. Creează un Pull Request

## 📄 Licență

MIT License - vezi fișierul LICENSE pentru detalii

## 🙏 Credite

Bazat pe:
- [homeassistant_salus](https://github.com/epoplavskis/homeassistant_salus) de epoplavskis
- [pyit600](https://github.com/epoplavskis/pyit600) library

## 📞 Suport

Pentru probleme sau întrebări:
- Deschide un [Issue pe GitHub](https://github.com/yourusername/salus_enhanced/issues)
- Consultă [Home Assistant Community](https://community.home-assistant.io/)
