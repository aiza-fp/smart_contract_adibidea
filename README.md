# Smart Contract baten hedapen eta erabilera adibidea

Proiektu honek Ethereum blockchain-ean formularioak kudeatzeko sistema bat eskaintzen du. Proiektuaren osagaiak: Solidity smart contract bat, Python script bat kontratua hedatzeko eta erabiltzeko, eta web interfaze bat trazabilitatea kontsultatzeko.

## Proiektuaren Deskribapena

Proiektu hau formularioen kudeaketa eta trazabilitatea blockchain-ean gordetzeko sistema bat da. Smart Contract baten bidez, formularioak sortu, eguneratu eta kontsultatu daitezke, eta guzti hori blockchain-ean erregistratzen da, trazabilitatea bermatuz.

## Fitxategien Azalpena

### `Formularioak.sol`
Solidity smart contract nagusia. Formularioak kudeatzeko funtzionalitateak eskaintzen ditu:
- **createForm()**: Formulario berri bat sortzen du `datu1` eta `datu2` datuekin
- **updateForm()**: Existitzen den formulario bat eguneratzen du
- **getForm()**: Formulario baten datuak kontsultatzen ditu
- **getFormCount()**: Sortu diren formulario kopurua itzultzen du

Kontratuak bi event emititzen ditu:
- `FormCreated`: Formulario berri bat sortzen denean
- `FormUpdated`: Formulario bat eguneratzen denean

### `hedatu_erabili.py`
Python script bat, Web3.py liburutegia erabiliz smart contract-a hedatzeko eta erabiltzeko. Script honek:
- Ethereum nodo batekin konektatzen da (IP zerrenda batetik)
- Kontratuaren bytecode eta ABI fitxategiak kargatzen ditu
- Kontratua blockchain-ean hedatzen du
- Formularioak sortzen eta eguneratzen ditu
- Formularioen datuak kontsultatzen ditu
- Blockchain-eko event-ak kontsultatzen ditu trazabilitatea erakusteko

### `trazabilitatea.html`
Web interfaze bat, formularioen historia kontsultatzeko. Interfaze honek:
- Ethereum nodo batekin konektatzen da
- Kontratuaren helbidea eta formulario zenbakia sartuz, formulario baten historia erakusten du
- `FormCreated` eta `FormUpdated` event-ak kontsultatzen ditu
- Event-ak taula batean erakusten ditu, bloke zenbakia, transakzio hash-a, datuak eta denbora-marka barne

### `Formularioak.abi` eta `Formularioak.bytecode`
Kontratuaren ABI (Application Binary Interface) eta bytecode fitxategiak. Hauek beharrezkoak dira kontratua hedatzeko eta erabiltzeko.

## Beharrezkoak

### Python Script-a erabiltzeko:
- Python 3.x
- `web3` liburutegia: `pip install web3`
- `eth-account` liburutegia: `pip install eth-account`
- Ethereum nodo bat konektagarri (adibidez, Blockchain FP Euskadi sareko nodo bat)

### Web interfazea erabiltzeko:
- Web nabigatzaile moderno bat
- Ethereum nodo bat konektagarri (adibidez, Besu nodo bat)
- Internet konexioa (ethers.js CDN-etik kargatzeko)

## Erabilera

### 1. Python Script-a exekutatu

```bash
python hedatu_erabili.py
```

Script-ak automatikoki:
1. Ethereum nodo batekin konektatuko da
2. Kontratua blockchain-ean hedatuko du
3. Formulario bat sortuko du
4. Formularioa eguneratuko du
5. Event-ak kontsultatuko ditu

### 2. Web interfazea erabili

1. `trazabilitatea.html` fitxategia nabigatzaile batean ireki
2. Kontratuaren helbidea sartu (Python script-ak terminalean erakutsiko du)
3. Formulario zenbakia sartu (adibidez, 1)
4. "Retrieve Events" botoia sakatu
5. Formularioaren historia taula batean erakutsiko da

## Konfigurazioa

### IP Zerrenda Aldatu

Emanda datorren IP helbidearekin Blockchain FP Euskadi sarean hedatuko da proiektua baina Python script-ean eta HTML fitxategian IP zerrenda alda dezakezu zure Ethereum nodoaren helbidea sartzeko edo nodo berriak gehitzeko:

**hedatu_erabili.py**:
```python
IP_LIST = [
    "85.190.243.52",  # Zure nodoaren IP helbidea
    # Gehiago gehitu ditzakezu
]
```

**trazabilitatea.html**:
```javascript
const IP_LIST = ["85.190.243.52"];  // Zure nodoaren IP helbidea
```

## Segurtasuna

- Kontratuak `onlyOwner` modifikadorea erabiltzen du, beraz soilik kontratuaren jabeak (hedatzailea) sortu eta eguneratu ditzake formularioak
- Kontratuaren jabea konstruktorean zehazten da (`msg.sender`)
- Formularioak kontsultatzeko (`getForm()`) ez da beharrezkoa jabea izatea

## Teknologia Stack-a

- **Solidity**: Smart contract-ak garatzeko lengoaia
- **Python**: Backend script-ak garatzeko
- **Web3.py**: Python-etik Ethereum-rekin komunikatzeko
- **JavaScript/HTML**: Web interfazea garatzeko
- **ethers.js**: JavaScript-etik Ethereum-rekin komunikatzeko

## Oharrak

- Proiektu hau Besu sare pribatu batekin (Blockchain FP Euskadi) probatua izan da, zero-gas konfigurazioarekin. Sarea pribatua da nodoen parte hartzearen aldetik baina publikoa erabilera aldetik.
- Kontratua Solidity 0.8.19 bertsioarekin konpilatu da
- EVM London bertsioa erabili da konpilazioan
- Aurreko puntuak kontutan izanda, kontratu berriak sortu eta konpilatzeko erreminta erraz bat [Remix](https://remix.ethereum.org) izan daiteke
## Lizentzia

MIT Lizentzia

